"""Pollution sector of the World3 model (2004 update)

The pollution sector models persistent pollution generation, absorption, and
impacts on agricultural yield and ecological footprint. This sector was
completely rebuilt for the 2004 update.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import numpy as np
import numpy.typing as npt

from fast_pyworld3.sectors.base import BaseSector, SectorConfig
from fast_pyworld3.utils import clip, Dlinf3


@dataclass
class PollutionConstants:
    """Constants for the pollution sector"""

    pp19: float = 2.5e7  # Persistent pollution in 1900
    apct: float = 4000.0  # Air pollution change time [year]
    io70: float = 7.9e11  # Industrial output in 1970 [$/year]
    imef: float = 0.1  # Industrial material emission factor
    imti: float = 10.0  # Industrial material toxicity index
    frpm: float = 0.02  # Fraction res pers mtl
    ghup: float = 4e-9  # GHA per unit of pollution
    faipm: float = 0.001  # Fraction agri input pers mtl
    amti: float = 1.0  # Agricultural material toxicity index
    pptd: float = 20.0  # Persistent pollution transmission delay [years]
    ahl70: float = 1.5  # Assimilation half-life 1970
    pp70: float = 1.36e8  # Persistent pollution in 1970
    dppolx: float = 1.2  # Desired persistent pollution index
    tdt: float = 20.0  # Technology development time [years]
    ppgf1: float = 1.0  # Persistent pollution generation factor 1


class Pollution(BaseSector):
    """
    Persistent pollution sector (2004 update - completely rebuilt)

    Models pollution generation from industry and agriculture, pollution
    absorption, impacts on agricultural yields, and ecological footprint.
    """

    def __init__(self, config: SectorConfig):
        super().__init__(config)
        self.constants = PollutionConstants()
        self._table_funcs: dict = {}

        # Policy implementation years (set by World3 model)
        self.pyear: float = 1975.0  # Policy implementation year
        self.pyear_pp_tech: float = 4000.0  # Pollution tech policy year

    def init_constants(self, **kwargs: float) -> None:
        """Initialize pollution constants"""
        self.constants = PollutionConstants(**kwargs)

    def init_variables(self) -> None:
        """Initialize pollution variables"""
        # State variables
        self.pp = self._create_array()  # Persistent pollution
        self.ppt = self._create_array()  # PP technology

        # Pollution generation
        self.ppgi = self._create_array()  # PP gen industry
        self.ppga = self._create_array()  # PP gen agriculture
        self.ppgr = self._create_array()  # PP generation rate
        self.ppgf = self._create_array()  # PP gen factor
        self.ppgf2 = self._create_array()  # PP gen factor 2
        self.ppar = self._create_array()  # PP appear rate

        # Pollution absorption
        self.ppolx = self._create_array()  # PP index
        self.ppasr = self._create_array()  # PP assimilation rate
        self.ahl = self._create_array()  # Assimilation half-life
        self.ahlm = self._create_array()  # AHL multiplier

        # Pollution technology
        self.pptc = self._create_array()  # PP tech change
        self.pptcm = self._create_array()  # PP tech change multiplier
        self.pptcr = self._create_array()  # PP tech change rate
        self.pptmi = self._create_array()  # PP tech mult ICOR COPM

        # Pollution impact on agriculture
        self.pii = self._create_array()  # Pollution intensity index
        self.fio70 = self._create_array()  # Fraction IO over 1970
        self.ymap1 = self._create_array()  # Yield mult air poll 1
        self.ymap2 = self._create_array()  # Yield mult air poll 2
        self.apfay = self._create_array()  # Air pollution factor agr yield

        # Ecological footprint
        self.abl = self._create_array()  # Absorption land [GHA]
        self.ef = self._create_array()  # Ecological footprint

        # Exogenous inputs from other sectors
        # (These will be properly set by World3 during simulation)
        self.pop = self._create_array()  # Population [persons]
        self.io = self._create_array()  # Industrial output [$/year]
        self.iopc = self._create_array()  # IO per capita [$/person/year]
        self.aiph = self._create_array()  # Agr inputs per hectare [$/ha/year]
        self.al = self._create_array()  # Arable land [hectares]
        self.uil = self._create_array()  # Urban-industrial land [hectares]
        self.pcrum = self._create_array()  # Per capita resource use mult

    def set_table_functions(self, json_file: Path | None = None) -> None:
        """Load table functions"""
        func_names = ["PCRUM", "AHLM", "PPTCM", "PPTMI", "YMAP1", "YMAP2"]
        self._table_funcs = self._load_table_functions(func_names, json_file)

    def set_delay_functions(self, method: Literal["euler", "odeint"] = "euler") -> None:
        """Initialize delay functions"""
        self.dlinf3_ppgr = Dlinf3(self.ppgr, self.dt, self.time, method=method)
        self.dlinf3_ppt = Dlinf3(self.ppt, self.dt, self.time, method=method)

    # ========================================================================
    # STATE UPDATE METHODS
    # ========================================================================

    def update_state_pp(self, k: int, j: int, jk: int) -> None:
        """
        Update persistent pollution state variable.
        From step j requires: PPAR, PPASR
        """
        self.pp[k] = self.pp[j] + self.dt * (self.ppar[jk] - self.ppasr[jk])

    def update_state_ppt(self, k: int, j: int, jk: int) -> None:
        """
        Update persistent pollution technology state variable.
        From step j requires: PPTCR
        """
        self.ppt[k] = self.ppt[j] + self.dt * self.pptcr[jk]

    # ========================================================================
    # POLLUTION GENERATION - INDUSTRY
    # ========================================================================

    def update_pcrum(self, k: int) -> None:
        """
        Update per capita resource use multiplier.
        From step k requires: IOPC
        """
        self.pcrum[k] = self._table_funcs["pcrum"](self.iopc[k])

    def update_ppgi(self, k: int) -> None:
        """
        Update persistent pollution generation from industry.
        From step k requires: PCRUM, POP
        """
        self.ppgi[k] = (
            self.pcrum[k]
            * self.pop[k]
            * self.constants.frpm
            * self.constants.imef
            * self.constants.imti
        )

    # ========================================================================
    # POLLUTION GENERATION - AGRICULTURE
    # ========================================================================

    def update_ppga(self, k: int) -> None:
        """
        Update persistent pollution generation from agriculture.
        From step k requires: AIPH, AL
        """
        self.ppga[k] = (
            self.aiph[k]
            * self.al[k]
            * self.constants.faipm
            * self.constants.amti
        )

    # ========================================================================
    # POLLUTION GENERATION - TOTAL
    # ========================================================================

    def update_ppgf(self, k: int) -> None:
        """
        Update persistent pollution generation factor.
        From step k requires: PPGF2
        """
        self.ppgf[k] = clip(
            self.ppgf2[k],
            self.constants.ppgf1,
            self.time[k],
            self.pyear_pp_tech,
        )

    def update_ppgr(self, k: int) -> None:
        """
        Update persistent pollution generation rate.
        From step k requires: PPGI, PPGA, PPGF
        """
        self.ppgr[k] = (self.ppgi[k] + self.ppga[k]) * self.ppgf[k]

    def update_ppar(self, k: int) -> None:
        """
        Update persistent pollution appearance rate.
        From step k requires: PPGR
        """
        self.ppar[k] = self.dlinf3_ppgr(k, self.constants.pptd)

    # ========================================================================
    # POLLUTION ABSORPTION
    # ========================================================================

    def update_ppolx(self, k: int) -> None:
        """
        Update persistent pollution index.
        From step k requires: PP
        """
        self.ppolx[k] = self.pp[k] / self.constants.pp70

    def update_ahlm(self, k: int) -> None:
        """
        Update assimilation half-life multiplier.
        From step k requires: PPOLX
        """
        self.ahlm[k] = self._table_funcs["ahlm"](self.ppolx[k])

    def update_ahl(self, k: int) -> None:
        """
        Update assimilation half-life.
        From step k requires: AHLM
        """
        self.ahl[k] = self.constants.ahl70 * self.ahlm[k]

    def update_ppasr(self, k: int) -> None:
        """
        Update persistent pollution assimilation rate.
        From step k requires: PP, AHL
        """
        self.ppasr[k] = self.pp[k] / (1.4 * self.ahl[k])

    # ========================================================================
    # POLLUTION TECHNOLOGY
    # ========================================================================

    def update_pptc(self, k: int) -> None:
        """
        Update persistent pollution technology change.
        From step k requires: PPOLX
        """
        self.pptc[k] = 1 - (self.ppolx[k] / self.constants.dppolx)

    def update_pptcm(self, k: int) -> None:
        """
        Update persistent pollution technology change multiplier.
        From step k requires: PPTC
        """
        self.pptcm[k] = self._table_funcs["pptcm"](self.pptc[k])

    def update_pptcr(self, k: int, j: int) -> None:
        """
        Update persistent pollution technology change rate.
        From step k requires: PPTCM, PPT
        """
        if self.time[k] >= self.pyear_pp_tech:
            self.pptcr[k] = self.pptcm[j] * self.ppt[j]
        else:
            self.pptcr[k] = 0

    def update_ppgf2(self, k: int) -> None:
        """
        Update persistent pollution generation factor 2.
        From step k requires: PPT
        """
        self.ppgf2[k] = self.dlinf3_ppt(k, self.constants.tdt)

    def update_pptmi(self, k: int) -> None:
        """
        Update persistent pollution technology multiplier ICOR COPM.
        From step k requires: PPGF
        """
        self.pptmi[k] = self._table_funcs["pptmi"](self.ppgf[k])

    # ========================================================================
    # POLLUTION IMPACT ON AGRICULTURE
    # ========================================================================

    def update_pii(self, k: int) -> None:
        """
        Update pollution intensity index.
        From step k requires: PPGI, PPGF, IO
        """
        self.pii[k] = self.ppgi[k] * self.ppgf[k] / self.io[k]

    def update_fio70(self, k: int) -> None:
        """
        Update fraction of industrial output over 1970.
        From step k requires: IO
        """
        self.fio70[k] = self.io[k] / self.constants.io70

    def update_ymap1(self, k: int) -> None:
        """
        Update yield multiplier from air pollution 1.
        From step k requires: FIO70
        """
        self.ymap1[k] = self._table_funcs["ymap1"](self.fio70[k])

    def update_ymap2(self, k: int) -> None:
        """
        Update yield multiplier from air pollution 2.
        From step k requires: FIO70
        """
        self.ymap2[k] = self._table_funcs["ymap2"](self.fio70[k])

    def update_apfay(self, k: int) -> None:
        """
        Update air pollution factor on agricultural yield.
        From step k requires: YMAP1, YMAP2
        """
        if self.time[k] > self.constants.apct:
            self.apfay[k] = self.ymap2[k]
        else:
            self.apfay[k] = self.ymap1[k]

    # ========================================================================
    # ECOLOGICAL FOOTPRINT
    # ========================================================================

    def update_abl(self, k: int) -> None:
        """
        Update absorption land in GHA.
        From step k requires: PPGR
        """
        self.abl[k] = self.ppgr[k] * self.constants.ghup

    def update_ef(self, k: int) -> None:
        """
        Update ecological footprint.
        From step k requires: AL, UIL, ABL
        """
        self.ef[k] = (self.al[k] / 1e9 + self.uil[k] / 1e9 + self.abl[k]) / 1.91


class Resource(BaseSector):
    """Nonrenewable resource sector (2004 update)"""

    # Similar structure to above sectors...
    pass
