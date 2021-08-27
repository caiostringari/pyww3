"""
Abstracts the ww3_ounf program.
"""
import os

import datetime

from typing import List

from dataclasses import dataclass, field
from textwrap import dedent as dtxt

from .utils import (run, bool_to_str, verify_runpath, verify_mod_def,
                    verify_ww3_out)

from .namelists import remove_namelist_block, add_namelist_block


@dataclass
class WW3Ounf:

    # withoput these two parameters, everything breaks
    runpath: str
    mod_def: str

    EXE = "ww3_ounf"
    DATE_FORMAT = "%Y%m%d %H%M%S"
    ww3_grd: str = "out_grd.ww3"
    output: str = "ww3_ounf.nml"

    # default parameters dictionary
    field_timestart: datetime.datetime = datetime.datetime(1900, 1, 1)
    field_timestride: int = 0
    field_timecount: int = 1000000000
    field_timesplit: int = 6
    field_list: List[str] = field(default_factory=lambda: ["HS", "FP", "DIR", "SPR", "WND" "ICE"])
    field_samefile: bool = True
    field_partition: List[int] = field(default_factory=lambda: [0, 1, 2, 3])
    field_type: int = 3

    file_prefix: str = "ww3."
    file_netcdf: int = 4
    file_ix0: int = 1
    file_ixn: int = 1000000000
    file_iy0: int = 1
    file_iyn: int = 1000000000

    smc_type: int = 1
    smc_sxo: int = 0
    smc_exo: int = 0
    smc_syo: int = 0
    smc_eyo: int = 0
    smc_celfac: int = 1
    smc_noval: int = -999

    def __post_init__(self):
        """Validate the class initialization"""

        # verify if all files are valid
        verify_runpath(self.runpath)
        verify_mod_def(self.runpath, self.mod_def)
        verify_ww3_out(self.runpath, self.ww3_grd)

        # update date to match the simulation date
        self.__setattr__("field_timestart", self.field_timestart)

        # create the namelist text here
        self.__setattr__("text", self.populate_namelist())

    # NOTE: I am doing this this way instead of reading it from a file
    # because f-strings in a file allow for arbitrary code execution,
    # and are thefore a security issue. Writting everything here at
    # least controls what is being executed.
    def populate_namelist(self):
        """Create the namelist text using NOAA's latest template."""
        txt = dtxt(f"""\
                    ! -------------------------------------------------------------------- !
                    ! WAVEWATCH III - ww3_ounf.nml - Grid output post-processing           !
                    ! -------------------------------------------------------------------- !

                    ! -------------------------------------------------------------------- !
                    ! Define the output fields to postprocess via FIELD_NML namelist
                    !
                    ! * the detailed list of field names FIELD%LIST is given in ww3_shel.nml
                    !  DPT CUR WND AST WLV ICE IBG D50 IC1 IC5
                    !  HS LM T02 T0M1 T01 FP DIR SPR DP HIG
                    !  EF TH1M STH1M TH2M STH2M WN
                    !  PHS PTP PLP PDIR PSPR PWS PDP PQP PPE PGW PSW PTM10 PT01 PT02 PEP TWS PNR
                    !  UST CHA CGE FAW TAW TWA WCC WCF WCH WCM FWS
                    !  SXY TWO BHD FOC TUS USS P2S USF P2L TWI FIC
                    !  ABR UBR BED FBB TBB
                    !  MSS MSC WL02 AXT AYT AXY
                    !  DTD FC CFX CFD CFK
                    !  U1 U2
                    !
                    ! * namelist must be terminated with /
                    ! * definitions & defaults:

                    ! Stop date for the output field
                    !     FIELD%TIMESTART            = '19000101 000000'

                    ! Time stride for the output field
                    !     FIELD%TIMESTRIDE           = '0'

                    ! Number of time steps
                    !     FIELD%TIMECOUNT            = '1000000000'

                    ! [4(yearly),6(monthly),8(daily),10(hourly)]
                    !     FIELD%TIMESPLIT            = 6

                    ! List of output fields
                    !     FIELD%LIST                 = 'unset'

                    ! List of wave partitions ['0 1 2 3 4 5']
                    !     FIELD%PARTITION            = '0 1 2 3'

                    ! All the variables in the same file
                    !     FIELD%SAMEFILE             = T

                    ! [2 = SHORT, 3 = it depends , 4 = REAL]
                    !     FIELD%TYPE                 = 3
                    ! -------------------------------------------------------------------- !
                    &FIELD_NML
                      FIELD%TIMESTART = '{self.field_timestart.strftime(self.DATE_FORMAT)}'
                      FIELD%TIMESTRIDE = '{self.field_timestride}'
                      FIELD%TIMECOUNT = '{self.field_timecount}'
                      FIELD%TIMESPLIT = {self.field_timesplit}
                      FIELD%LIST = '{" ".join(self.field_list)}'
                      FIELD%SAMEFILE = {bool_to_str(self.field_samefile).upper()}
                      FIELD%PARTITION = '{" ".join(str(x) for x in self.field_partition)}'
                      FIELD%TYPE = {self.field_type}
                    /


                    ! -------------------------------------------------------------------- !
                    ! Define the content of the output file via FILE_NML namelist
                    !
                    ! * namelist must be terminated with /
                    ! * definitions & defaults:
                    !     FILE%PREFIX        = 'ww3.'            ! Prefix for output file name
                    !     FILE%NETCDF        = 3                 ! Netcdf version [3|4]
                    !     FILE%IX0           = 1                 ! First X-axis or node index
                    !     FILE%IXN           = 1000000000        ! Last X-axis or node index
                    !     FILE%IY0           = 1                 ! First Y-axis index
                    !     FILE%IYN           = 1000000000        ! Last Y-axis index
                    ! -------------------------------------------------------------------- !
                    &FILE_NML
                      FILE%PREFIX = '{self.file_prefix}'
                      FILE%NETCDF = {self.file_netcdf}
                      FILE%IX0 = {self.file_ix0}
                      FILE%IXN = {self.file_ixn}
                      FILE%IY0 = {self.file_iy0}
                      FILE%IYN = {self.file_iyn}
                    /

                    ! -------------------------------------------------------------------- !
                    ! Define the content of the output file via SMC_NML namelist
                    !
                    ! * For SMC grids, IX0, IXN, IY0 and IYN from FILE_NML are not used.
                    !   Two types of output are available:
                    ! *   TYPE=1: Flat 1D "seapoint" array of grid cells.
                    ! *   TYPE=2: Re-gridded regular grid with cell sizes being an integer
                    ! *           multiple of the smallest SMC grid cells size.
                    !
                    ! * Note that the first/last longitudes and latitudes will be adjusted
                    !  to snap to the underlying SMC grid edges. CELFAC is only used for
                    !  type 2 output and defines the output cell sizes as an integer
                    !  multiple of the smallest SMC Grid cell size. CELFAC should be a
                    !  power of 2, e.g: 1,2,4,8,16, etc...
                    !
                    ! * namelist must be terminated with /
                    ! * definitions & defaults:
                    !     SMC%TYPE          = 1              ! SMC Grid type (1 or 2)
                    !     SMC%SXO           = -999.9         ! First longitude
                    !     SMC%EXO           = -999.9         ! Last longitude
                    !     SMC%SYO           = -999.9         ! First latitude
                    !     SMC%EYO           = -999.9         ! Last latitude
                    !     SMC%CELFAC        = 1              ! Cell size factor (SMCTYPE=2 only)
                    !     SMC%NOVAL         = UNDEF          ! Fill val. for wet cells without data
                    ! -------------------------------------------------------------------- !
                    &SMC_NML
                      SMC%TYPE = {self.smc_type}
                      SMC%SXO = {self.smc_sxo}
                      SMC%EXO = {self.smc_exo}
                      SMC%SYO = {self.smc_syo}
                      SMC%EYO = {self.smc_eyo}
                      SMC%CELFAC = {self.smc_celfac}
                      SMC%NOVAL = {self.smc_noval}
                    /

                    ! -------------------------------------------------------------------- !
                    ! WAVEWATCH III - end of namelist                                      !
                    ! -------------------------------------------------------------------- !""")
        return txt

    def to_file(self):
        """Write namelist text to file ww3_ounf.nml."""
        if os.path.isfile(os.path.join(self.runpath, self.output)):
            os.remove(os.path.join(self.runpath, self.output))
        with open(os.path.join(self.runpath, self.output), 'w') as f:
            f.write(self.text)

    def run(self):
        """Run the program ww3_ounf."""
        res = run(self.runpath, self.EXE)
        self.__setattr__("returncode", res.returncode)
        self.__setattr__("stdout", res.stdout)
        self.__setattr__("stderr", res.stderr)

    def update_text(self, block: str, action: str = "add", index: int = -1):
        """Update namelist block in the text with an action."""

        # add case
        if action.lower().startswith("a"):
            newtext = add_namelist_block(self.text, block, index)

        # remove case
        else:
            newtext = remove_namelist_block(self.text, block)

        # update class attribute
        self.__setattr__("text", newtext)
