"""Resource sector of the World3 model (2004 update)

The resource sector models nonrenewable resource depletion, usage patterns,
capital allocation for resource extraction, and resource technology development.
This sector was updated in 2004 to include resource technology changes.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from fast_pyworld3.sectors.base import BaseSector, SectorConfig
from fast_pyworld3.utils import Dlinf3, clip


@dataclass
class ResourceConstants:
    """Constants for the resource sector"""

    nri: float = 1e12  # Nonrenewable resources initial [resource units]
    nruf1: float = 1.0  # NR usage factor (before policy)
    drur: float = 4.8e9  # Desired resource utilization rate
    tdt: float = 20.0  # Technology development time [years]


class Resource(BaseSector):
    """
    Nonrenewable resource sector (2004 update - added resource technology)

    Models nonrenewable resource depletion, usage patterns, capital allocation
    for resource extraction, and resource technology development.
    """

    def __init__(self, config: SectorConfig):
        super().__init__(config)
        self.constants = ResourceConstants()
        self._table_funcs: dict = {}

        # Policy implementation years (set by World3 model)
        self.pyear: float = 1975.0  # Policy implementation year
        self.pyear_res_tech: float = 4000.0  # Resource tech policy year
        self.pyear_fcaor: float = 4000.0  # FCAOR policy year

    def init_constants(self, **kwargs: float) -> None:
        """Initialize resource constants"""
        self.constants = ResourceConstants(**kwargs)

    def init_variables(self) -> None:
        """Initialize resource variables"""
        # State variables
        self.nr = self._create_array()  # Nonrenewable resources [resource units]
        self.rt = self._create_array()  # Resource technology

        # Resource availability
        self.nrfr = self._create_array()  # NR fraction remaining
        self.fcaor = self._create_array()  # Fraction capital to resource obtaining
        self.fcaor1 = self._create_array()  # FCAOR before policy
        self.fcaor2 = self._create_array()  # FCAOR after policy

        # Resource usage
        self.nruf = self._create_array()  # NR usage factor
        self.nruf2 = self._create_array()  # NR usage factor 2
        self.nrur = self._create_array()  # NR usage rate [resource units/year]
        self.pcrum = self._create_array()  # Per capita resource use multiplier

        # Resource technology (2004 update)
        self.rtc = self._create_array()  # RT change
        self.rtcm = self._create_array()  # RT change multiplier
        self.rtcr = self._create_array()  # RT change rate

        # Exogenous inputs from other sectors
        # (These will be properly set by World3 during simulation)
        self.pop = self._create_array()  # Population [persons]
        self.iopc = self._create_array()  # IO per capita [$/person/year]

    def set_table_functions(self, json_file: Path | None = None) -> None:
        """Load table functions"""
        func_names = ["PCRUM", "FCAOR1", "FCAOR2", "RTCM"]
        self._table_funcs = self._load_table_functions(func_names, json_file)

    def set_delay_functions(self, method: Literal["euler", "odeint"] = "euler") -> None:
        """Initialize delay functions"""
        self.dlinf3_rt = Dlinf3(self.rt, self.dt, self.time, method=method)

    # ========================================================================
    # STATE UPDATE METHODS
    # ========================================================================

    def update_state_nr(self, k: int, j: int, jk: int) -> None:
        """
        Update nonrenewable resources state variable.
        From step j requires: NRUR
        """
        self.nr[k] = self.nr[j] - self.dt * self.nrur[jk]

    def update_state_rt(self, k: int, j: int, jk: int) -> None:
        """
        Update resource technology state variable.
        From step j requires: RTCR
        """
        self.rt[k] = self.rt[j] + self.dt * self.rtcr[jk]

    # ========================================================================
    # RESOURCE AVAILABILITY
    # ========================================================================

    def update_nrfr(self, k: int) -> None:
        """
        Update nonrenewable resource fraction remaining.
        From step k requires: NR
        """
        self.nrfr[k] = self.nr[k] / self.constants.nri

    def update_fcaor1(self, k: int) -> None:
        """
        Update fraction capital allocated to obtaining resources (before policy).
        From step k requires: NRFR
        """
        self.fcaor1[k] = self._table_funcs["fcaor1"](self.nrfr[k])

    def update_fcaor2(self, k: int) -> None:
        """
        Update fraction capital allocated to obtaining resources (after policy).
        From step k requires: NRFR
        """
        self.fcaor2[k] = self._table_funcs["fcaor2"](self.nrfr[k])

    def update_fcaor(self, k: int) -> None:
        """
        Update fraction capital allocated to obtaining resources.
        From step k requires: FCAOR1, FCAOR2
        """
        self.fcaor[k] = clip(
            self.fcaor2[k],
            self.fcaor1[k],
            self.time[k],
            self.pyear_fcaor,
        )

    # ========================================================================
    # RESOURCE TECHNOLOGY (2004 UPDATE)
    # ========================================================================

    def update_rtc(self, k: int) -> None:
        """
        Update resource technology change.
        From step k requires: NRUR
        """
        self.rtc[k] = 1 - self.nrur[k] / self.constants.drur

    def update_rtcm(self, k: int) -> None:
        """
        Update resource technology change multiplier.
        From step k requires: RTC
        """
        self.rtcm[k] = self._table_funcs["rtcm"](self.rtc[k])

    def update_rtcr(self, k: int, j: int) -> None:
        """
        Update resource technology change rate.
        From step k requires: RTCM, RT
        """
        if self.time[k] > self.pyear_res_tech:
            self.rtcr[k] = self.rtcm[k] * self.rt[j]
        else:
            self.rtcr[k] = 0.0

    def update_nruf2(self, k: int) -> None:
        """
        Update nonrenewable resource usage factor 2 (smoothed).
        From step k requires: RT
        """
        self.nruf2[k] = self.dlinf3_rt(k, self.constants.tdt)

    def update_nruf(self, k: int) -> None:
        """
        Update nonrenewable resource usage factor.
        From step k requires: NRUF2
        """
        self.nruf[k] = clip(
            self.nruf2[k],
            self.constants.nruf1,
            self.time[k],
            self.pyear_res_tech,
        )

    # ========================================================================
    # RESOURCE USAGE
    # ========================================================================

    def update_pcrum(self, k: int) -> None:
        """
        Update per capita resource usage multiplier.
        From step k requires: IOPC
        """
        self.pcrum[k] = self._table_funcs["pcrum"](self.iopc[k])

    def update_nrur(self, k: int, kl: int) -> None:
        """
        Update nonrenewable resource usage rate.
        From step k requires: POP, PCRUM, NRUF
        """
        self.nrur[kl] = self.pop[k] * self.pcrum[k] * self.nruf[k]
