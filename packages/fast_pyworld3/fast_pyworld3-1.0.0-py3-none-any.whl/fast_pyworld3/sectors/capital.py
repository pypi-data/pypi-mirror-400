"""Capital sector (Industrial and Service) of the World3 model"""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import numpy as np
import numpy.typing as npt

from fast_pyworld3.sectors.base import BaseSector, SectorConfig
from fast_pyworld3.utils import clip, Smooth


@dataclass
class CapitalConstants:
    """Constants for the capital sector"""

    # Initial capital stocks [dollars]
    ici: float = 2.1e11  # Industrial capital initial
    sci: float = 1.44e11  # Service capital initial

    # Capital output ratios [years]
    icor1: float = 3.0  # Industrial capital-output ratio (before policy)
    icor2: float = 3.0  # Industrial capital-output ratio (after policy)
    scor1: float = 1.0  # Service capital-output ratio (before policy)
    scor2: float = 1.0  # Service capital-output ratio (after policy)

    # Average lifetimes [years]
    alic1: float = 14.0  # Average lifetime industrial capital (before)
    alic2: float = 14.0  # Average lifetime industrial capital (after)
    alsc1: float = 20.0  # Average lifetime service capital (before)
    alsc2: float = 20.0  # Average lifetime service capital (after)

    # Resource allocation fractions
    fioac1: float = 0.43  # Fraction industrial output to consumption (before)
    fioac2: float = 0.43  # Fraction industrial output to consumption (after)

    # Other parameters
    iet: float = 4000.0  # Industrial equilibrium time [year]
    iopcd: float = 400.0  # Industrial output per capita desired [$/person/year]
    lfpf: float = 0.75  # Labor force participation fraction
    lufdt: float = 2.0  # Labor utilization fraction delay time [years]


