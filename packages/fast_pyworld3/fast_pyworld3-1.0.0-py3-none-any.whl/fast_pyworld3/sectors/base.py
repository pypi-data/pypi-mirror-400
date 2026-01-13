"""Base class for World3 model sectors"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, Literal
import json

import numpy as np
import numpy.typing as npt


@dataclass
class SectorConfig:
    """Configuration for a model sector"""

    year_min: float = 1900.0
    year_max: float = 2100.0
    dt: float = 0.5
    verbose: bool = False


class FastTableFunction:
    """
    Fast table lookup function using numpy.interp.

    This replaces scipy.interpolate.interp1d for significant performance gains.
    numpy.interp is ~10-20x faster for single value lookups.
    Includes simple caching for consecutive identical lookups.
    """

    __slots__ = ('_xp', '_fp', '_left', '_right', '_cache_x', '_cache_y')

    def __init__(
        self,
        x_values: list[float],
        y_values: list[float],
    ):
        """
        Initialize fast table function.

        Args:
            x_values: X coordinates (must be increasing)
            y_values: Y coordinates
        """
        self._xp = np.asarray(x_values, dtype=np.float64)
        self._fp = np.asarray(y_values, dtype=np.float64)
        self._left = y_values[0]
        self._right = y_values[-1]
        self._cache_x = None
        self._cache_y = None

    def __call__(self, x: float) -> float:
        """
        Interpolate value at x.

        Args:
            x: X coordinate to interpolate at

        Returns:
            Interpolated y value
        """
        # Check cache for consecutive identical lookups
        if self._cache_x == x:
            return self._cache_y

        # Compute and cache result
        result = np.interp(x, self._xp, self._fp, left=self._left, right=self._right)
        self._cache_x = x
        self._cache_y = result
        return result


class BaseSector(ABC):
    """
    Base class for all World3 model sectors.

    Provides common functionality for time management, variable initialization,
    and table function loading.
    """

    def __init__(self, config: SectorConfig):
        self.year_min = config.year_min
        self.year_max = config.year_max
        self.dt = config.dt
        self.verbose = config.verbose

        # Derived time properties
        self.length = self.year_max - self.year_min
        self.n = int(self.length / self.dt) + 1
        self.time = np.arange(self.year_min, self.year_max + self.dt, self.dt)

        # Flag for loop rescheduling
        self.redo_loop = False

    def _create_array(self) -> npt.NDArray[np.float64]:
        """Create a NaN-filled array for storing variables"""
        return np.full(self.n, np.nan)

    def _load_table_functions(
        self, func_names: list[str], json_file: Path | None = None
    ) -> dict[str, Callable[[float], float]]:
        """
        Load table functions from JSON file.

        Args:
            func_names: List of function names to load
            json_file: Path to JSON file (defaults to packaged data file)

        Returns:
            Dictionary mapping function names to FastTableFunction instances
        """
        if json_file is None:
            # Use packaged data file
            json_file = Path(__file__).parent.parent / "data" / "functions_table_world3.json"

        with open(json_file) as f:
            tables = json.load(f)

        functions: dict[str, Callable[[float], float]] = {}

        for func_name in func_names:
            for table in tables:
                if table["y.name"] == func_name:
                    func = FastTableFunction(
                        table["x.values"],
                        table["y.values"],
                    )
                    functions[func_name.lower()] = func
                    break

        return functions

    @abstractmethod
    def init_constants(self, **kwargs: Any) -> None:
        """Initialize sector constants"""
        pass

    @abstractmethod
    def init_variables(self) -> None:
        """Initialize sector variables (state and rate variables)"""
        pass

    @abstractmethod
    def set_table_functions(self, json_file: Path | None = None) -> None:
        """Set nonlinear table functions from JSON file"""
        pass

    @abstractmethod
    def set_delay_functions(self, method: Literal["euler", "odeint"] = "euler") -> None:
        """Set delay and smoothing functions"""
        pass
