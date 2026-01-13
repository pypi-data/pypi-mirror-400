"""
Core World3 model integrating all five sectors.

The World3 model simulates global dynamics from 1900-2100 across five
interconnected sectors: Population, Capital, Agriculture, Pollution, and Resources.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import numpy as np
import numpy.typing as npt

from fast_pyworld3.sectors import Agriculture, Capital, Pollution, Population, Resource
from fast_pyworld3.sectors.base import SectorConfig


@dataclass
class World3Config:
    """Configuration for World3 model"""

    year_min: float = 1900.0
    year_max: float = 2100.0
    dt: float = 0.5

    # Policy implementation years
    pyear: float = 1975.0  # General policy year
    pyear_res_tech: float = 4000.0  # Resource technology policy
    pyear_pp_tech: float = 4000.0  # Pollution technology policy
    pyear_fcaor: float = 4000.0  # Resource capital allocation policy
    pyear_y_tech: float = 4000.0  # Agricultural yield technology policy
    iphst: float = 1940.0  # Health services implementation year

    verbose: bool = False


class World3:
    """
    The World3 model from "Limits to Growth: The 30-Year Update" (2004).

    This integrates five sectors that model global dynamics:
    - Population: demographic changes across four age groups
    - Capital: industrial and service production
    - Agriculture: food production and land use
    - Pollution: persistent pollution generation and assimilation
    - Resource: nonrenewable resource depletion

    Example:
        >>> config = World3Config(year_min=1900, year_max=2100, dt=0.5)
        >>> world3 = World3(config)
        >>> world3.init_constants()
        >>> world3.init_variables()
        >>> world3.set_table_functions()
        >>> world3.set_delay_functions()
        >>> world3.run()
        >>> print(f"Final population: {world3.pop.pop[-1]:.2e}")
    """

    def __init__(self, config: World3Config | None = None):
        if config is None:
            config = World3Config()

        self.config = config

        # Create base configuration for sectors
        sector_config = SectorConfig(
            year_min=config.year_min,
            year_max=config.year_max,
            dt=config.dt,
            verbose=config.verbose,
        )

        # Initialize sectors
        self.pop = Population(sector_config)
        self.cap = Capital(sector_config)
        self.agr = Agriculture(sector_config)
        self.pol = Pollution(sector_config)
        self.res = Resource(sector_config)

        # Time arrays (shared across sectors)
        self.dt = config.dt
        self.year_min = config.year_min
        self.year_max = config.year_max
        self.length = config.year_max - config.year_min
        self.n = int(self.length / config.dt) + 1
        self.time = np.arange(config.year_min, config.year_max + config.dt, config.dt)

        # Control flags
        self.verbose = config.verbose
        self._initialized = False

    def init_constants(
        self,
        # Population constants
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
        # Capital constants
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
        # Agriculture constants
        ali: float = 0.9e9,
        pali: float = 2.3e9,
        lfh: float = 0.7,
        palt: float = 3.2e9,
        pl: float = 0.1,
        alai1: float = 2.0,
        alai2: float = 2.0,
        io70: float = 7.9e11,
        lyf1: float = 1.0,
        sd: float = 0.07,
        uili: float = 8.2e6,
        alln: float = 1000.0,
        uildt: float = 10.0,
        lferti: float = 600.0,
        ilf: float = 600.0,
        fspd: float = 2.0,
        sfpc: float = 230.0,
        dfr: float = 2.0,
        # Pollution constants
        pp19: float = 2.5e7,
        apct: float = 4000.0,
        imef: float = 0.1,
        imti: float = 10.0,
        frpm: float = 0.02,
        ghup: float = 4e-9,
        faipm: float = 0.001,
        amti: float = 1.0,
        pptd: float = 20.0,
        ahl70: float = 1.5,
        pp70: float = 1.36e8,
        dppolx: float = 1.2,
        ppgf1: float = 1.0,
        # Resource constants
        nri: float = 1e12,
        nruf1: float = 1.0,
        drur: float = 4.8e9,
        tdt: float = 20.0,
    ) -> None:
        """
        Initialize constants for all five sectors.

        Constants can be customized to explore different scenarios.
        See individual sector documentation for parameter meanings.
        """
        self.pop.init_constants(
            p1i=p1i,
            p2i=p2i,
            p3i=p3i,
            p4i=p4i,
            dcfsn=dcfsn,
            fcest=fcest,
            hsid=hsid,
            ieat=ieat,
            len_=len_,
            lpd=lpd,
            mtfn=mtfn,
            pet=pet,
            rlt=rlt,
            sad=sad,
            zpgt=zpgt,
            sfpc=sfpc,
            iphst=self.config.iphst,
        )

        self.cap.init_constants(
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

        self.agr.init_constants(
            ali=ali,
            pali=pali,
            lfh=lfh,
            palt=palt,
            pl=pl,
            alai1=alai1,
            alai2=alai2,
            io70=io70,
            lyf1=lyf1,
            sd=sd,
            uili=uili,
            alln=alln,
            uildt=uildt,
            lferti=lferti,
            ilf=ilf,
            fspd=fspd,
            sfpc=sfpc,
            dfr=dfr,
        )

        self.pol.init_constants(
            pp19=pp19,
            apct=apct,
            io70=io70,
            imef=imef,
            imti=imti,
            frpm=frpm,
            ghup=ghup,
            faipm=faipm,
            amti=amti,
            pptd=pptd,
            ahl70=ahl70,
            pp70=pp70,
            dppolx=dppolx,
            ppgf1=ppgf1,
        )

        self.res.init_constants(
            nri=nri,
            nruf1=nruf1,
            drur=drur,
            tdt=tdt,
        )

    def init_variables(self) -> None:
        """Initialize state and rate variables for all sectors"""
        self.pop.init_variables()
        self.cap.init_variables()
        self.agr.init_variables()
        self.pol.init_variables()
        self.res.init_variables()

        # Share array references between sectors
        # This must be done after all sectors have created their arrays
        self._share_arrays()

    def set_table_functions(self, json_file: Path | None = None) -> None:
        """Load nonlinear table functions for all sectors"""
        self.pop.set_table_functions(json_file)
        self.cap.set_table_functions(json_file)
        self.agr.set_table_functions(json_file)
        self.pol.set_table_functions(json_file)
        self.res.set_table_functions(json_file)

    def set_delay_functions(self, method: Literal["euler", "odeint"] = "euler") -> None:
        """Initialize delay functions for all sectors"""
        self.pop.set_delay_functions(method)
        self.cap.set_delay_functions(method)
        self.agr.set_delay_functions(method)
        self.pol.set_delay_functions(method)
        self.res.set_delay_functions(method)
        self._initialized = True

    def _ensure_initialized(self) -> None:
        """Initialize model with default values if not already initialized."""
        if not self._initialized:
            self.init_constants()
            self.init_variables()
            self.set_table_functions()
            self.set_delay_functions()

    def run(self) -> None:
        """
        Run the World3 simulation.

        If the model has not been initialized, it will be initialized with default
        values automatically. For custom parameters, call init_constants() before run().

        All circular dependencies have been completely resolved through careful
        ordering of calculations. Each time step requires exactly ONE pass through
        _update_step() with no iterations needed.

        Circular dependencies resolved by splitting sectors into phases:
        1. Resource Part 1 → Capital Part 1: FCAOR for IO calculation
        2. Capital Part 1 → Agriculture: IO, IOPC for lymap calculation
        3. Pollution Part 1 → Agriculture: PPOLX for lfdr calculation
        4. Agriculture → Capital Part 2: FIOAA for FIOAI calculation
        5. Agriculture → Pollution Part 2: AIPH, AL for PPGA calculation

        Within each sector, variables are calculated in strict dependency order.
        """
        # Auto-initialize with defaults if not already initialized
        self._ensure_initialized()

        # Initialize (k=0)
        self._init_step()

        # Main loop - NO ITERATIONS NEEDED
        # All circular dependencies resolved by proper sector ordering
        for k in range(1, self.n):
            self._update_step(k - 1, k, k - 1, k)

            if self.verbose and k % 100 == 0:
                print(f"Step {k}/{self.n}")

    def _init_step(self) -> None:
        """
        Initialize all sectors at t=0 (loop0).

        Executes in dependency order with minimal iterations to resolve
        internal circular dependencies within sectors (e.g., Agriculture's
        ly->f->fioaa->tai->ly cycle).

        Order: Population → Resource Phase 1 → Capital Phase 1 → Resource Phase 2 →
               Pollution Phase 1 → Agriculture → Pollution Phase 2 →
               Capital Phase 2 → Population Phase 2

        Arrays are already shared via _share_arrays(), so no manual value passing needed.
        """
        # Pass policy years to all sectors (needed before any initialization)
        self._pass_policy_years()

        # Multi-phase initialization to break circular dependencies
        # Phase 1: Initialize basic variables (pop, fcaor)
        self._loop0_population_phase1()
        self._loop0_resource_phase1()  # fcaor for Capital (before iopc is available)

        # Phase 2: Capital Phase 1 calculates IO, IOPC
        self._loop0_capital_phase1()

        # Phase 3: Resource Phase 2 needs IOPC for pcrum/nrur
        self._loop0_resource_phase2()

        # Phase 4: Pollution Phase 1 - ppolx for Agriculture (before aiph/al available)
        self._loop0_pollution_phase1()

        # Phase 5: Agriculture needs pop, io, iopc from Phase 1-2 and ppolx from Pollution
        self._loop0_agriculture()

        # Phase 6: Pollution Phase 2 - ppga, ppgr need aiph, al from Agriculture
        self._loop0_pollution_phase2()

        # Phase 7: Capital Phase 2 needs fioaa from Agriculture
        self._loop0_capital_phase2()  # Calculate Job subsector, ICIR, FIOAI

        # Phase 8: Complete Population using fpc from Agriculture
        self._loop0_population_phase2()

    def _loop0_population_phase1(self) -> None:
        """Initialize population sector Phase 1 - basic state (provides pop[0])"""
        k = 0

        # Set initial state variables
        self.pop.p1[0] = self.pop.constants.p1i
        self.pop.p2[0] = self.pop.constants.p2i
        self.pop.p3[0] = self.pop.constants.p3i
        self.pop.p4[0] = self.pop.constants.p4i
        self.pop.frsn[0] = 0.82
        self.pop.pop[0] = self.pop.p1[0] + self.pop.p2[0] + self.pop.p3[0] + self.pop.p4[0]

    def _loop0_population_phase2(self) -> None:
        """Initialize population sector Phase 2 - complete (uses fpc[0] from Agriculture)"""
        k = 0

        # Death rate subsector (needs fpc[0])
        self.pop.update_fpu(k)
        self.pop.update_lmp(k)
        self.pop.update_lmf(k)  # Uses fpc[0]
        self.pop.update_cmi(k)
        self.pop.update_hsapc(k)
        self.pop.update_ehspc(k)
        self.pop.update_lmhs(k)
        self.pop.update_lmc(k)
        self.pop.update_le(k)
        self.pop.update_m1(k)
        self.pop.update_m2(k)
        self.pop.update_m3(k)
        self.pop.update_m4(k)
        self.pop.update_mat1(k, k)
        self.pop.update_mat2(k, k)
        self.pop.update_mat3(k, k)
        self.pop.update_d1(k, k)
        self.pop.update_d2(k, k)
        self.pop.update_d3(k, k)
        self.pop.update_d4(k, k)
        self.pop.update_d(k, k)
        self.pop.update_cdr(k)

        # Birth rate subsector
        self.pop.update_aiopc(k)
        self.pop.update_diopc(k)
        self.pop.update_fie(k)
        self.pop.update_sfsn(k)
        self.pop.update_frsn(k)
        self.pop.update_dcfs(k)
        self.pop.update_ple(k)
        self.pop.update_cmple(k)
        self.pop.update_dtf(k)
        self.pop.update_fm(k)
        self.pop.update_mtf(k)
        self.pop.update_nfc(k)
        self.pop.update_fsafc(k)
        self.pop.update_fcapc(k)
        self.pop.update_fcfpc(k)
        self.pop.update_fce(k)
        self.pop.update_tf(k)
        self.pop.update_b(k, k)  # b must be before cbr
        self.pop.update_cbr(k, k)  # cbr depends on b

        # Recompute supplementary initial conditions
        self.pop.update_frsn(k)

        # 2004 update added
        self.pop.update_lei(k)
        self.pop.update_gdpc(k)
        self.pop.update_gdpi(k)
        self.pop.update_ei(k)
        self.pop.update_hwi(k)

    def _loop0_capital_phase1(self) -> None:
        """
        Initialize capital sector Phase 1 (loop0).

        Calculate IO, IOPC and service sector variables.
        Does NOT calculate FIOAI or ICIR yet (they need FIOAA from Agriculture).
        """
        k = 0

        # Set initial state variables BEFORE any updates (from PyWorld3-03 pattern)
        self.cap.ic[0] = self.cap.constants.ici
        self.cap.sc[0] = self.cap.constants.sci

        # IMPORTANT: Set initial CUF to 1.0 for bootstrapping
        # Without this, IO calculation will fail with nan
        self.cap.cuf[0] = 1.0

        # Industrial subsector (partial - without FIOAI/ICIR)
        self.cap.update_alic(k)
        self.cap.update_icdr(k, k)
        self.cap.update_icor(k)
        self.cap.update_io(k)  # Uses CUF[0] = 1.0 initially
        self.cap.update_iopc(k)
        self.cap.update_fioac(k)

        # 2004 update added
        self.cap.update_cio(k)
        self.cap.update_ciopc(k)

        # Service subsector
        self.cap.update_isopc(k)
        self.cap.update_alsc(k)
        self.cap.update_scdr(k, k)
        self.cap.update_scor(k)
        self.cap.update_so(k)
        self.cap.update_sopc(k)
        self.cap.update_fioas(k)
        self.cap.update_scir(k, k)

        # NOTE: Job subsector moved to Phase 2 because JPH needs AIPH from Agriculture

    def _loop0_capital_phase2(self) -> None:
        """
        Initialize capital sector Phase 2 (loop0).

        Calculate Job subsector, FIOAI and ICIR which depend on Agriculture.
        This must be called AFTER Agriculture initialization.
        """
        k = 0

        # Job subsector - needs AIPH, AL from Agriculture
        self.cap.update_jpicu(k)
        self.cap.update_pjis(k)
        self.cap.update_jpscu(k)
        self.cap.update_pjss(k)
        self.cap.update_jph(k)  # Needs AIPH from Agriculture
        self.cap.update_pjas(k)  # Needs JPH, AL from Agriculture
        self.cap.update_j(k)
        self.cap.update_lf(k)
        self.cap.update_luf(k)
        self.cap.update_lufd(k)
        self.cap.update_cuf(k)  # Recalculate CUF with actual LUFD value

        # Industrial subsector - variables that depend on Agriculture
        self.cap.update_fioai(k)  # Needs FIOAA from Agriculture
        self.cap.update_icir(k, k)

    def _loop0_agriculture(self) -> None:
        """Initialize agriculture sector (loop0) - optimized order"""
        k = 0

        # Set initial state variables BEFORE any updates
        self.agr.al[0] = self.agr.constants.ali
        self.agr.pal[0] = self.agr.constants.pali
        self.agr.uil[0] = self.agr.constants.uili
        self.agr.lfert[0] = self.agr.constants.lferti
        self.agr.ai[0] = 5e9
        self.agr.pfr[0] = 1
        self.agr.yt[0] = 1
        self.agr.ytcr[0] = 0

        # Calculate LY dependencies first (aiph, lymc, lyf, lymap needed for ly)
        self.agr.update_falm(k)  # Uses pfr[0] (already set)
        self.agr.update_aiph(k)  # Uses ai[0], falm[0], al[0]
        self.agr.update_lymc(k)  # Uses aiph[0]
        self.agr.update_lyf(k)  # Uses io[0]/io70
        self.agr.update_lymap(k)  # Uses io[0]/io70
        self.agr.update_lyf2(k)  # 2004 update

        # Calculate LFDR before LFD (lfdr depends on ppolx, lfd depends on lfdr)
        self.agr.update_lfdr(k)  # Uses ppolx[0] (from Pollution)
        self.agr.update_lfd(k, k)  # Uses lfert[0], lfdr[0]

        # Calculate LY now that dependencies are ready
        self.agr.update_ly(k)  # Uses lyf[0], lfert[0], lymc[0], lymap[0]

        # Now calculate F which depends on LY
        self.agr.update_lfc(k)  # Uses al[0]
        self.agr.update_f(k)  # Uses ly[0], al[0]
        self.agr.update_fpc(k)  # Uses f[0], pop[0]

        # Continue with remaining variables
        self.agr.update_ifpc(k)
        self.agr.update_fioaa(k)
        self.agr.update_tai(k)
        self.agr.update_dcph(k)

        # Loop 1&2 - investment allocation
        self.agr.update_mlymc(k)
        self.agr.update_alai(k)  # Must calculate alai BEFORE mpai (mpai depends on alai)
        self.agr.update_mpai(k)
        self.agr.update_mpld(k)
        self.agr.update_fiald(k)
        self.agr.update_ldr(k, k)

        # Loop 2 - agricultural inputs
        self.agr.update_cai(k)
        self.agr.update_aic(k)

        # Loop 6 - food ratio
        self.agr.update_fr(k)
        self.agr.update_cpfr(k)

        # Loop 4 - fertility degradation (lfdr already calculated earlier, lfd too)
        # (lfdr and lfd moved to line 505-506 to fix dependency order)

        # Loop 3 - land erosion (llmy must be calculated BEFORE all)
        self.agr.update_llmy(k)  # Uses ly[k]
        self.agr.update_all(k)  # Uses llmy[k]
        self.agr.update_ler(k, k)  # Uses al[k], all[k]
        self.agr.update_uilpc(k)
        self.agr.update_uilr(k)
        self.agr.update_lrui(k, k)

        # Loop 5 - fertility regeneration (lfrt must be calculated BEFORE lfr)
        self.agr.update_lfrt(k)  # Calculate lfrt[k] first
        self.agr.update_lfr(k, k)  # Then calculate lfr[k] using lfrt[k]

        # 2004 update - yield tech
        self.agr.update_frd(k)
        self.agr.update_ytcm(k)
        self.agr.update_ytcr(k, k)

    def _loop0_pollution_phase1(self) -> None:
        """
        Initialize pollution sector Phase 1 - provides PPOLX for Agriculture.

        Must run BEFORE _loop0_agriculture() because Agriculture needs ppolx for lfdr.
        """
        k = 0

        # Set initial state variables BEFORE any updates (from PyWorld3-03 pattern)
        self.pol.pp[0] = self.pol.constants.pp19
        self.pol.ppt[0] = 1

        self.pol.update_pcrum(k)
        self.pol.update_ppolx(k)  # Needed by Agriculture for lfdr

    def _loop0_pollution_phase2(self) -> None:
        """
        Initialize pollution sector Phase 2 - calculates PPGA, PPGR, PPASR.

        Must run AFTER _loop0_agriculture() because PPGA needs AIPH, AL from Agriculture.
        """
        k = 0

        self.pol.update_ppgi(k)
        self.pol.update_ppga(k)  # Needs AIPH, AL from Agriculture
        self.pol.update_ppgf(k)
        self.pol.update_ppgr(k)  # Needs PPGA
        self.pol.update_ppar(k)
        self.pol.update_ahlm(k)
        self.pol.update_ahl(k)
        self.pol.update_ppasr(k)

        # 2004 update added
        self.pol.update_pptc(k)
        self.pol.update_pptcm(k)
        self.pol.update_pptcr(k, k)
        self.pol.update_ppgf2(k)
        self.pol.update_pptmi(k)
        self.pol.update_pii(k)
        self.pol.update_fio70(k)
        self.pol.update_ymap1(k)
        self.pol.update_ymap2(k)
        self.pol.update_apfay(k)
        self.pol.update_abl(k)
        self.pol.update_ef(k)

    def _loop0_resource_phase1(self) -> None:
        """
        Initialize resource sector Phase 1 - provides FCAOR for Capital.

        Must run BEFORE _loop0_capital_phase1().
        """
        k = 0

        # Set initial state variables BEFORE any updates (from PyWorld3-03 pattern)
        self.res.nr[0] = self.res.constants.nri
        self.res.rt[0] = 1

        self.res.update_nrfr(k)
        # Calculate FCAOR1 and FCAOR2 before FCAOR (needed by Capital for IO calculation)
        self.res.update_fcaor1(k)
        self.res.update_fcaor2(k)
        self.res.update_fcaor(k)

    def _loop0_resource_phase2(self) -> None:
        """
        Initialize resource sector Phase 2 - calculates PCRUM and NRUR.

        Must run AFTER _loop0_capital_phase1() because PCRUM needs IOPC.
        """
        k = 0

        # 2004 update added
        self.res.update_rtc(k)
        self.res.update_rtcm(k)
        self.res.update_rtcr(k, k)
        self.res.update_nruf2(k)
        self.res.update_nruf(k)
        self.res.update_pcrum(k)  # Needs IOPC from Capital Phase 1
        self.res.update_nrur(k, k)  # Needs POP, PCRUM, NRUF

    def _update_step(self, j: int, k: int, jk: int, kl: int) -> None:
        """
        Update all sectors for one time step (single iteration).

        Sector order is carefully arranged to break all circular dependencies:
        1. Resource Part 1 - provides FCAOR for Capital
        2. Population Part 1 - calculates POP for Agriculture/Capital
        3. Capital Part 1 - calculates IO, IOPC (needed by Agriculture for lymap)
        4. Pollution Part 1 - calculates PP state, PPOLX (needed by Agriculture for lfdr)
        5. Agriculture - provides FPC for Population Part 2 and FIOAA for Capital Part 2
        6. Population Part 2 - calculates flow variables (B, D, MAT) using FPC
        7. Capital Part 2 - calculates FIOAI, ICIR, FIOAC (needs FIOAA from Agriculture)
        8. Resource Part 2 - calculates PCRUM, NRUR (needs IOPC from Capital)
        9. Pollution Part 2 - calculates PPGI, PPGA, PPAR, PPASR (needs AIPH, AL)

        Note: Array references are shared via _share_arrays(), so no manual variable
        passing is needed. Updates in one sector are automatically visible in others.
        """

        # Phase 1: Resource and Population basics
        self._loopk_resource_part1(j, k, jk, kl)
        self._loopk_population_part1(j, k, jk, kl)

        # Phase 2: Capital Part 1 (IO, IOPC - needed by Agriculture for lymap)
        self._loopk_capital_part1(j, k, jk, kl)

        # Phase 3: Pollution Part 1 (PP state, PPOLX - needed by Agriculture for lfdr)
        self._loopk_pollution_part1(j, k, jk, kl)

        # Phase 4: Agriculture (can now calculate all variables with IO and PPOLX)
        self._loopk_agriculture(j, k, jk, kl)

        # Phase 5: Complete Population with FPC from Agriculture
        self._loopk_population_part2(j, k, jk, kl)

        # Phase 6: Complete Capital with FIOAA from Agriculture
        self._loopk_capital_part2(j, k, jk, kl)

        # Phase 7: Complete Resource with IOPC from Capital
        self._loopk_resource_part2(j, k, jk, kl)

        # Phase 8: Complete Pollution with AIPH, AL from Agriculture
        self._loopk_pollution_part2(j, k, jk, kl)

    def _loopk_population_part1(self, j: int, k: int, jk: int, kl: int) -> None:
        """
        Update population sector Part 1 - before Agriculture.

        This part calculates POP which is needed by Agriculture and Capital.
        Flow variables (births, deaths, maturation) are calculated in Part 2
        after Agriculture provides FPC.
        """
        # State updates (uses flow variables from previous step)
        self.pop.update_state_p1(k, j, jk)
        self.pop.update_state_p2(k, j, jk)
        self.pop.update_state_p3(k, j, jk)
        self.pop.update_state_p4(k, j, jk)
        self.pop.update_pop(k)

    def _loopk_population_part2(self, j: int, k: int, jk: int, kl: int) -> None:
        """
        Update population sector Part 2 - after Agriculture.

        This part calculates flow variables (births, deaths, maturation)
        which depend on FPC from Agriculture.
        """
        # Death rate subsector (needs FPC from Agriculture)
        self.pop.update_fpu(k)
        self.pop.update_lmp(k)
        self.pop.update_lmf(k)  # Needs FPC
        self.pop.update_cmi(k)
        self.pop.update_hsapc(k)
        self.pop.update_ehspc(k)
        self.pop.update_lmhs(k)
        self.pop.update_lmc(k)
        self.pop.update_le(k)
        self.pop.update_m1(k)
        self.pop.update_m2(k)
        self.pop.update_m3(k)
        self.pop.update_m4(k)
        self.pop.update_mat1(k, kl)
        self.pop.update_mat2(k, kl)
        self.pop.update_mat3(k, kl)
        self.pop.update_d1(k, kl)
        self.pop.update_d2(k, kl)
        self.pop.update_d3(k, kl)
        self.pop.update_d4(k, kl)
        self.pop.update_d(k, jk)
        self.pop.update_cdr(k)

        # Birth rate subsector (needs FPC through FIE)
        self.pop.update_aiopc(k)
        self.pop.update_diopc(k)
        self.pop.update_fie(k)
        self.pop.update_sfsn(k)
        self.pop.update_frsn(k)
        self.pop.update_dcfs(k)
        self.pop.update_ple(k)
        self.pop.update_cmple(k)
        self.pop.update_dtf(k)
        self.pop.update_fm(k)
        self.pop.update_mtf(k)
        self.pop.update_nfc(k)
        self.pop.update_fsafc(k)
        self.pop.update_fcapc(k)
        self.pop.update_fcfpc(k)
        self.pop.update_fce(k)
        self.pop.update_tf(k)
        self.pop.update_b(k, kl)  # b must be before cbr
        self.pop.update_cbr(k, jk)  # cbr depends on b

        # 2004 update added
        self.pop.update_lei(k)
        self.pop.update_gdpc(k)
        self.pop.update_gdpi(k)
        self.pop.update_ei(k)
        self.pop.update_hwi(k)

    def _loopk_capital_part1(self, j: int, k: int, jk: int, kl: int) -> None:
        """
        Update capital sector Part 1 - before Agriculture.

        This part calculates Service sector, IO, IOPC, and FIOAC.
        IO does NOT depend on FIOAA, so it can be calculated here.
        FIOAC also calculated here as it only needs IOPC.
        """
        # Job subsector
        self.cap.update_lufd(k)
        self.cap.update_cuf(k)
        # Industrial subsector (state and basic variables)
        self.cap.update_state_ic(k, j, jk)
        self.cap.update_alic(k)
        self.cap.update_icdr(k, kl)
        self.cap.update_icor(k)
        # CRITICAL: Calculate IO early (needed by Agriculture for lymap)
        # IO = IC * (1 - FCAOR) * CUF / ICOR - does NOT need FIOAA!
        self.cap.update_io(k)
        self.cap.update_iopc(k)
        # FIOAC only needs IOPC, calculate here for FIOAI later
        self.cap.update_fioac(k)
        # Service subsector
        self.cap.update_state_sc(k, j, jk)
        self.cap.update_isopc(k)
        self.cap.update_alsc(k)
        self.cap.update_scdr(k, kl)
        self.cap.update_scor(k)
        self.cap.update_so(k)
        self.cap.update_sopc(k)
        self.cap.update_fioas(k)
        self.cap.update_scir(k, kl)

    def _loopk_capital_part2(self, j: int, k: int, jk: int, kl: int) -> None:
        """
        Update capital sector Part 2 - after Agriculture.

        This part calculates Industrial variables that depend on
        Agriculture's FIOAA (FIOAI, ICIR).
        Note: IO, IOPC, FIOAC already calculated in Part 1.
        """
        # Industrial subsector - variables that depend on Agriculture
        self.cap.update_fioai(k)  # Needs FIOAA from Agriculture, FIOAS, FIOAC
        self.cap.update_icir(k, kl)
        # 2004 update added
        self.cap.update_cio(k)
        self.cap.update_ciopc(k)
        # Job subsector - final calculations
        self.cap.update_jpicu(k)
        self.cap.update_pjis(k)
        self.cap.update_jpscu(k)
        self.cap.update_pjss(k)
        self.cap.update_jph(k)
        self.cap.update_pjas(k)
        self.cap.update_j(k)
        self.cap.update_lf(k)
        self.cap.update_luf(k)

    def _loopk_agriculture(self, j: int, k: int, jk: int, kl: int) -> None:
        """
        Update agriculture sector for one time step - optimized order.
        """
        # Update state variables first
        self.agr.update_state_al(k, j, jk)
        self.agr.update_state_pal(k, j, jk)
        self.agr.update_state_uil(k, j, jk)
        self.agr.update_state_lfert(k, j, jk)
        self.agr.update_state_ai(k, j, jk)
        self.agr.update_state_pfr(k, j, jk)
        self.agr.update_state_yt(k, j, jk)

        # Calculate LY dependencies first (needed before F)
        self.agr.update_falm(k)  # Uses pfr[k] (just updated)
        self.agr.update_aiph(k)  # Uses ai[k], falm[k], al[k]
        self.agr.update_lymc(k)  # Uses aiph[k]
        self.agr.update_lyf(k)  # Uses io[k]/io70
        self.agr.update_lymap(k)  # Uses io[k]/io70
        self.agr.update_lyf2(k)  # 2004 update, uses yt[k]

        # Calculate LY now
        self.agr.update_lfdr(k)  # Uses aiph[k]
        self.agr.update_lfd(k, kl)  # Uses lfert[k], aiph[k]
        self.agr.update_ly(k)  # Uses lyf[k], lfert[k], lymc[k], lymap[k]

        # Now calculate F which depends on LY
        self.agr.update_lfc(k)  # Uses al[k]
        self.agr.update_f(k)  # Uses ly[k], al[k]
        self.agr.update_fpc(k)  # Uses f[k], pop[k]

        # Continue with food-dependent variables
        self.agr.update_fr(k)  # Uses fpc[k]
        self.agr.update_cpfr(k)  # Uses fr[k], pfr[k]
        self.agr.update_ifpc(k)  # Uses iopc[k]
        self.agr.update_fioaa(k)  # Uses fpc[k], ifpc[k]
        self.agr.update_tai(k)  # Uses io[k], fioaa[k]
        self.agr.update_dcph(k)  # Uses pal[k]

        # Investment allocation (alai MUST be calculated BEFORE mpai)
        self.agr.update_mlymc(k)  # Uses aiph[k]
        self.agr.update_alai(k)  # Policy-based, must be before mpai
        self.agr.update_mpai(k)  # Uses alai[k], ly[k], mlymc[k], lymc[k]
        self.agr.update_mpld(k)  # Uses tai[k], pal[k], dcph[k]
        self.agr.update_fiald(k)  # Uses mpld[k], mpai[k]
        self.agr.update_ldr(k, kl)  # Uses tai[k], fiald[k], dcph[k]

        # Agricultural inputs
        self.agr.update_cai(k)  # Uses tai[k], fiald[k]
        self.agr.update_aic(k)  # Uses cai[k], ai[k], alai[k]

        # Land erosion (llmy must be calculated BEFORE all)
        self.agr.update_llmy(k)  # Uses ly[k]
        self.agr.update_all(k)  # Uses llmy[k]
        self.agr.update_ler(k, kl)  # Uses al[k], all[k]
        self.agr.update_uilpc(k)  # Uses iopc[k]
        self.agr.update_uilr(k)  # Uses pop[k], uilpc[k]
        self.agr.update_lrui(k, kl)  # Uses uilr[k], uil[k]

        # Fertility regeneration (lfrt MUST be calculated BEFORE lfr)
        self.agr.update_lfrt(k)  # Uses pfr[k]
        self.agr.update_lfr(k, kl)  # Uses lfert[k], lfrt[k], ilf

        # Yield tech (2004 update)
        self.agr.update_frd(k)  # Uses fr[k]
        self.agr.update_ytcm(k)  # Uses frd[k]
        self.agr.update_ytcr(k, j)  # Uses ytcm[k], yt[j]

    def _loopk_pollution_part1(self, j: int, k: int, jk: int, kl: int) -> None:
        """
        Update pollution sector Part 1 - PP state and PPOLX.

        Must run BEFORE Agriculture to provide PPOLX for lfdr calculation.
        Only depends on previous time step's PPAR and PPASR.
        """
        # State update (uses PPAR and PPASR from previous step)
        self.pol.update_state_pp(k, j, jk)
        self.pol.update_ppolx(k)

    def _loopk_pollution_part2(self, j: int, k: int, jk: int, kl: int) -> None:
        """
        Update pollution sector Part 2 - generation and absorption.

        Must run AFTER Agriculture because PPGA needs AIPH, AL.
        """
        # PCRUM update (uses IOPC from Capital)
        self.pol.update_pcrum(k)

        # Pollution generation (needs AIPH, AL from Agriculture)
        self.pol.update_ppgi(k)  # Uses PCRUM
        self.pol.update_ppga(k)  # Uses AIPH, AL
        self.pol.update_ppgf(k)
        self.pol.update_ppgr(k)
        self.pol.update_ppar(k)

        # Pollution absorption
        self.pol.update_ahlm(k)
        self.pol.update_ahl(k)
        self.pol.update_ppasr(k)

        # 2004 update - pollution technology
        self.pol.update_pptc(k)
        self.pol.update_pptcm(k)
        self.pol.update_pptcr(k, kl)
        self.pol.update_state_ppt(k, j, jk)
        self.pol.update_ppgf2(k)

        # 2004 update - other variables
        self.pol.update_pptmi(k)
        self.pol.update_pii(k)
        self.pol.update_fio70(k)
        self.pol.update_ymap1(k)
        self.pol.update_ymap2(k)
        self.pol.update_apfay(k)
        self.pol.update_abl(k)
        self.pol.update_ef(k)

    def _loopk_resource_part1(self, j: int, k: int, jk: int, kl: int) -> None:
        """
        Update resource sector Part 1 - state and FCAOR.

        Must run BEFORE Capital to provide FCAOR.
        """
        self.res.update_state_nr(k, j, jk)
        self.res.update_nrfr(k)
        self.res.update_fcaor1(k)
        self.res.update_fcaor2(k)
        self.res.update_fcaor(k)

    def _loopk_resource_part2(self, j: int, k: int, jk: int, kl: int) -> None:
        """
        Update resource sector Part 2 - PCRUM and NRUR.

        Must run AFTER Capital Part 2 because PCRUM needs IOPC.
        """
        # 2004 update added
        self.res.update_rtc(k)
        self.res.update_rtcm(k)
        self.res.update_rtcr(k, kl)
        self.res.update_state_rt(k, j, jk)  # CRITICAL: Must update RT state before NRUF2
        self.res.update_nruf2(k)
        self.res.update_nruf(k)
        self.res.update_pcrum(k)  # Needs IOPC from Capital Part 2
        self.res.update_nrur(k, kl)  # Needs POP, PCRUM, NRUF

    def _pass_policy_years(self) -> None:
        """
        Pass policy years and time arrays to all sectors.

        This should be called once before initialization to set up global configuration.
        """
        # Pass policy years to all sectors
        # These control when policy changes are implemented
        self.pop.pyear = self.config.pyear
        self.cap.pyear = self.config.pyear
        self.agr.pyear = self.config.pyear
        self.pol.pyear = self.config.pyear
        self.res.pyear = self.config.pyear

        # Pass sector-specific policy years
        self.res.pyear_res_tech = self.config.pyear_res_tech
        self.res.pyear_fcaor = self.config.pyear_fcaor
        self.pol.pyear_pp_tech = self.config.pyear_pp_tech
        self.agr.pyear_y_tech = self.config.pyear_y_tech

        # Pass iphst (health services implementation year)
        self.pop.iphst = self.config.iphst

        # Pass time arrays (shared across all sectors)
        self.pop.time = self.time
        self.cap.time = self.time
        self.agr.time = self.time
        self.pol.time = self.time
        self.res.time = self.time

    def _share_arrays(self) -> None:
        """
        Share array references between sectors to avoid copying.

        This is called once during initialization to set up inter-sector connections.
        Instead of copying values between sectors at each time step, we share
        the actual array references (similar to PyWorld3-03's multiple inheritance).
        """
        # Population outputs → other sectors (read by Capital, Agriculture, Resource, Pollution)
        self.cap.pop = self.pop.pop
        self.cap.p2 = self.pop.p2
        self.cap.p3 = self.pop.p3
        self.agr.pop = self.pop.pop
        self.pol.pop = self.pop.pop
        self.res.pop = self.pop.pop

        # Capital outputs → other sectors
        self.pop.io = self.cap.io
        self.pop.iopc = self.cap.iopc
        self.pop.so = self.cap.so
        self.pop.sopc = self.cap.sopc
        self.agr.io = self.cap.io
        self.agr.iopc = self.cap.iopc
        self.pol.io = self.cap.io
        self.pol.iopc = self.cap.iopc
        self.res.iopc = self.cap.iopc

        # Agriculture outputs → other sectors
        self.pop.f = self.agr.f
        self.pop.fpc = self.agr.fpc
        self.cap.fioaa = self.agr.fioaa
        self.cap.aiph = self.agr.aiph
        self.cap.al = self.agr.al
        self.pol.aiph = self.agr.aiph
        self.pol.al = self.agr.al
        self.pol.uil = self.agr.uil

        # Pollution outputs → other sectors
        self.pop.ppolx = self.pol.ppolx
        self.agr.ppolx = self.pol.ppolx

        # Resource outputs → other sectors
        self.cap.fcaor = self.res.fcaor
        self.cap.nrfr = self.res.nrfr

    def get_results(self) -> dict[str, npt.NDArray[np.float64]]:
        """
        Get key results from the simulation.

        Returns:
            Dictionary with time series of key variables
        """
        return {
            "time": self.time,
            # Population
            "pop": self.pop.pop,
            "le": self.pop.le,
            "cbr": self.pop.cbr,
            "cdr": self.pop.cdr,
            "hwi": self.pop.hwi,
            # Capital
            "iopc": self.cap.iopc,
            "sopc": self.cap.sopc,
            # Agriculture
            "fpc": self.agr.fpc,
            # Pollution
            "ppolx": self.pol.ppolx,
            # Resources
            "nrfr": self.res.nrfr,
        }


def hello_world3() -> None:
    """
    Run a standard "Business as Usual" scenario and display results.

    This is the classic reference run from Limits to Growth.
    """
    import matplotlib.pyplot as plt

    print("Running World3 standard scenario...")

    # Create and configure model
    config = World3Config(year_min=1900, year_max=2100, dt=0.5)
    world3 = World3(config)

    # Initialize
    world3.init_constants()
    world3.init_variables()
    world3.set_table_functions()
    world3.set_delay_functions()

    # Run simulation
    world3.run()

    print("Simulation complete!")

    # Get results
    results = world3.get_results()

    # Plot key variables
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle("World3 Standard Run", fontsize=16)

    # Plot configurations
    plots = [
        ("pop", "Population", [0, 12e9]),
        ("iopc", "Industrial Output per Capita", [0, 1000]),
        ("fpc", "Food per Capita", [0, 1000]),
        ("ppolx", "Pollution Index", [0, 40]),
        ("nrfr", "Resource Fraction Remaining", [0, 1]),
        ("hwi", "Human Welfare Index", [0, 1]),
    ]

    for ax, (var, title, ylim) in zip(axes.flat, plots):
        ax.plot(results["time"], results[var], linewidth=2)
        ax.set_xlabel("Year")
        ax.set_title(title)
        ax.set_ylim(ylim)
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()

    print("\nKey results at year 2100:")
    print(f"  Population: {results['pop'][-1]:.2e}")
    print(f"  IOPC: {results['iopc'][-1]:.2f}")
    print(f"  FPC: {results['fpc'][-1]:.2f}")
    print(f"  Pollution Index: {results['ppolx'][-1]:.2f}")
    print(f"  Resources Remaining: {results['nrfr'][-1]:.2%}")
    print(f"  Human Welfare Index: {results['hwi'][-1]:.3f}")
