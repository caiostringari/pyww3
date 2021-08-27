"""
Abstracts the ww3_shel program.
"""
import os

import datetime
# import shutil

from typing import List

from logging import warning
from dataclasses import dataclass, field
from textwrap import dedent as dtxt

from .utils import (mpirun, bool_to_str, verify_runpath, verify_mod_def)

from .namelists import remove_namelist_block, add_namelist_block


@dataclass
class WW3Shel:
    """
    Abstraction class for ww3_shel.
    """

    # withoput these two parameters, everything breaks
    runpath: str
    mod_def: str

    EXE = "ww3_shel"
    DATE_FORMAT = "%Y%m%d %H%M%S"
    output: str = "ww3_shel.nml"

    nproc: int = 1

    # namelist parameters start here
    domain_iostyp: int = 1

    domain_start: datetime.datetime = datetime.datetime(1900, 1, 1)
    domain_stop: datetime.datetime = datetime.datetime(2900, 12, 31)

    input_forcing_water_levels: bool = False
    input_forcing_currents: bool = False
    input_forcing_winds: bool = False
    input_forcing_ice_conc: bool = False
    input_forcing_ice_param1: bool = False
    input_forcing_ice_param2: bool = False
    input_forcing_ice_param3: bool = False
    input_forcing_ice_param4: bool = False
    input_forcing_ice_param5: bool = False
    input_forcing_mud_density: bool = False
    input_forcing_mud_thickness: bool = False
    input_forcing_mud_viscosity: bool = False
    input_assim_mean: bool = False
    input_assim_spec1d: bool = False
    input_assim_spec2d: bool = False

    type_field_list: List[str] = field(default_factory=lambda:
                                       ["DPT", "WND", "HS", "LM", "T02",
                                        "T0M1", "T01", "FP", "DIR", "SPR",
                                        "DP", "PHS", "PTP", "PLP", "PDIR",
                                        "PSPR", "PWS", "TWS", "PNR", "DW"])
    type_point_file: str = "mylist"
    type_track_format: bool = True
    type_partition_x0: int = 0
    type_partition_xn: int = 0
    type_partition_nx: int = 0
    type_partition_y0: int = 0
    type_partition_yn: int = 0
    type_partition_ny: int = 0
    type_partition_format = True
    type_coupling_sent: str = " "  # bug here?
    type_coupling_received: str = " "  # bug here?

    date_field_start: datetime.datetime = datetime.datetime(1900, 1, 1)
    date_field_stride: int = 0
    date_field_stop: datetime.datetime = datetime.datetime(2900, 12, 31)

    date_point_start: datetime.datetime = datetime.datetime(1900, 1, 1)
    date_point_stride: int = 0
    date_point_stop: datetime.datetime = datetime.datetime(2900, 12, 31)

    date_track_start: datetime.datetime = datetime.datetime(1900, 1, 1)
    date_track_stride: int = 0
    date_track_stop: datetime.datetime = datetime.datetime(2900, 12, 31)

    date_restart_start: datetime.datetime = datetime.datetime(1900, 1, 1)
    date_restart_stride: int = 0
    date_restart_stop: datetime.datetime = datetime.datetime(2900, 12, 31)

    date_boundary_start: datetime.datetime = datetime.datetime(1900, 1, 1)
    date_boundary_stride: int = 0
    date_boundary_stop: datetime.datetime = datetime.datetime(2900, 12, 31)

    date_partition_start: datetime.datetime = datetime.datetime(1900, 1, 1)
    date_partition_stride: int = 0
    date_partition_stop: datetime.datetime = datetime.datetime(2900, 12, 31)

    date_coupling_start: datetime.datetime = datetime.datetime(1900, 1, 1)
    date_coupling_stride: int = 0
    date_coupling_stop: datetime.datetime = datetime.datetime(2900, 12, 31)

    date_restart: str = "'19000101 000000' '0' '29001231 000000'"
    date_restart_stride = 0  # not in a namelsit, bit should!

    homog_count_n_ic1: int = 0
    homog_count_n_ic2: int = 0
    homog_count_n_ic3: int = 0
    homog_count_n_ic4: int = 0
    homog_count_n_ic5: int = 0
    homog_count_n_mdn: int = 0
    homog_count_n_mth: int = 0
    homog_count_n_mvs: int = 0
    homog_count_n_lev: int = 0
    homog_count_n_cur: int = 0
    homog_count_n_wnd: int = 0
    homog_count_n_ice: int = 0
    homog_count_n_mov: int = 0

    homog_input_1_name: str = "unset"
    homog_input_1_date: datetime.datetime = datetime.datetime(1900, 1, 1)
    homog_input_1_value1: int = 0
    homog_input_1_value2: int = 0
    homog_input_1_value3: int = 0

    homog_input_2_name: str = "unset"
    homog_input_2_date:  datetime.datetime = datetime.datetime(1900, 1, 1)
    homog_input_2_value1: int = 0
    homog_input_2_value2: int = 0
    homog_input_2_value3: int = 0

    homog_input_3_name: str = "unset"
    homog_input_3_date:  datetime.datetime = datetime.datetime(1900, 1, 1)
    homog_input_3_value1: int = 0
    homog_input_3_value2: int = 0
    homog_input_3_value3: int = 0

    # validate the data types and values, where possible
    def __post_init__(self):

        # verify if all files are valid
        verify_runpath(self.runpath)
        verify_mod_def(self.mod_def)

        # check domain_iostyp
        if self.domain_iostyp not in [0, 1, 2, 3]:
            error = "Parameter \'domain_iostyp\' must be 0, 1, 2 or 3."
            raise ValueError(error)

        # check if point list exists if date_point_stride > 0
        if self.date_point_stride > 0:
            if not os.path.isfile(self.type_point_file):
                error = f"No such file or directory \'{self.type_point_file}\'."
                raise ValueError(error)
            else:
                basename = os.path.basename(self.type_point_file)
                if not os.path.isfile(os.path.join(self.runpath, basename)):
                    warn = (f"File \'{self.type_point_file}\' is not in the run path. "
                            "I am creating a link for you.")
                    warning(warn)
                    os.symlink(os.path.abspath(self.type_point_file),
                               os.path.join(self.runpath, basename))

                self.__setattr__("type_point_file", basename)

        # update all dates to match the simulation date
        self.__setattr__("date_field_start", self.domain_start)
        self.__setattr__("date_field_stop", self.domain_stop)

        self.__setattr__("date_point_start", self.domain_start)
        self.__setattr__("date_point_stop", self.domain_stop)

        self.__setattr__("date_track_start", self.domain_start)
        self.__setattr__("date_track_stop", self.domain_stop)

        self.__setattr__("date_restart_start", self.domain_start)
        self.__setattr__("date_restart_stop", self.domain_stop)

        self.__setattr__("date_boundary_start", self.domain_start)
        self.__setattr__("date_boundary_stop", self.domain_stop)

        self.__setattr__("date_partition_start", self.domain_start)
        self.__setattr__("date_partition_stop", self.domain_stop)

        self.__setattr__("date_coupling_start", self.domain_start)
        self.__setattr__("date_coupling_stop", self.domain_stop)

        fmt = self.DATE_FORMAT
        d = f"'{self.domain_start.strftime(fmt)}' '{self.date_restart_stride}' '{self.domain_stop.strftime(fmt)}'"
        self.__setattr__("date_restart", d)

        # create the namelist text here
        self.__setattr__("text", self.populate_namelist())

    # NOTE: I am doing this this way instead of reading it from a file
    # because f-strings in a file allow for arbitrary code execution,
    # and are thefore a security issue. Writting everything here at
    # least controls what is being executed.
    def populate_namelist(self):
        """Create the namelist text using NOAA's latest template."""
        txt = dtxt(f"""\
                    ! -------------------------------------------------------- !
                    ! WAVEWATCH III - ww3_shel_nml - single-grid model         !
                    ! -------------------------------------------------------- !

                    ! -------------------------------------------------------- !
                    ! Define top-level model parameters via DOMAIN_NML namelist
                    !
                    ! * IOSTYP defines the output server mode for parallel implementation_
                    !             0 : No data server processes, direct access output from
                    !                 each process (requires true parallel file system)_
                    !             1 : No data server process_ All output for each type
                    !                 performed by process that performs computations too_
                    !             2 : Last process is reserved for all output, and does no
                    !                 computing_
                    !             3 : Multiple dedicated output processes_
                    !
                    ! * namelist must be terminated with /
                    ! * definitions & defaults:
                    !     DOMAIN%IOSTYP =  1                 ! Output server type
                    !     DOMAIN%START  = '19680606 000000'  ! Start date for the entire model
                    !     DOMAIN%STOP   = '19680607 000000'  ! Stop date for the entire model
                    ! -------------------------------------------------------- !
                    &DOMAIN_NML
                      DOMAIN%IOSTYP = {self.domain_iostyp}
                      DOMAIN%START  = '{self.domain_start.strftime(self.DATE_FORMAT)}'
                      DOMAIN%STOP   = '{self.domain_stop.strftime(self.DATE_FORMAT)}'
                    /

                    ! -------------------------------------------------------- !
                    ! Define each forcing via the INPUT_NML namelist
                    !
                    ! * The FORCING flag can be  : 'F' for "no forcing"
                    !                              'T' for "external forcing file"
                    !                              'H' for "homogeneous forcing input"
                    !                              'C' for "coupled forcing field"
                    !
                    ! * homogeneous forcing is not available for ICE_CONC
                    !
                    ! * The ASSIM flag can :  'F' for "no forcing"
                    !                         'T' for "external forcing file"
                    !
                    ! * namelist must be terminated with /
                    ! * definitions & defaults:
                    !     INPUT%FORCING%WATER_LEVELS  = 'F'
                    !     INPUT%FORCING%CURRENTS      = 'F'
                    !     INPUT%FORCING%WINDS         = 'F'
                    !     INPUT%FORCING%ICE_CONC      = 'F'
                    !     INPUT%FORCING%ICE_PARAM1    = 'F'
                    !     INPUT%FORCING%ICE_PARAM2    = 'F'
                    !     INPUT%FORCING%ICE_PARAM3    = 'F'
                    !     INPUT%FORCING%ICE_PARAM4    = 'F'
                    !     INPUT%FORCING%ICE_PARAM5    = 'F'
                    !     INPUT%FORCING%MUD_DENSITY   = 'F'
                    !     INPUT%FORCING%MUD_THICKNESS = 'F'
                    !     INPUT%FORCING%MUD_VISCOSITY = 'F'
                    !     INPUT%ASSIM%MEAN            = 'F'
                    !     INPUT%ASSIM%SPEC1D          = 'F'
                    !     INPUT%ASSIM%SPEC2D          = 'F'
                    ! -------------------------------------------------------- !
                    &INPUT_NML
                      INPUT%FORCING%WATER_LEVELS = '{bool_to_str(self.input_forcing_water_levels).upper()}'
                      INPUT%FORCING%CURRENTS = '{bool_to_str(self.input_forcing_currents).upper()}'
                      INPUT%FORCING%WINDS = '{bool_to_str(self.input_forcing_winds).upper()}'
                      INPUT%FORCING%ICE_CONC = '{bool_to_str(self.input_forcing_ice_conc).upper()}'
                      INPUT%FORCING%ICE_PARAM1 = '{bool_to_str(self.input_forcing_ice_param1).upper()}'
                      INPUT%FORCING%ICE_PARAM2 = '{bool_to_str(self.input_forcing_ice_param2).upper()}'
                      INPUT%FORCING%ICE_PARAM3 = '{bool_to_str(self.input_forcing_ice_param3).upper()}'
                      INPUT%FORCING%ICE_PARAM4 = '{bool_to_str(self.input_forcing_ice_param4).upper()}'
                      INPUT%FORCING%ICE_PARAM5 = '{bool_to_str(self.input_forcing_ice_param5).upper()}'
                      INPUT%FORCING%MUD_DENSITY = '{bool_to_str(self.input_forcing_mud_density).upper()}'
                      INPUT%FORCING%MUD_THICKNESS = '{bool_to_str(self.input_forcing_mud_thickness).upper()}'
                      INPUT%FORCING%MUD_VISCOSITY = '{bool_to_str(self.input_forcing_mud_viscosity).upper()}'
                      INPUT%ASSIM%MEAN = '{bool_to_str(self.input_assim_mean).upper()}'
                      INPUT%ASSIM%SPEC1D = '{bool_to_str(self.input_assim_spec1d).upper()}'
                      INPUT%ASSIM%SPEC2D = '{bool_to_str(self.input_assim_spec2d).upper()}'
                    /


                    ! -------------------------------------------------------- !
                    ! Define the output types point parameters via OUTPUT_TYPE_NML namelist
                    !
                    ! * the point file is a space separated values per line : lon lat 'name'
                    !
                    ! * the full list of field names is :
                    !  All parameters listed below are available in output file of the types
                    !  ASCII and NetCDF_ If selected output file types are grads or grib,
                    !  some parameters may not be available_ The first two columns in the
                    !  table below identify such cases by flags, cols 1 (GRB) and 2 (GXO)
                    !  refer to grib (ww3_grib) and grads (gx_outf), respectively_
                    !
                    ! Columns 3 and 4 provide group and parameter numbers per group_
                    ! Columns 5, 6 and 7 provide:
                    !   5 - code name (internal)
                    !   6 - output tags (names used is ASCII file extensions, NetCDF
                    !       variable names and namelist-based selection
                    !   7 - Long parameter name/definition
                    !
                    !  G  G
                    !  R  X Grp  Param Code     Output  Parameter/Group
                    !  B  O Numb Numbr Name        Tag  Definition
                    !  --------------------------------------------------
                    !        1                          Forcing Fields
                    !   -------------------------------------------------
                    !  T  T  1     1   DW         DPT   Water depth_
                    !  T  T  1     2   C[X,Y]     CUR   Current velocity_
                    !  T  T  1     3   UA         WND   Wind speed_
                    !  T  T  1     4   AS         AST   Air-sea temperature difference_
                    !  T  T  1     5   WLV        WLV   Water levels_
                    !  T  T  1     6   ICE        ICE   Ice concentration_
                    !  T  T  1     7   IBG        IBG   Iceberg-induced damping_
                    !  T  T  1     8   D50        D50   Median sediment grain size_
                    !  T  T  1     9   IC1        IC1   Ice thickness_
                    !  T  T  1    10   IC5        IC5   Ice flow diameter_
                    !   -------------------------------------------------
                    !        2                          Standard mean wave Parameters
                    !   -------------------------------------------------
                    !  T  T  2     1   HS         HS    Wave height_
                    !  T  T  2     2   WLM        LM    Mean wave length_
                    !  T  T  2     3   T02        T02   Mean wave period (Tm0,2)_
                    !  T  T  2     4   T0M1       T0M1  Mean wave period (Tm0,-1)_
                    !  T  T  2     5   T01        T01   Mean wave period (Tm0,1)_
                    !  T  T  2     6   FP0        FP    Peak frequency_
                    !  T  T  2     7   THM        DIR   Mean wave direction_
                    !  T  T  2     8   THS        SPR   Mean directional spread_
                    !  T  T  2     9   THP0       DP    Peak direction_
                    !  T  T  2    10   HIG        HIG   Infragravity height
                    !  T  T  2    11   STMAXE     MXE   Max surface elev (STE)
                    !  T  T  2    12   STMAXD     MXES  St Dev of max surface elev (STE)
                    !  T  T  2    13   HMAXE      MXH   Max wave height (STE)
                    !  T  T  2    14   HCMAXE     MXHC  Max wave height from crest (STE)
                    !  T  T  2    15   HMAXD      SDMH  St Dev of MXC (STE)
                    !  T  T  2    16   HCMAXD     SDMHC St Dev of MXHC (STE)
                    !  F  T  2    17   WBT        WBT   Dominant wave breaking probability bT
                    !   -------------------------------------------------
                    !        3                          Spectral Parameters (first 5)
                    !   -------------------------------------------------
                    !  F  F  3     1   EF         EF    Wave frequency spectrum
                    !  F  F  3     2   TH1M       TH1M  Mean wave direction from a1,b2
                    !  F  F  3     3   STH1M      STH1M Directional spreading from a1,b2
                    !  F  F  3     4   TH2M       TH2M  Mean wave direction from a2,b2
                    !  F  F  3     5   STH2M      STH2M Directional spreading from a2,b2
                    !  F  F  3     6   WN         WN    Wavenumber array
                    !   -------------------------------------------------
                    !        4                          Spectral Partition Parameters
                    !   -------------------------------------------------
                    !  T  T  4     1   PHS        PHS   Partitioned wave heights_
                    !  T  T  4     2   PTP        PTP   Partitioned peak period_
                    !  T  T  4     3   PLP        PLP   Partitioned peak wave length_
                    !  T  T  4     4   PDIR       PDIR  Partitioned mean direction_
                    !  T  T  4     5   PSI        PSPR  Partitioned mean directional spread_
                    !  T  T  4     6   PWS        PWS   Partitioned wind sea fraction_
                    !  T  T  4     7   PDP        PDP   Peak wave direction of partition_
                    !  T  T  4     8   PQP        PQP   Goda peakdedness parameter of partition_
                    !  T  T  4     9   PPE        PPE   JONSWAP peak enhanc_ factor of partition_
                    !  T  T  4    10   PGW        PGW   Gaussian frequency width of partition_
                    !  T  T  4    11   PSW        PSW   Spectral width of partition_
                    !  T  T  4    12   PTM1       PTM10 Mean wave period (m-1,0) of partition_
                    !  T  T  4    13   PT1        PT01  Mean wave period (m0,1) of partition_
                    !  T  T  4    14   PT2        PT02  Mean wave period (m0,2) of partition_
                    !  T  T  4    15   PEP        PEP   Peak spectral density of partition_
                    !  T  T  4    16   PWST       TWS   Total wind sea fraction_
                    !  T  T  4    17   PNR        PNR   Number of partitions_
                    !   -------------------------------------------------
                    !        5                          Atmosphere-waves layer
                    !   -------------------------------------------------
                    !  T  T  5     1   UST        UST   Friction velocity_
                    !  F  T  5     2   CHARN      CHA   Charnock parameter
                    !  F  T  5     3   CGE        CGE   Energy flux
                    !  F  T  5     4   PHIAW      FAW   Air-sea energy flux
                    !  F  T  5     5   TAUWI[X,Y] TAW   Net wave-supported stress
                    !  F  T  5     6   TAUWN[X,Y] TWA   Negative part of the wave-supported stress
                    !  F  F  5     7   WHITECAP   WCC   Whitecap coverage
                    !  F  F  5     8   WHITECAP   WCF   Whitecap thickness
                    !  F  F  5     9   WHITECAP   WCH   Mean breaking height
                    !  F  F  5    10   WHITECAP   WCM   Whitecap moment
                    !  F  F  5    11   FWS        FWS   Wind sea mean period
                    !   -------------------------------------------------
                    !        6                          Wave-ocean layer
                    !   -------------------------------------------------
                    !  F  F  6     1   S[XX,YY,XY] SXY  Radiation stresses_
                    !  F  F  6     2   TAUO[X,Y]  TWO   Wave to ocean momentum flux
                    !  F  F  6     3   BHD        BHD   Bernoulli head (J term)
                    !  F  F  6     4   PHIOC      FOC   Wave to ocean energy flux
                    !  F  F  6     5   TUS[X,Y]   TUS   Stokes transport
                    !  F  F  6     6   USS[X,Y]   USS   Surface Stokes drift
                    !  F  F  6     7   [PR,TP]MS  P2S   Second-order sum pressure
                    !  F  F  6     8   US3D       USF   Spectrum of surface Stokes drift
                    !  F  F  6     9   P2SMS      P2L   Micro seism  source term
                    !  F  F  6    10   TAUICE     TWI   Wave to sea ice stress
                    !  F  F  6    11   PHICE      FIC   Wave to sea ice energy flux
                    !  F  F  6    12   USSP       USP   Partitioned surface Stokes drift
                    !   -------------------------------------------------
                    !        7                          Wave-bottom layer
                    !   -------------------------------------------------
                    !  F  F  7     1   ABA        ABR   Near bottom rms amplitides_
                    !  F  F  7     2   UBA        UBR   Near bottom rms velocities_
                    !  F  F  7     3   BEDFORMS   BED   Bedforms
                    !  F  F  7     4   PHIBBL     FBB   Energy flux due to bottom friction
                    !  F  F  7     5   TAUBBL     TBB   Momentum flux due to bottom friction
                    !   -------------------------------------------------
                    !        8                          Spectrum parameters
                    !   -------------------------------------------------
                    !  F  F  8     1   MSS[X,Y]   MSS   Mean square slopes
                    !  F  F  8     2   MSC[X,Y]   MSC   Spectral level at high frequency tail
                    !  F  F  8     3   WL02[X,Y]  WL02  East/X North/Y mean wavelength compon
                    !  F  F  8     4   ALPXT      AXT   Correl sea surface gradients (x,t)
                    !  F  F  8     5   ALPYT      AYT   Correl sea surface gradients (y,t)
                    !  F  F  8     6   ALPXY      AXY   Correl sea surface gradients (x,y)
                    !   -------------------------------------------------
                    !        9                          Numerical diagnostics
                    !   -------------------------------------------------
                    !  T  T  9     1   DTDYN      DTD   Average time step in integration_
                    !  T  T  9     2   FCUT       FC    Cut-off frequency_
                    !  T  T  9     3   CFLXYMAX   CFX   Max_ CFL number for spatial advection_
                    !  T  T  9     4   CFLTHMAX   CFD   Max_ CFL number for theta-advection_
                    !  F  F  9     5   CFLKMAX    CFK   Max_ CFL number for k-advection_
                    !   -------------------------------------------------
                    !        10                         User defined
                    !   -------------------------------------------------
                    !  F  F  10    1              U1    User defined #1_ (requires coding ___)
                    !  F  F  10    2              U2    User defined #1_ (requires coding ___)
                    !   -------------------------------------------------
                    !
                    !     Section 4 consist of a set of fields, index 0 = wind sea, index
                    !     1:NOSWLL are first NOSWLL swell fields_
                    !
                    !
                    ! * output track file formatted (T) or unformated (F)
                    !
                    ! * coupling fields exchanged list is :
                    !   - Sent fields by ww3:
                    !       - Ocean model : T0M1 OCHA OHS DIR BHD TWO UBR FOC TAW TUS USS LM DRY
                    !       - Atmospheric model : ACHA AHS TP (or FP) FWS
                    !       - Ice model : IC5 TWI
                    !   - Received fields by ww3:
                    !       - Ocean model : SSH CUR
                    !       - Atmospheric model : WND
                    !       - Ice model : ICE IC1 IC5
                    !
                    ! * namelist must be terminated with /
                    ! * definitions & defaults:
                    !     TYPE%FIELD%LIST         =  'unset'
                    !     TYPE%POINT%FILE         =  'points_list'
                    !     TYPE%TRACK%FORMAT       =  T
                    !     TYPE%PARTITION%X0       =  0
                    !     TYPE%PARTITION%XN       =  0
                    !     TYPE%PARTITION%NX       =  0
                    !     TYPE%PARTITION%Y0       =  0
                    !     TYPE%PARTITION%YN       =  0
                    !     TYPE%PARTITION%NY       =  0
                    !     TYPE%PARTITION%FORMAT   =  T
                    !     TYPE%COUPLING%SENT      = 'unset'
                    !     TYPE%COUPLING%RECEIVED  = 'unset'
                    !
                    ! -------------------------------------------------------- !
                    &OUTPUT_TYPE_NML
                      TYPE%FIELD%LIST = '{" ".join(self.type_field_list)}'
                      TYPE%POINT%FILE = '{self.type_point_file}'
                      TYPE%TRACK%FORMAT = {bool_to_str(self.type_track_format).upper()}
                      TYPE%PARTITION%X0 = {self.type_partition_x0}
                      TYPE%PARTITION%XN = {self.type_partition_xn}
                      TYPE%PARTITION%NX = {self.type_partition_nx}
                      TYPE%PARTITION%Y0 = {self.type_partition_y0}
                      TYPE%PARTITION%YN = {self.type_partition_yn}
                      TYPE%PARTITION%NY = {self.type_partition_ny}
                      TYPE%PARTITION%FORMAT = {bool_to_str(self.type_partition_format).upper()}
                      !TYPE%COUPLING%SENT = {self.type_coupling_sent}  # does not work
                      !TYPE%COUPLING%RECEIVED = {self.type_coupling_received}  # does not work
                    /

                    ! -------------------------------------------------------- !
                    ! Define output dates via OUTPUT_DATE_NML namelist
                    !
                    ! * start and stop times are with format 'yyyymmdd hhmmss'
                    ! * if time stride is equal '0', then output is disabled
                    ! * time stride is given in seconds
                    !
                    ! * namelist must be terminated with /
                    ! * definitions & defaults:
                    !     DATE%FIELD%START         =  '19680606 000000'
                    !     DATE%FIELD%STRIDE        =  '0'
                    !     DATE%FIELD%STOP          =  '19680607 000000'
                    !     DATE%POINT%START         =  '19680606 000000'
                    !     DATE%POINT%STRIDE        =  '0'
                    !     DATE%POINT%STOP          =  '19680607 000000'
                    !     DATE%TRACK%START         =  '19680606 000000'
                    !     DATE%TRACK%STRIDE        =  '0'
                    !     DATE%TRACK%STOP          =  '19680607 000000'
                    !     DATE%RESTART%START       =  '19680606 000000'
                    !     DATE%RESTART%STRIDE      =  '0'
                    !     DATE%RESTART%STOP        =  '19680607 000000'
                    !     DATE%BOUNDARY%START      =  '19680606 000000'
                    !     DATE%BOUNDARY%STRIDE     =  '0'
                    !     DATE%BOUNDARY%STOP       =  '19680607 000000'
                    !     DATE%PARTITION%START     =  '19680606 000000'
                    !     DATE%PARTITION%STRIDE    =  '0'
                    !     DATE%PARTITION%STOP      =  '19680607 000000'
                    !     DATE%COUPLING%START      =  '19680606 000000'
                    !     DATE%COUPLING%STRIDE     =  '0'
                    !     DATE%COUPLING%STOP       =  '19680607 000000'
                    !
                    !     DATE%RESTART             =  '19680606 000000' '0' '19680607 000000'
                    ! -------------------------------------------------------- !
                    &OUTPUT_DATE_NML
                      DATE%FIELD%START = '{self.date_field_start.strftime(self.DATE_FORMAT)}'
                      DATE%FIELD%STRIDE = '{self.date_field_stride}'
                      DATE%FIELD%STOP = '{self.date_field_stop.strftime(self.DATE_FORMAT)}'
                      DATE%POINT%START = '{self.date_point_start.strftime(self.DATE_FORMAT)}'
                      DATE%POINT%STRIDE = '{self.date_point_stride}'
                      DATE%POINT%STOP = '{self.date_point_stop.strftime(self.DATE_FORMAT)}'
                      DATE%TRACK%START = '{self.date_track_start.strftime(self.DATE_FORMAT)}'
                      DATE%TRACK%STRIDE = '{self.date_track_stride}'
                      DATE%TRACK%STOP = '{self.date_track_stop.strftime(self.DATE_FORMAT)}'
                      DATE%RESTART%START = '{self.date_restart_start.strftime(self.DATE_FORMAT)}'
                      DATE%RESTART%STRIDE = '{self.date_restart_stride}'
                      DATE%RESTART%STOP = '{self.date_restart_stop.strftime(self.DATE_FORMAT)}'
                      DATE%BOUNDARY%START = '{self.date_boundary_start.strftime(self.DATE_FORMAT)}'
                      DATE%BOUNDARY%STRIDE = '{self.date_boundary_stride}'
                      DATE%BOUNDARY%STOP = '{self.date_boundary_stop.strftime(self.DATE_FORMAT)}'
                      DATE%PARTITION%START = '{self.date_partition_start.strftime(self.DATE_FORMAT)}'
                      DATE%PARTITION%STRIDE = '{self.date_partition_stride}'
                      DATE%PARTITION%STOP = '{self.date_partition_stop.strftime(self.DATE_FORMAT)}'
                      DATE%COUPLING%START = '{self.date_coupling_start.strftime(self.DATE_FORMAT)}'
                      DATE%COUPLING%STRIDE = '{self.date_coupling_stride}'
                      DATE%COUPLING%STOP = '{self.date_coupling_stop.strftime(self.DATE_FORMAT)}'
                    !
                      DATE%RESTART             =  {self.date_restart}
                    /

                    ! -------------------------------------------------------- !
                    ! Define homogeneous input via HOMOG_COUNT_NML and HOMOG_INPUT_NML namelist
                    !
                    ! * the number of each homogeneous input is defined by HOMOG_COUNT
                    ! * the total number of homogeneous input is automatically calculated
                    ! * the homogeneous input must start from index 1 to N
                    ! * if VALUE1 is equal 0, then the homogeneous input is desactivated
                    ! * NAME can be IC1, IC2, IC3, IC4, IC5, MDN, MTH, MVS, LEV, CUR, WND, ICE, MOV
                    ! * each homogeneous input is defined over a maximum of 3 values
                    ! * detailled below :
                    !     - IC1 is defined by thickness
                    !     - IC2 is defined by viscosity
                    !     - IC3 is defined by density
                    !     - IC4 is defined by modulus
                    !     - IC5 is defined by floe diameter
                    !     - MDN is defined by density
                    !     - MTH is defined by thickness
                    !     - MVS is defined by viscosity
                    !     - LEV is defined by height
                    !     - CUR is defined by speed and direction
                    !     - WND is defined by speed, direction and airseatemp
                    !     - ICE is defined by concentration
                    !     - MOV is defined by speed and direction
                    !
                    ! * namelist must be terminated with /
                    ! * definitions & defaults:
                    !     HOMOG_COUNT%N_IC1            =  0
                    !     HOMOG_COUNT%N_IC2            =  0
                    !     HOMOG_COUNT%N_IC3            =  0
                    !     HOMOG_COUNT%N_IC4            =  0
                    !     HOMOG_COUNT%N_IC5            =  0
                    !     HOMOG_COUNT%N_MDN            =  0
                    !     HOMOG_COUNT%N_MTH            =  0
                    !     HOMOG_COUNT%N_MVS            =  0
                    !     HOMOG_COUNT%N_LEV            =  0
                    !     HOMOG_COUNT%N_CUR            =  0
                    !     HOMOG_COUNT%N_WND            =  0
                    !     HOMOG_COUNT%N_ICE            =  0
                    !     HOMOG_COUNT%N_MOV            =  0
                    !
                    !     HOMOG_INPUT(I)%NAME           =  'unset'
                    !     HOMOG_INPUT(I)%DATE           =  '19680606 000000'
                    !     HOMOG_INPUT(I)%VALUE1         =  0
                    !     HOMOG_INPUT(I)%VALUE2         =  0
                    !     HOMOG_INPUT(I)%VALUE3         =  0
                    ! -------------------------------------------------------- !
                    &HOMOG_COUNT_NML
                      HOMOG_COUNT%N_IC1 = {self.homog_count_n_ic1}
                      HOMOG_COUNT%N_IC2 = {self.homog_count_n_ic2}
                      HOMOG_COUNT%N_IC3 = {self.homog_count_n_ic3}
                      HOMOG_COUNT%N_IC4 = {self.homog_count_n_ic4}
                      HOMOG_COUNT%N_IC5 = {self.homog_count_n_ic5}
                      HOMOG_COUNT%N_MDN = {self.homog_count_n_mdn}
                      HOMOG_COUNT%N_MTH = {self.homog_count_n_mth}
                      HOMOG_COUNT%N_MVS = {self.homog_count_n_mvs}
                      HOMOG_COUNT%N_LEV = {self.homog_count_n_lev}
                      HOMOG_COUNT%N_CUR = {self.homog_count_n_cur}
                      HOMOG_COUNT%N_WND = {self.homog_count_n_wnd}
                      HOMOG_COUNT%N_ICE = {self.homog_count_n_ice}
                      HOMOG_COUNT%N_MOV = {self.homog_count_n_mov}
                    /

                    &HOMOG_INPUT_NML
                    ! REQUIRES USER INTERVENTION IF ANYTHING ABOVE IS SET TO > 0
                    /

                    ! -------------------------------------------------------- !
                    ! WAVEWATCH III - end of namelist                          !
                    ! -------------------------------------------------------- !""")
        return txt

    def to_file(self):
        """Write namelist text to file ww3_shel.nml."""
        if os.path.isfile(os.path.join(self.runpath, self.output)):
            os.remove(os.path.join(self.runpath, self.output))
        with open(os.path.join(self.runpath, self.output), 'w') as f:
            f.write(self.text)

    def run(self):
        """Run the program ww3_shel using mpi."""
        res = mpirun(self.runpath, self.EXE, self.nproc)
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