class Capital(BaseSector):
    """
    Capital sector modeling industrial and service capital.

    Includes three subsectors:
    - Industrial: production capacity
    - Service: health, education, etc.
    - Jobs: employment from capital stocks
    """

    def __init__(self, config: SectorConfig):
        super().__init__(config)
        self.constants = CapitalConstants()
        self._table_funcs: dict = {}

        # Policy implementation years (set by World3 model)
        self.pyear: float = 1975.0  # Policy implementation year

    def init_constants(
        self,
        ici: float = 2.1e11,
        sci: float = 1.44e11,
        iet: float = 4000.0,
        iopcd: float = 400.0,
        lfpf: float = 0.75,
        lufdt: float = 2.0,
        icor1: float = 3.0,
        icor2: float = 3.0,
        scor1: float = 1.0,
        scor2: float = 1.0,
        alic1: float = 14.0,
        alic2: float = 14.0,
        alsc1: float = 20.0,
        alsc2: float = 20.0,
        fioac1: float = 0.43,
        fioac2: float = 0.43,
        **kwargs: float,
    ) -> None:
        """Initialize capital constants"""
        self.constants = CapitalConstants(
            ici=ici,
            sci=sci,
            iet=iet,
            iopcd=iopcd,
            lfpf=lfpf,
            lufdt=lufdt,
            icor1=icor1,
            icor2=icor2,
            scor1=scor1,
            scor2=scor2,
            alic1=alic1,
            alic2=alic2,
            alsc1=alsc1,
            alsc2=alsc2,
            fioac1=fioac1,
            fioac2=fioac2,
        )

    def init_variables(self) -> None:
        """Initialize capital sector variables"""
        # Industrial subsector
        self.ic = self._create_array()  # Industrial capital [dollars]
        self.io = self._create_array()  # Industrial output [$/year]
        self.icdr = self._create_array()  # IC depreciation rate [$/year]
        self.icir = self._create_array()  # IC investment rate [$/year]
        self.icor = self._create_array()  # IC-output ratio [years]
        self.iopc = self._create_array()  # IO per capita [$/person/year]
        self.alic = self._create_array()  # Average lifetime of IC [years]
        self.fioac = self._create_array()  # Fraction IO to consumption
        self.fioacc = self._create_array()  # FIOAC constant
        self.fioacv = self._create_array()  # FIOAC variable
        self.fioai = self._create_array()  # Fraction IO to industry
        self.cio = self._create_array()  # Consumption of IO (2004)
        self.ciopc = self._create_array()  # CIO per capita (2004)

        # Service subsector
        self.sc = self._create_array()  # Service capital [dollars]
        self.so = self._create_array()  # Service output [$/year]
        self.scdr = self._create_array()  # SC depreciation rate [$/year]
        self.scir = self._create_array()  # SC investment rate [$/year]
        self.scor = self._create_array()  # SC-output ratio [years]
        self.sopc = self._create_array()  # SO per capita [$/person/year]
        self.alsc = self._create_array()  # Average lifetime of SC [years]
        self.isopc = self._create_array()  # Indicated SO per capita
        self.isopc1 = self._create_array()  # ISOPC before policy
        self.isopc2 = self._create_array()  # ISOPC after policy
        self.fioas = self._create_array()  # Fraction IO to services
        self.fioas1 = self._create_array()  # FIOAS before policy
        self.fioas2 = self._create_array()  # FIOAS after policy

        # Job subsector
        self.j = self._create_array()  # Jobs [persons]
        self.jph = self._create_array()  # Jobs per hectare [persons/hectare]
        self.jpicu = self._create_array()  # Jobs per IC unit [persons/$]
        self.jpscu = self._create_array()  # Jobs per SC unit [persons/$]
        self.lf = self._create_array()  # Labor force [persons]
        self.cuf = self._create_array()  # Capital utilization fraction
        self.luf = self._create_array()  # Labor utilization fraction
        self.lufd = self._create_array()  # LUF delayed
        self.pjas = self._create_array()  # Potential jobs agriculture
        self.pjis = self._create_array()  # Potential jobs industry
        self.pjss = self._create_array()  # Potential jobs services

        # Exogenous inputs from other sectors
        # (These will be properly set by World3 during simulation)
        self.aiph = self._create_array()  # From Agriculture
        self.al = self._create_array()    # From Agriculture
        self.fioaa = self._create_array() # From Agriculture/World3
        self.pop = self._create_array()   # From Population
        self.p2 = self._create_array()    # From Population
        self.p3 = self._create_array()    # From Population
        self.fcaor = self._create_array() # From Resource
        self.nrfr = self._create_array()  # From Resource

    def set_table_functions(self, json_file: Path | None = None) -> None:
        """Load table functions from JSON"""
        func_names = [
            "FIOACV",
            "ISOPC1",
            "ISOPC2",
            "FIOAS1",
            "FIOAS2",
            "JPICU",
            "JPSCU",
            "JPH",
            "CUF",
        ]
        self._table_funcs = self._load_table_functions(func_names, json_file)

    def set_delay_functions(self, method: Literal["euler", "odeint"] = "euler") -> None:
        """Initialize delay functions"""
        self.smooth_luf = Smooth(self.luf, self.dt, self.time, method=method)

    # ========================================================================
    # STATE UPDATE METHODS
    # ========================================================================

    def update_state_ic(self, k: int, j: int, jk: int) -> None:
        """Update industrial capital"""
        self.ic[k] = self.ic[jk] + self.dt * (self.icir[jk] - self.icdr[jk])

    def update_state_sc(self, k: int, j: int, jk: int) -> None:
        """Update service capital"""
        self.sc[k] = self.sc[j] + self.dt * (self.scir[jk] - self.scdr[jk])

    # ========================================================================
    # INDUSTRIAL SUBSECTOR UPDATE METHODS
    # ========================================================================

    def update_alic(self, k: int) -> None:
        """
        Update average lifetime of industrial capital.
        From step k requires: nothing
        """
        self.alic[k] = clip(self.constants.alic2, self.constants.alic1, self.time[k], self.pyear)

    def update_icdr(self, k: int, kl: int) -> None:
        """
        Update industrial capital depreciation rate.
        From step k requires: IC, ALIC
        """
        self.icdr[kl] = self.ic[k] / self.alic[k]

    def update_icor(self, k: int) -> None:
        """
        Update industrial capital-output ratio.
        From step k requires: nothing
        """
        self.icor[k] = clip(self.constants.icor2, self.constants.icor1, self.time[k], self.pyear)

    def update_io(self, k: int) -> None:
        """
        Update industrial output.
        From step k requires: IC, FCAOR, CUF, ICOR
        """
        self.io[k] = self.ic[k] * (1 - self.fcaor[k]) * self.cuf[k] / self.icor[k]

    def update_iopc(self, k: int) -> None:
        """
        Update industrial output per capita.
        From step k requires: IO, POP
        """
        self.iopc[k] = self.io[k] / self.pop[k]

    def update_fioac(self, k: int) -> None:
        """
        Update fraction of industrial output allocated to consumption.
        From step k requires: IOPC
        """
        self.fioacv[k] = self._table_funcs["fioacv"](self.iopc[k] / self.constants.iopcd)
        self.fioacc[k] = clip(
            self.constants.fioac2,
            self.constants.fioac1,
            self.time[k],
            self.pyear,
        )
        self.fioac[k] = clip(
            self.fioacv[k],
            self.fioacc[k],
            self.time[k],
            self.constants.iet,
        )

    def update_cio(self, k: int) -> None:
        """
        Update consumption of industrial output (2004 update).
        From step k requires: FIOAC, IO
        """
        self.cio[k] = self.fioac[k] * self.io[k]

    def update_ciopc(self, k: int) -> None:
        """
        Update consumption of industrial output per capita (2004 update).
        From step k requires: CIO, POP
        """
        self.ciopc[k] = self.cio[k] / self.pop[k]

    def update_fioai(self, k: int) -> None:
        """
        Update fraction of industrial output allocated to industry.
        From step k requires: FIOAA, FIOAS, FIOAC
        """
        self.fioai[k] = 1 - self.fioaa[k] - self.fioas[k] - self.fioac[k]

    def update_icir(self, k: int, kl: int) -> None:
        """
        Update industrial capital investment rate.
        From step k requires: IO, FIOAI
        """
        self.icir[kl] = self.io[k] * self.fioai[k]

    # ========================================================================
    # SERVICE SUBSECTOR UPDATE METHODS
    # ========================================================================

    def update_isopc(self, k: int) -> None:
        """
        Update indicated service output per capita.
        From step k requires: IOPC
        """
        self.isopc1[k] = self._table_funcs["isopc1"](self.iopc[k])
        self.isopc2[k] = self._table_funcs["isopc2"](self.iopc[k])
        self.isopc[k] = clip(
            self.isopc2[k],
            self.isopc1[k],
            self.time[k],
            self.pyear,
        )

    def update_alsc(self, k: int) -> None:
        """
        Update average lifetime of service capital.
        From step k requires: nothing
        """
        self.alsc[k] = clip(self.constants.alsc2, self.constants.alsc1, self.time[k], self.pyear)

    def update_scdr(self, k: int, kl: int) -> None:
        """
        Update service capital depreciation rate.
        From step k requires: SC, ALSC
        """
        self.scdr[kl] = self.sc[k] / self.alsc[k]

    def update_scor(self, k: int) -> None:
        """
        Update service capital-output ratio.
        From step k requires: nothing
        """
        self.scor[k] = clip(self.constants.scor2, self.constants.scor1, self.time[k], self.pyear)

    def update_so(self, k: int) -> None:
        """
        Update service output.
        From step k requires: SC, CUF, SCOR
        """
        self.so[k] = self.sc[k] * self.cuf[k] / self.scor[k]

    def update_sopc(self, k: int) -> None:
        """
        Update service output per capita.
        From step k requires: SO, POP
        """
        self.sopc[k] = self.so[k] / self.pop[k]

    def update_fioas(self, k: int) -> None:
        """
        Update fraction of industrial output allocated to services.
        From step k requires: SOPC, ISOPC
        """
        self.fioas1[k] = self._table_funcs["fioas1"](self.sopc[k] / self.isopc[k])
        self.fioas2[k] = self._table_funcs["fioas2"](self.sopc[k] / self.isopc[k])
        self.fioas[k] = clip(
            self.fioas2[k],
            self.fioas1[k],
            self.time[k],
            self.pyear,
        )

    def update_scir(self, k: int, kl: int) -> None:
        """
        Update service capital investment rate.
        From step k requires: IO, FIOAS
        """
        self.scir[kl] = self.io[k] * self.fioas[k]

    # ========================================================================
    # JOB SUBSECTOR UPDATE METHODS
    # ========================================================================

    def update_lufd(self, k: int) -> None:
        """
        Update labor utilization fraction delayed.
        From step k=0 requires: LUF, else nothing
        """
        self.lufd[k] = self.smooth_luf(k, self.constants.lufdt, 1)

    def update_cuf(self, k: int) -> None:
        """
        Update capital utilization fraction.
        From step k requires: LUFD
        """
        self.cuf[k] = self._table_funcs["cuf"](self.lufd[k])

    def update_jpicu(self, k: int) -> None:
        """
        Update jobs per industrial capital unit.
        From step k requires: IOPC
        """
        self.jpicu[k] = self._table_funcs["jpicu"](self.iopc[k])

    def update_pjis(self, k: int) -> None:
        """
        Update potential jobs in industrial sector.
        From step k requires: IC, JPICU
        """
        self.pjis[k] = self.ic[k] * self.jpicu[k]

    def update_jpscu(self, k: int) -> None:
        """
        Update jobs per service capital unit.
        From step k requires: SOPC
        """
        self.jpscu[k] = self._table_funcs["jpscu"](self.sopc[k])

    def update_pjss(self, k: int) -> None:
        """
        Update potential jobs in service sector.
        From step k requires: SC, JPSCU
        """
        self.pjss[k] = self.sc[k] * self.jpscu[k]

    def update_jph(self, k: int) -> None:
        """
        Update jobs per hectare.
        From step k requires: AIPH
        """
        self.jph[k] = self._table_funcs["jph"](self.aiph[k])

    def update_pjas(self, k: int) -> None:
        """
        Update potential jobs in agricultural sector.
        From step k requires: JPH, AL
        """
        self.pjas[k] = self.jph[k] * self.al[k]

    def update_j(self, k: int) -> None:
        """
        Update total jobs.
        From step k requires: PJIS, PJAS, PJSS
        """
        self.j[k] = self.pjis[k] + self.pjas[k] + self.pjss[k]

    def update_lf(self, k: int) -> None:
        """
        Update labor force.
        From step k requires: P2, P3
        """
        self.lf[k] = (self.p2[k] + self.p3[k]) * self.constants.lfpf

    def update_luf(self, k: int) -> None:
        """
        Update labor utilization fraction.
        From step k requires: J, LF
        """
        self.luf[k] = self.j[k] / self.lf[k]
