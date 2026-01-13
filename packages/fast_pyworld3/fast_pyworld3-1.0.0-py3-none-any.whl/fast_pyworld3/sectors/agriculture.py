"""Agriculture sector of the World3 model

Models food production through land development, agricultural inputs,
land erosion, urban expansion, and soil fertility dynamics.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import numpy as np
import numpy.typing as npt

from fast_pyworld3.sectors.base import BaseSector, SectorConfig
from fast_pyworld3.utils import clip, Smooth, Dlinf3


@dataclass
class AgricultureConstants:
    """Constants for the agriculture sector"""

    ali: float = 0.9e9  # Arable land initial [hectares]
    pali: float = 2.3e9  # Potentially arable land initial [hectares]
    lfh: float = 0.7  # Land fraction harvested
    palt: float = 3.2e9  # Potentially arable land total [hectares]
    pl: float = 0.1  # Processing loss
    alai1: float = 2.0  # Average lifetime agricultural inputs (before)
    alai2: float = 2.0  # Average lifetime agricultural inputs (after)
    io70: float = 7.9e11  # Industrial output in 1970 [$/year]
    lyf1: float = 1.0  # Land yield factor (before)
    sd: float = 0.07  # Social discount [1/year]
    uili: float = 8.2e6  # Urban-industrial land initial [hectares]
    alln: float = 1000.0  # Average life of land normal [years]
    uildt: float = 10.0  # Urban-industrial land development time [years]
    lferti: float = 600.0  # Land fertility initial [kg/hectare/year]
    ilf: float = 600.0  # Inherent land fertility [kg/hectare/year]
    fspd: float = 2.0  # Food shortage perception delay [years]
    sfpc: float = 230.0  # Subsistence food per capita [kg/person/year]
    dfr: float = 2.0  # Desired food ratio (2004 update)
    tdt: float = 20.0  # Technology development time [years] (2004)


class Agriculture(BaseSector):
    """
    Agriculture sector with loops for land development, inputs,
    erosion, and fertility.
    """

    def __init__(self, config: SectorConfig):
        super().__init__(config)
        self.constants = AgricultureConstants()
        self._table_funcs: dict = {}

        # Policy implementation years (set by World3 model)
        self.pyear: float = 1975.0  # Policy implementation year
        self.pyear_y_tech: float = 4000.0  # Yield technology policy year

    def init_constants(self, **kwargs: float) -> None:
        """Initialize agriculture constants"""
        self.constants = AgricultureConstants(**kwargs)

    def init_variables(self) -> None:
        """Initialize agriculture variables"""
        # State variables
        self.al = self._create_array()  # Arable land [hectares]
        self.pal = self._create_array()  # Potentially arable land [hectares]
        self.uil = self._create_array()  # Urban-industrial land [hectares]
        self.lfert = self._create_array()  # Land fertility [kg/ha/year]
        self.ai = self._create_array()  # Agricultural inputs [$/year]
        self.pfr = self._create_array()  # Perceived food ratio

        # Loop 1 - Food from investment in land development
        self.dcph = self._create_array()  # Development cost per hectare [$/ha]
        self.f = self._create_array()  # Food [kg/year]
        self.fpc = self._create_array()  # Food per capita [kg/person/year]
        self.fioaa = self._create_array()  # Fraction IO to agriculture
        self.fioaa1 = self._create_array()  # FIOAA before policy
        self.fioaa2 = self._create_array()  # FIOAA after policy
        self.ifpc = self._create_array()  # Indicated food per capita [kg/person/yr]
        self.ifpc1 = self._create_array()  # IFPC before policy
        self.ifpc2 = self._create_array()  # IFPC after policy
        self.ldr = self._create_array()  # Land development rate [ha/year]
        self.lfc = self._create_array()  # Land fraction cultivated
        self.tai = self._create_array()  # Total agricultural investment [$/yr]

        # Loop 2 - Food from investment in agricultural inputs
        self.aic = self._create_array()  # Agricultural inputs change [$/yr]
        self.aiph = self._create_array()  # Agricultural inputs per hectare [$/ha/yr]
        self.alai = self._create_array()  # Avg lifetime agricultural inputs [yrs]
        self.cai = self._create_array()  # Current agricultural inputs [$/yr]
        self.ly = self._create_array()  # Land yield [kg/ha/year]
        self.lyf = self._create_array()  # Land yield factor
        self.lymap = self._create_array()  # Land yield mult from air pollution
        self.lymap1 = self._create_array()  # LYMAP before policy
        self.lymap2 = self._create_array()  # LYMAP after policy
        self.lymc = self._create_array()  # Land yield mult from capital

        # Loop 1 & 2 - Investment allocation decision
        self.fiald = self._create_array()  # Fraction inputs to land development
        self.mlymc = self._create_array()  # Marginal land yield mult from capital
        self.mpai = self._create_array()  # Marginal productivity agr inputs
        self.mpld = self._create_array()  # Marginal productivity land development

        # Loop 3 - Land erosion and urban-industrial use
        self.all = self._create_array()  # Average life of land [years]
        self.llmy = self._create_array()  # Land life multiplier from yield
        self.llmy1 = self._create_array()  # LLMY before policy
        self.llmy2 = self._create_array()  # LLMY after policy
        self.ler = self._create_array()  # Land erosion rate [ha/year]
        self.lrui = self._create_array()  # Land removal for urban-industrial [ha/yr]
        self.uilpc = self._create_array()  # Urban-industrial land per capita [ha/person]
        self.uilr = self._create_array()  # Urban-industrial land required [ha]

        # Loop 4 - Land fertility degradation
        self.lfd = self._create_array()  # Land fertility degradation [kg/ha/yr/yr]
        self.lfdr = self._create_array()  # Land fertility degradation rate [1/yr]

        # Loop 5 - Land fertility regeneration
        self.lfr = self._create_array()  # Land fertility regeneration [kg/ha/yr/yr]
        self.lfrt = self._create_array()  # Land fertility regeneration time [yrs]

        # Loop 6 - Discontinuing land maintenance
        self.falm = self._create_array()  # Fraction inputs to land maintenance
        self.fr = self._create_array()  # Food ratio
        self.cpfr = self._create_array()  # Change in perceived food ratio

        # 2004 update: yield technology
        self.frd = self._create_array()  # Food ratio difference
        self.ytcm = self._create_array()  # Yield tech change multiplier
        self.ytcr = self._create_array()  # Yield tech change rate
        self.yt = self._create_array()  # Yield technology
        self.lyf2 = self._create_array()  # Land yield factor 2

        # Exogenous inputs from other sectors
        self.pop = self._create_array()  # Population [persons]
        self.io = self._create_array()  # Industrial output [$/year]
        self.iopc = self._create_array()  # Industrial output per capita [$/person/yr]
        self.ppolx = self._create_array()  # Persistent pollution index

    def set_table_functions(self, json_file: Path | None = None) -> None:
        """Load table functions"""
        func_names = [
            "IFPC1",
            "IFPC2",
            "FIOAA1",
            "FIOAA2",
            "DCPH",
            "LYMC",
            "LYMAP1",
            "LYMAP2",
            "FIALD",
            "MLYMC",
            "LLMY1",
            "LLMY2",
            "UILPC",
            "LFDR",
            "LFRT",
            "FALM",
            "YTCM",
            "FRD",
        ]
        self._table_funcs = self._load_table_functions(func_names, json_file)

    def set_delay_functions(self, method: Literal["euler", "odeint"] = "euler") -> None:
        """Initialize delay functions"""
        self.smooth_cai = Smooth(self.ai, self.dt, self.time, method=method)
        self.smooth_fr = Smooth(self.fr, self.dt, self.time, method=method)
        self.dlinf3_yt = Dlinf3(self.yt, self.dt, self.time, method=method)

    # ========================================================================
    # STATE UPDATE METHODS
    # ========================================================================

    def update_state_al(self, k: int, j: int, jk: int) -> None:
        """
        Update arable land state variable.
        From step j requires: LDR, LER, LRUI
        """
        self.al[k] = self.al[j] + self.dt * (self.ldr[jk] - self.ler[jk] - self.lrui[jk])

    def update_state_pal(self, k: int, j: int, jk: int) -> None:
        """
        Update potentially arable land state variable.
        From step j requires: LDR
        """
        self.pal[k] = self.pal[j] - self.dt * self.ldr[jk]

    def update_state_uil(self, k: int, j: int, jk: int) -> None:
        """
        Update urban-industrial land state variable.
        From step j requires: LRUI
        """
        self.uil[k] = self.uil[j] + self.dt * self.lrui[jk]

    def update_state_lfert(self, k: int, j: int, jk: int) -> None:
        """
        Update land fertility state variable.
        From step j requires: LFR, LFD
        """
        self.lfert[k] = self.lfert[j] + self.dt * (self.lfr[jk] - self.lfd[jk])

    def update_state_ai(self, k: int, j: int, jk: int) -> None:
        """
        Update agricultural inputs state variable.
        From step j requires: AIC
        """
        self.ai[k] = self.ai[j] + self.dt * self.aic[jk]

    def update_state_pfr(self, k: int, j: int, jk: int) -> None:
        """
        Update perceived food ratio state variable.
        From step j requires: CPFR
        """
        self.pfr[k] = self.pfr[j] + self.dt * self.cpfr[j]

    def update_state_yt(self, k: int, j: int, jk: int) -> None:
        """
        Update yield technology state variable (2004 update).
        From step j requires: YTCR
        """
        self.yt[k] = self.yt[j] + self.dt * self.ytcr[jk]

    # ========================================================================
    # LOOP 1 - FOOD FROM INVESTMENT IN LAND DEVELOPMENT
    # ========================================================================

    def update_lfc(self, k: int) -> None:
        """
        Update land fraction cultivated.
        From step k requires: AL
        """
        self.lfc[k] = self.al[k] / self.constants.palt

    def update_f(self, k: int) -> None:
        """
        Update food production.
        From step k requires: LY, AL
        """
        self.f[k] = self.ly[k] * self.al[k] * self.constants.lfh * (1 - self.constants.pl)

    def update_fpc(self, k: int) -> None:
        """
        Update food per capita.
        From step k requires: F, POP
        """
        self.fpc[k] = self.f[k] / self.pop[k]

    def update_ifpc(self, k: int) -> None:
        """
        Update indicated food per capita.
        From step k requires: IOPC
        """
        self.ifpc1[k] = self._table_funcs["ifpc1"](self.iopc[k])
        self.ifpc2[k] = self._table_funcs["ifpc2"](self.iopc[k])
        self.ifpc[k] = clip(self.ifpc2[k], self.ifpc1[k], self.time[k], self.pyear)

    def update_fioaa(self, k: int) -> None:
        """
        Update fraction of industrial output allocated to agriculture.
        From step k requires: FPC, IFPC
        """
        self.fioaa1[k] = self._table_funcs["fioaa1"](self.fpc[k] / self.ifpc[k])
        self.fioaa2[k] = self._table_funcs["fioaa2"](self.fpc[k] / self.ifpc[k])
        self.fioaa[k] = clip(self.fioaa2[k], self.fioaa1[k], self.time[k], self.pyear)

    def update_tai(self, k: int) -> None:
        """
        Update total agricultural investment.
        From step k requires: IO, FIOAA
        """
        self.tai[k] = self.io[k] * self.fioaa[k]

    def update_dcph(self, k: int) -> None:
        """
        Update development cost per hectare.
        From step k requires: PAL
        """
        self.dcph[k] = self._table_funcs["dcph"](self.pal[k] / self.constants.palt)

    def update_ldr(self, k: int, kl: int) -> None:
        """
        Update land development rate.
        From step k requires: TAI, FIALD, DCPH
        """
        self.ldr[kl] = self.tai[k] * self.fiald[k] / self.dcph[k]

    # ========================================================================
    # LOOP 2 - FOOD FROM INVESTMENT IN AGRICULTURAL INPUTS
    # ========================================================================

    def update_cai(self, k: int) -> None:
        """
        Update current agricultural inputs.
        From step k requires: TAI, FIALD
        """
        self.cai[k] = self.tai[k] * (1 - self.fiald[k])

    def update_aic(self, k: int) -> None:
        """
        Update agricultural inputs change rate.
        From step k requires: CAI, AI, ALAI
        """
        self.aic[k] = (self.cai[k] - self.ai[k]) / self.alai[k]

    def update_alai(self, k: int) -> None:
        """
        Update average lifetime of agricultural inputs.
        From step k requires: nothing
        """
        self.alai[k] = clip(self.constants.alai2, self.constants.alai1, self.time[k], self.pyear)

    def update_aiph(self, k: int) -> None:
        """
        Update agricultural inputs per hectare.
        From step k requires: AI, FALM, AL
        """
        self.aiph[k] = self.ai[k] * (1 - self.falm[k]) / self.al[k]

    def update_lymc(self, k: int) -> None:
        """
        Update land yield multiplier from capital.
        From step k requires: AIPH
        """
        self.lymc[k] = self._table_funcs["lymc"](self.aiph[k])

    def update_lyf(self, k: int) -> None:
        """
        Update land yield factor.
        From step k requires: LYF2
        """
        self.lyf[k] = clip(self.lyf2[k], self.constants.lyf1, self.time[k], self.pyear_y_tech)

    def update_lymap(self, k: int) -> None:
        """
        Update land yield multiplier from air pollution.
        From step k requires: IO
        """
        self.lymap1[k] = self._table_funcs["lymap1"](self.io[k] / self.constants.io70)
        self.lymap2[k] = self._table_funcs["lymap2"](self.io[k] / self.constants.io70)
        self.lymap[k] = clip(self.lymap2[k], self.lymap1[k], self.time[k], self.pyear)

    def update_ly(self, k: int) -> None:
        """
        Update land yield.
        From step k requires: LYF, LFERT, LYMC, LYMAP
        """
        self.ly[k] = self.lyf[k] * self.lfert[k] * self.lymc[k] * self.lymap[k]

    # ========================================================================
    # LOOP 1 & 2 - INVESTMENT ALLOCATION DECISION
    # ========================================================================

    def update_mlymc(self, k: int) -> None:
        """
        Update marginal land yield multiplier from capital.
        From step k requires: AIPH
        """
        self.mlymc[k] = self._table_funcs["mlymc"](self.aiph[k])

    def update_mpai(self, k: int) -> None:
        """
        Update marginal productivity of agricultural inputs.
        From step k requires: ALAI, LY, MLYMC, LYMC
        """
        self.mpai[k] = self.alai[k] * self.ly[k] * self.mlymc[k] / self.lymc[k]

    def update_mpld(self, k: int) -> None:
        """
        Update marginal productivity of land development.
        From step k requires: LY, DCPH
        """
        self.mpld[k] = self.ly[k] / (self.dcph[k] * self.constants.sd)

    def update_fiald(self, k: int) -> None:
        """
        Update fraction of inputs allocated to land development.
        From step k requires: MPLD, MPAI
        """
        self.fiald[k] = self._table_funcs["fiald"](self.mpld[k] / self.mpai[k])

    # ========================================================================
    # LOOP 3 - LAND EROSION AND URBAN-INDUSTRIAL USE
    # ========================================================================

    def update_all(self, k: int) -> None:
        """
        Update average life of land.
        From step k requires: LLMY
        """
        self.all[k] = self.constants.alln * self.llmy[k]

    def update_llmy(self, k: int) -> None:
        """
        Update land life multiplier from yield.
        From step k requires: LY
        """
        self.llmy1[k] = self._table_funcs["llmy1"](self.ly[k] / self.constants.ilf)
        self.llmy2[k] = self._table_funcs["llmy2"](self.ly[k] / self.constants.ilf)
        self.llmy[k] = clip(self.llmy2[k], self.llmy1[k], self.time[k], self.pyear)

    def update_ler(self, k: int, kl: int) -> None:
        """
        Update land erosion rate.
        From step k requires: AL, ALL
        """
        self.ler[kl] = self.al[k] / self.all[k]

    def update_uilpc(self, k: int) -> None:
        """
        Update urban-industrial land per capita.
        From step k requires: IOPC
        """
        self.uilpc[k] = self._table_funcs["uilpc"](self.iopc[k])

    def update_uilr(self, k: int) -> None:
        """
        Update urban-industrial land required.
        From step k requires: UILPC, POP
        """
        self.uilr[k] = self.uilpc[k] * self.pop[k]

    def update_lrui(self, k: int, kl: int) -> None:
        """
        Update land removal for urban-industrial use.
        From step k requires: UILR, UIL
        """
        self.lrui[kl] = np.maximum(0, (self.uilr[k] - self.uil[k]) / self.constants.uildt)

    # ========================================================================
    # LOOP 4 - LAND FERTILITY DEGRADATION
    # ========================================================================

    def update_lfdr(self, k: int) -> None:
        """
        Update land fertility degradation rate.
        From step k requires: PPOLX
        """
        self.lfdr[k] = self._table_funcs["lfdr"](self.ppolx[k])

    def update_lfd(self, k: int, kl: int) -> None:
        """
        Update land fertility degradation.
        From step k requires: LFERT, LFDR
        """
        self.lfd[kl] = self.lfert[k] * self.lfdr[k]

    # ========================================================================
    # LOOP 5 - LAND FERTILITY REGENERATION
    # ========================================================================

    def update_lfrt(self, k: int) -> None:
        """
        Update land fertility regeneration time.
        From step k requires: FALM
        """
        self.lfrt[k] = self._table_funcs["lfrt"](self.falm[k])

    def update_lfr(self, k: int, kl: int) -> None:
        """
        Update land fertility regeneration.
        From step k requires: LFERT, LFRT
        """
        self.lfr[kl] = (self.constants.ilf - self.lfert[k]) / self.lfrt[k]

    # ========================================================================
    # LOOP 6 - DISCONTINUING LAND MAINTENANCE
    # ========================================================================

    def update_falm(self, k: int) -> None:
        """
        Update fraction of inputs allocated to land maintenance.
        From step k requires: PFR
        """
        self.falm[k] = self._table_funcs["falm"](self.pfr[k])

    def update_fr(self, k: int) -> None:
        """
        Update food ratio.
        From step k requires: FPC
        """
        self.fr[k] = self.fpc[k] / self.constants.sfpc

    def update_cpfr(self, k: int) -> None:
        """
        Update change in perceived food ratio.
        From step k requires: FR, PFR
        """
        self.cpfr[k] = (self.fr[k] - self.pfr[k]) / self.constants.fspd

    # ========================================================================
    # 2004 UPDATE - YIELD TECHNOLOGY
    # ========================================================================

    def update_frd(self, k: int) -> None:
        """
        Update food ratio difference (2004).
        From step k requires: FR
        """
        self.frd[k] = self.constants.dfr - self.fr[k]

    def update_ytcm(self, k: int) -> None:
        """
        Update yield technology change multiplier (2004).
        From step k requires: FRD
        """
        self.ytcm[k] = self._table_funcs["ytcm"](self.frd[k])

    def update_ytcr(self, k: int, j: int) -> None:
        """
        Update yield technology change rate (2004).
        From step k requires: YTCM, YT
        """
        if self.time[k] < self.pyear_y_tech:
            self.ytcr[k] = 0
        else:
            self.ytcr[k] = self.ytcm[k] * self.yt[j]

    def update_lyf2(self, k: int) -> None:
        """
        Update land yield factor 2 (2004).
        From step k requires: YT
        """
        self.lyf2[k] = self.dlinf3_yt(k, self.constants.tdt)
