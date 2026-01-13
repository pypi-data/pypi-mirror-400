"""Basic utility functions for World3 model"""

from typing import Union
import numpy as np
import numpy.typing as npt

NumericType = Union[float, npt.NDArray[np.float64]]


def clip(func2: NumericType, func1: NumericType, t: float, t_switch: float) -> NumericType:
    """
    Time switch function to change parameter value.

    Returns func1 if t <= t_switch, else func2.
    Commonly used to switch between policy scenarios at a specific time.

    Args:
        func2: Value to return after t_switch
        func1: Value to return before or at t_switch
        t: Current time value
        t_switch: Time threshold for switching

    Returns:
        func2 if t > t_switch, else func1

    Examples:
        >>> clip(2.0, 1.0, 1950, 1975)  # Before switch time
        1.0
        >>> clip(2.0, 1.0, 2000, 1975)  # After switch time
        2.0
    """
    # Fast path for scalar values (most common case)
    if t <= t_switch:
        return func1
    return func2


def switch(var1: NumericType, var2: NumericType, boolean_switch: bool) -> NumericType:
    """
    Logical function returning var1 if boolean_switch is False, else var2.

    Args:
        var1: Value to return when switch is False
        var2: Value to return when switch is True
        boolean_switch: Boolean condition

    Returns:
        var1 or var2 depending on boolean_switch
    """
    if np.isnan(var1).any() or np.isnan(var2).any():  # type: ignore
        return np.nan  # type: ignore
    return var2 if boolean_switch else var1


def ramp(slope: float, t_offset: float, t: float) -> float:
    """
    Affine function with provided slope, clipped at 0 for t < t_offset.

    Args:
        slope: Ramp slope
        t_offset: Time when ramp begins
        t: Current time value

    Returns:
        slope * (t - t_offset) if t >= t_offset, else 0

    Examples:
        >>> ramp(2.0, 1900, 1950)
        100.0
        >>> ramp(2.0, 1900, 1850)
        0
    """
    return 0.0 if t < t_offset else slope * (t - t_offset)
