"""Population sector of the World3 model

This module implements the population dynamics with four age cohorts:
- P1: ages 0-14
- P2: ages 15-44
- P3: ages 45-64
- P4: ages 65+

The sector models birth rates, death rates, and maturation between age groups,
influenced by factors like food availability, health services, and pollution.
"""

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from fast_pyworld3.sectors.base import BaseSector, SectorConfig
from fast_pyworld3.utils import Dlinf3, Smooth, clip


@dataclass
class PopulationConstants:
    """Constants for the population sector"""

    # Initial populations by age group [persons]
    p1i: float = 65e7  # Ages 0-14
    p2i: float = 70e7  # Ages 15-44
    p3i: float = 19e7  # Ages 45-64
    p4i: float = 6e7  # Ages 65+

    # Fertility and family size
    dcfsn: float = 3.8  # Desired completed family size normal
    fcest: float = 4000.0  # Fertility control effectiveness set time [year]
    mtfn: float = 12.0  # Maximum total fertility normal
    rlt: float = 30.0  # Reproductive lifetime [years]
    zpgt: float = 4000.0  # Zero population growth time [year]

    # Life expectancy and health
    len: float = 28.0  # Life expectancy normal [years]
    hsid: float = 20.0  # Health services impact delay [years]
    iphst: float = 1940.0  # Implementation of health services time [year]

    # Social and economic delays
    ieat: float = 3.0  # Income expectation averaging time [years]
    lpd: float = 20.0  # Lifetime perception delay [years]
    sad: float = 20.0  # Social adjustment delay [years]

    # Population equilibrium
    pet: float = 4000.0  # Population equilibrium time [year]

    # Subsistence food level
    sfpc: float = 230.0  # Subsistence food per capita [kg/person/year]


class Population(BaseSector):
    """
    Population sector with four age levels.

    Can be run independently from other sectors with exogenous inputs.
    Models births, deaths, and aging across four age cohorts.

    Example:
        >>> config = SectorConfig(year_min=1900, year_max=2100, dt=0.5)
        >>> pop = Population(config)
        >>> pop.init_constants()
        >>> pop.init_variables()
        >>> pop.set_table_functions()
        >>> pop.set_delay_functions()
    """

    def __init__(self, config: SectorConfig):
        super().__init__(config)
        self.constants = PopulationConstants()
        self._table_funcs: dict = {}

        # Policy implementation years (set by World3 model)
        self.pyear: float = 1975.0  # Policy implementation year
        self.iphst: float = 1940.0  # Health services implementation year

    def init_constants(
        self,
        p1i: float = 65e7,
        p2i: float = 70e7,
        p3i: float = 19e7,
        p4i: float = 6e7,
        dcfsn: float = 3.8,
        fcest: float = 4000.0,
        hsid: float = 20.0,
        ieat: float = 3.0,
        len_: float = 28.0,
        lpd: float = 20.0,
        mtfn: float = 12.0,
        pet: float = 4000.0,
        rlt: float = 30.0,
        sad: float = 20.0,
        zpgt: float = 4000.0,
        sfpc: float = 230.0,
        iphst: float = 1940.0,
        **kwargs: float,
    ) -> None:
        """Initialize population constants with 2004 update values"""
        self.constants = PopulationConstants(
            p1i=p1i,
            p2i=p2i,
            p3i=p3i,
            p4i=p4i,
            dcfsn=dcfsn,
            fcest=fcest,
            hsid=hsid,
            ieat=ieat,
            len=len_,
            lpd=lpd,
            mtfn=mtfn,
            pet=pet,
            rlt=rlt,
            sad=sad,
            zpgt=zpgt,
            sfpc=sfpc,
            iphst=iphst,
        )

    def init_variables(self) -> None:
        """Initialize state and rate variables"""
        # Population by age group [persons]
        self.p1 = self._create_array()  # Ages 0-14
        self.p2 = self._create_array()  # Ages 15-44
        self.p3 = self._create_array()  # Ages 45-64
        self.p4 = self._create_array()  # Ages 65+
        self.pop = self._create_array()  # Total population

        # Maturation rates [persons/year]
        self.mat1 = self._create_array()  # Age 14-15
        self.mat2 = self._create_array()  # Age 44-45
        self.mat3 = self._create_array()  # Age 64-65

        # Death rate subsector
        self.d = self._create_array()  # Total deaths [persons/year]
        self.d1 = self._create_array()  # Deaths ages 0-14
        self.d2 = self._create_array()  # Deaths ages 15-44
        self.d3 = self._create_array()  # Deaths ages 45-64
        self.d4 = self._create_array()  # Deaths ages 65+
        self.cdr = self._create_array()  # Crude death rate [/1000/year]

        self.fpu = self._create_array()  # Fraction population urban
        self.le = self._create_array()  # Life expectancy [years]
        self.lmc = self._create_array()  # Lifetime multiplier from crowding
        self.lmf = self._create_array()  # Lifetime multiplier from food
        self.lmhs = self._create_array()  # Lifetime multiplier from health services
        self.lmhs1 = self._create_array()  # LMHS before policy year
        self.lmhs2 = self._create_array()  # LMHS after policy year
        self.lmp = self._create_array()  # Lifetime multiplier from pollution

        self.m1 = self._create_array()  # Mortality ages 0-14 [/year]
        self.m2 = self._create_array()  # Mortality ages 15-44
        self.m3 = self._create_array()  # Mortality ages 45-64
        self.m4 = self._create_array()  # Mortality ages 65+

        self.ehspc = self._create_array()  # Effective health services per capita
        self.hsapc = self._create_array()  # Health services allocated per capita

        # Birth rate subsector
        self.b = self._create_array()  # Births [persons/year]
        self.cbr = self._create_array()  # Crude birth rate [/1000/year]
        self.cmi = self._create_array()  # Crowding multiplier from industrialization
        self.cmple = self._create_array()  # Compensatory multiplier from perceived LE
        self.tf = self._create_array()  # Total fertility
        self.dtf = self._create_array()  # Desired total fertility
        self.dcfs = self._create_array()  # Desired completed family size
        self.fce = self._create_array()  # Fertility control effectiveness
        self.fie = self._create_array()  # Family income expectation
        self.fm = self._create_array()  # Fecundity multiplier
        self.frsn = self._create_array()  # Family response to social norm
        self.mtf = self._create_array()  # Maximum total fertility
        self.nfc = self._create_array()  # Need for fertility control
        self.ple = self._create_array()  # Perceived life expectancy [years]
        self.sfsn = self._create_array()  # Social family size norm

        self.aiopc = self._create_array()  # Average industrial output per capita
        self.diopc = self._create_array()  # Delayed industrial output per capita
        self.fcapc = self._create_array()  # Fertility control allocated per capita
        self.fcfpc = self._create_array()  # Fertility control facilities per capita
        self.fsafc = self._create_array()  # Fraction services allocated to FC

        # 2004 update: Human Welfare Index components
        self.lei = self._create_array()  # Life expectancy index
        self.gdpc = self._create_array()  # GDP per capita
        self.gdpi = self._create_array()  # GDP index
        self.ei = self._create_array()  # Education index
        self.hwi = self._create_array()  # Human welfare index

        # Exogenous inputs (provided by other sectors in full simulation)
        self.io = self._create_array()  # Industrial output [$/year]
        self.iopc = self._create_array()  # Industrial output per capita
        self.so = self._create_array()  # Service output [$/year]
        self.sopc = self._create_array()  # Service output per capita
        self.f = self._create_array()  # Food [kg/year]
        self.fpc = self._create_array()  # Food per capita
        self.ppolx = self._create_array()  # Persistent pollution index

    def set_table_functions(self, json_file: Path | None = None) -> None:
        """Load nonlinear table functions from JSON"""
        func_names = [
            "M1",
            "M2",
            "M3",
            "M4",
            "LMF",
            "HSAPC",
            "LMHS1",
            "LMHS2",
            "FPU",
            "CMI",
            "LMP",
            "FM",
            "CMPLE",
            "SFSN",
            "FRSN",
            "FCE_TOCLIP",
            "FSAFC",
            "LEI",
            "GDPC",
            "EI",
        ]
        self._table_funcs = self._load_table_functions(func_names, json_file)

    def set_delay_functions(self, method: Literal["euler", "odeint"] = "euler") -> None:
        """Initialize delay and smoothing functions"""
        # Third-order information delays
        self.dlinf3_le = Dlinf3(self.le, self.dt, self.time, method=method)
        self.dlinf3_iopc = Dlinf3(self.iopc, self.dt, self.time, method=method)
        self.dlinf3_fcapc = Dlinf3(self.fcapc, self.dt, self.time, method=method)

        # First-order smoothing
        self.smooth_hsapc = Smooth(self.hsapc, self.dt, self.time, method=method)
        self.smooth_iopc = Smooth(self.iopc, self.dt, self.time, method=method)

    # State variable update methods
    def update_state_p1(self, k: int, j: int, jk: int) -> None:
        """Update population ages 0-14"""
        self.p1[k] = self.p1[j] + self.dt * (self.b[jk] - self.d1[jk] - self.mat1[jk])

    def update_state_p2(self, k: int, j: int, jk: int) -> None:
        """Update population ages 15-44"""
        self.p2[k] = self.p2[j] + self.dt * (self.mat1[jk] - self.d2[jk] - self.mat2[jk])

    def update_state_p3(self, k: int, j: int, jk: int) -> None:
        """Update population ages 45-64"""
        self.p3[k] = self.p3[j] + self.dt * (self.mat2[jk] - self.d3[jk] - self.mat3[jk])

    def update_state_p4(self, k: int, j: int, jk: int) -> None:
        """Update population ages 65+"""
        self.p4[k] = self.p4[j] + self.dt * (self.mat3[jk] - self.d4[jk])

    def update_pop(self, k: int) -> None:
        """Update total population"""
        self.pop[k] = self.p1[k] + self.p2[k] + self.p3[k] + self.p4[k]

    # Death rate subsector methods
    def update_fpu(self, k: int) -> None:
        """Update fraction of population urban"""
        self.fpu[k] = self._table_funcs["fpu"](self.pop[k])

    def update_lmp(self, k: int) -> None:
        """Update lifetime multiplier from pollution"""
        self.lmp[k] = self._table_funcs["lmp"](self.ppolx[k])

    def update_lmf(self, k: int) -> None:
        """Update lifetime multiplier from food"""
        self.lmf[k] = self._table_funcs["lmf"](self.fpc[k] / self.constants.sfpc)

    def update_cmi(self, k: int) -> None:
        """Update crowding multiplier from industrialization"""
        self.cmi[k] = self._table_funcs["cmi"](self.iopc[k])

    def update_hsapc(self, k: int) -> None:
        """Update health services allocated per capita"""
        self.hsapc[k] = self._table_funcs["hsapc"](self.sopc[k])

    def update_ehspc(self, k: int) -> None:
        """Update effective health services per capita"""
        self.ehspc[k] = self.smooth_hsapc(k, self.constants.hsid, self.hsapc[0])

    def update_lmhs(self, k: int) -> None:
        """Update lifetime multiplier from health services"""
        self.lmhs1[k] = self._table_funcs["lmhs1"](self.ehspc[k])
        self.lmhs2[k] = self._table_funcs["lmhs2"](self.ehspc[k])
        self.lmhs[k] = clip(self.lmhs2[k], self.lmhs1[k], self.time[k], self.constants.iphst)

    def update_lmc(self, k: int) -> None:
        """Update lifetime multiplier from crowding"""
        self.lmc[k] = 1.0 - self.cmi[k] * self.fpu[k]

    def update_le(self, k: int) -> None:
        """Update life expectancy"""
        self.le[k] = self.constants.len * self.lmf[k] * self.lmhs[k] * self.lmp[k] * self.lmc[k]

    def update_m1(self, k: int) -> None:
        """Update mortality rate ages 0-14"""
        self.m1[k] = self._table_funcs["m1"](self.le[k])

    def update_m2(self, k: int) -> None:
        """Update mortality rate ages 15-44"""
        self.m2[k] = self._table_funcs["m2"](self.le[k])

    def update_m3(self, k: int) -> None:
        """Update mortality rate ages 45-64"""
        self.m3[k] = self._table_funcs["m3"](self.le[k])

    def update_m4(self, k: int) -> None:
        """Update mortality rate ages 65+"""
        self.m4[k] = self._table_funcs["m4"](self.le[k])

    def update_mat1(self, k: int, kl: int) -> None:
        """Update maturation rate age 14-15"""
        self.mat1[kl] = self.p1[k] * (1.0 - self.m1[k]) / 15.0

    def update_mat2(self, k: int, kl: int) -> None:
        """Update maturation rate age 44-45"""
        self.mat2[kl] = self.p2[k] * (1.0 - self.m2[k]) / 30.0

    def update_mat3(self, k: int, kl: int) -> None:
        """Update maturation rate age 64-65"""
        self.mat3[kl] = self.p3[k] * (1.0 - self.m3[k]) / 20.0

    def update_d1(self, k: int, kl: int) -> None:
        """Update deaths ages 0-14"""
        self.d1[kl] = self.p1[k] * self.m1[k]

    def update_d2(self, k: int, kl: int) -> None:
        """Update deaths ages 15-44"""
        self.d2[kl] = self.p2[k] * self.m2[k]

    def update_d3(self, k: int, kl: int) -> None:
        """Update deaths ages 45-64"""
        self.d3[kl] = self.p3[k] * self.m3[k]

    def update_d4(self, k: int, kl: int) -> None:
        """Update deaths ages 65+"""
        self.d4[kl] = self.p4[k] * self.m4[k]

    def update_d(self, k: int, jk: int) -> None:
        """Update total deaths"""
        self.d[k] = self.d1[jk] + self.d2[jk] + self.d3[jk] + self.d4[jk]

    def update_cdr(self, k: int) -> None:
        """Update crude death rate"""
        self.cdr[k] = 1000.0 * self.d[k] / self.pop[k]

    # Birth rate subsector methods (abbreviated for brevity)
    def update_aiopc(self, k: int) -> None:
        """Update average industrial output per capita"""
        self.aiopc[k] = self.smooth_iopc(k, self.constants.ieat, self.iopc[0])

    def update_diopc(self, k: int) -> None:
        """Update delayed industrial output per capita"""
        self.diopc[k] = self.dlinf3_iopc(k, self.constants.sad)

    def update_fie(self, k: int) -> None:
        """Update family income expectation"""
        self.fie[k] = (self.iopc[k] - self.aiopc[k]) / self.aiopc[k]

    def update_sfsn(self, k: int) -> None:
        """Update social family size norm"""
        self.sfsn[k] = self._table_funcs["sfsn"](self.diopc[k])

    def update_frsn(self, k: int) -> None:
        """Update family response to social norm"""
        self.frsn[k] = self._table_funcs["frsn"](self.fie[k])

    def update_dcfs(self, k: int) -> None:
        """Update desired completed family size"""
        desired = self.constants.dcfsn * self.frsn[k] * self.sfsn[k]
        self.dcfs[k] = clip(2.0, desired, self.time[k], self.constants.zpgt)

    def update_ple(self, k: int) -> None:
        """Update perceived life expectancy"""
        self.ple[k] = self.dlinf3_le(k, self.constants.lpd)

    def update_cmple(self, k: int) -> None:
        """Update compensatory multiplier from perceived life expectancy"""
        self.cmple[k] = self._table_funcs["cmple"](self.ple[k])

    def update_dtf(self, k: int) -> None:
        """Update desired total fertility"""
        self.dtf[k] = self.dcfs[k] * self.cmple[k]

    def update_fm(self, k: int) -> None:
        """Update fecundity multiplier"""
        self.fm[k] = self._table_funcs["fm"](self.le[k])

    def update_mtf(self, k: int) -> None:
        """Update maximum total fertility"""
        self.mtf[k] = self.constants.mtfn * self.fm[k]

    def update_nfc(self, k: int) -> None:
        """Update need for fertility control"""
        self.nfc[k] = self.mtf[k] / self.dtf[k] - 1.0

    def update_fsafc(self, k: int) -> None:
        """Update fraction services allocated to fertility control"""
        self.fsafc[k] = self._table_funcs["fsafc"](self.nfc[k])

    def update_fcapc(self, k: int) -> None:
        """Update fertility control allocated per capita"""
        self.fcapc[k] = self.fsafc[k] * self.sopc[k]

    def update_fcfpc(self, k: int) -> None:
        """Update fertility control facilities per capita"""
        self.fcfpc[k] = self.dlinf3_fcapc(k, self.constants.hsid)

    def update_fce(self, k: int) -> None:
        """Update fertility control effectiveness"""
        fce_val = self._table_funcs["fce_toclip"](self.fcfpc[k])
        self.fce[k] = clip(1.0, fce_val, self.time[k], self.constants.fcest)

    def update_tf(self, k: int) -> None:
        """Update total fertility"""
        self.tf[k] = min(
            self.mtf[k],
            self.mtf[k] * (1.0 - self.fce[k]) + self.dtf[k] * self.fce[k],
        )

    def update_cbr(self, k: int, jk: int) -> None:
        """Update crude birth rate"""
        self.cbr[k] = 1000.0 * self.b[jk] / self.pop[k]

    def update_b(self, k: int, kl: int) -> None:
        """Update births per year"""
        births = self.tf[k] * self.p2[k] * 0.5 / self.constants.rlt
        self.b[kl] = clip(self.d[k], births, self.time[k], self.constants.pet)

    # 2004 update: Human Welfare Index
    def update_lei(self, k: int) -> None:
        """Update life expectancy index"""
        self.lei[k] = self._table_funcs["lei"](self.le[k])

    def update_gdpc(self, k: int) -> None:
        """Update GDP per capita"""
        self.gdpc[k] = self._table_funcs["gdpc"](self.iopc[k])

    def update_gdpi(self, k: int) -> None:
        """Update GDP index"""
        log_gdpc = math.log(self.gdpc[k])
        self.gdpi[k] = (log_gdpc - math.log(24.0)) / (math.log(9508.0) - math.log(24.0))

    def update_ei(self, k: int) -> None:
        """Update education index"""
        self.ei[k] = self._table_funcs["ei"](self.gdpc[k])

    def update_hwi(self, k: int) -> None:
        """Update human welfare index"""
        self.hwi[k] = (self.lei[k] + self.ei[k] + self.gdpi[k]) / 3.0
