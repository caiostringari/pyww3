"""
Abstracts the ww3_grid program.
"""
import os

from dataclasses import dataclass
from textwrap import dedent as dtxt

from .ww3 import WW3Base
from .utils import (bool_to_str, verify_runpath, verify_ww3_file)


@dataclass
class WW3GRid(WW3Base):

    runpath: str
    grid_name: str
    grid_nml: str
    grid_type: str
    grid_coord: str
    grid_clos: str

    EXE = "ww3_grid"
    output: str = "ww3_grid.nml"

    spectrum_xfr: int = 1.1
    spectrum_freq1: int = 0.04118
    spectrum_nk: int = 32
    spectrum_nth: int = 24
    spectrum_thoff: int = 0

    run_fldry: bool = False
    run_flcx: bool = True
    run_flcy: bool = True
    run_flcth: bool = True
    run_flck: bool = True
    run_flsou: bool = True

    timesteps_dtmax: float = 480.
    timesteps_dtxy: float = 160.
    timesteps_dtkth: float = 240.
    timesteps_dtmin: float = 10.

    grid_zlim: float = 0.
    grid_dmin: float = 0.

    rect_nx: int = 0
    rect_ny: int = 0
    rect_sx: float = 0.0
    rect_sy: float = 0.0
    rect_sf: float = 1.
    rect_x0: float = 0.
    rect_y0: float = 0.
    rect_sf0: float = 1.

    curv_nx: int = 0
    curv_ny: int = 0
    curv_xcoord_sf: float = 1.
    curv_xcoord_off: float = 0.
    curv_xcoord_filename: str = ""
    curv_xcoord_idf: int = 21
    curv_xcoord_idla: int = 1
    curv_xcoord_idfm: int = 1
    curv_xcoord_format: str = "(....)"
    curv_ycoord_sf: float = 1.
    curv_ycoord_off: float = 0.
    curv_ycoord_filename: str = ""
    curv_ycoord_idf: int = 22
    curv_ycoord_idla: int = 1
    curv_ycoord_idfm: int = 1
    curv_ycoord_format: str = "(....)"

    unst_sf: float = 1.
    unst_filename: str = ""
    unst_idla: int = 20
    unst_idfm: int = 1
    unst_format: int = "(20f10.2)"
    unst_ugobcfile: str = ""

    depth_sf: float = 1.
    depth_filename: str = ""
    depth_idf: int = 50
    depth_dla: int = 1
    depth_dfm: int = 1
    depth_format: str = "(....)"

    mask_filename: str = ""
    mask_idf: int = 60
    mask_idla: int = 1
    mask_idfm: int = 1
    mask_format: str = "(....)"

    obst_sf: float = 1.
    obst_filename: str = ""
    obst_idf: int = 70
    obst_idla: int = 1
    obst_idfm: int = 1
    obst_format: str = "(....)"

    slope_sf: float = 1.
    slope_filename: str = ""
    slope_idf: int = 80
    slope_idla: int = 1
    slope_idfm: int = 1
    slope_format: str = "(....)"

    sed_sf: float = 1.
    sed_filename: str = ""
    sed_idfm: int = 90
    sed_idla: int = 1
    sed_idfm: int = 1
    sed_format: str = "(....)"

    def __post_init__(self):

        # verify if all files are valid
        verify_runpath(self.runpath)

        # check if grid_nml exists
        verify_ww3_file(self.runpath, self.grid_nml)
        self.__setattr__("grid_nml", os.path.basename(self.grid_nml))

        grid_types = ["RECT", "CURV", "UNST"]
        if self.grid_type not in grid_types:
            error = "grid_type type must be: {}".format(",".join(grid_types))
            raise ValueError(error)

        coord_types = ["SPHE", "CART"]
        if self.grid_coord not in coord_types:
            error = "grid_coord type must be: {}".format(",".join(grid_types))
            raise ValueError(error)

        clos_types = ["NONE", "SMPL", "TRPL"]
        if self.grid_clos not in clos_types:
            error = "grid_clos type must be: {}".format(",".join(grid_types))
            raise ValueError(error)

        # check if required data exists
        if self.depth_filename:
            verify_ww3_file(self.runpath, self.depth_filename)
            self.__setattr__("depth_filename", os.path.basename(self.depth_filename))

        if self.mask_filename:
            verify_ww3_file(self.runpath, self.mask_filename)
            self.__setattr__("mask_filename", os.path.basename(self.mask_filename))

        if self.obst_filename:
            verify_ww3_file(self.runpath, self.obst_filename)
            self.__setattr__("obst_filename", os.path.basename(self.obst_filename))

        if self.slope_filename:
            verify_ww3_file(self.runpath, self.slope_filename)
            self.__setattr__("slope_filename", os.path.basename(self.slope_filename))

        if self.sed_filename:
            verify_ww3_file(self.runpath, self.sed_filename)
            self.__setattr__("sed_filename", os.path.basename(self.sed_filename))

        # unstructured grid data
        if self.unst_filename:
            verify_ww3_file(self.runpath, self.unst_filename)
            self.__setattr__("unst_filename", os.path.basename(self.unst_filename))

        # curvlinear grid data
        if self.curv_xcoord_filename:
            verify_ww3_file(self.runpath, self.curv_xcoord_filename)
            self.__setattr__("curv_xcoord_filename", os.path.basename(self.curv_xcoord_filename))

        if self.curv_ycoord_filename:
            verify_ww3_file(self.runpath, self.curv_ycoord_filename)
            self.__setattr__("curv_ycoord_filename", os.path.basename(self.curv_ycoord_filename))

        self.__setattr__("text", self.populate_namelist())

    # NOTE: I am doing this this way instead of reading it from a file
    # because f-strings in a file allow for arbitrary code execution,
    # and are thefore a security issue. Writting everything here at
    # least controls what is being executed.
    def populate_namelist(self):
        """Create the namelist text using NOAA's latest template."""
        txt = dtxt(f"""\
                    ! -------------------------------------------------------------------- !
                    ! WAVEWATCH III - ww3_grid.nml - Grid pre-processing                   !
                    ! -------------------------------------------------------------------- !


                    ! -------------------------------------------------------------------- !
                    ! Define the spectrum parameterization via SPECTRUM_NML namelist
                    !
                    ! * namelist must be terminated with /
                    ! * definitions & defaults:
                    !     SPECTRUM%XFR         = 0.            ! frequency increment
                    !     SPECTRUM%FREQ1       = 0.            ! first frequency (Hz)
                    !     SPECTRUM%NK          = 0             ! number of frequencies (wavenumbers)
                    !     SPECTRUM%NTH         = 0             ! number of direction bins
                    !     SPECTRUM%THOFF       = 0.            ! relative offset of first direction [-0.5,0.5]
                    ! -------------------------------------------------------------------- !
                    &SPECTRUM_NML
                      SPECTRUM%XFR = {self.spectrum_xfr}
                      SPECTRUM%FREQ1 = {self.spectrum_freq1}
                      SPECTRUM%NK = {self.spectrum_nk}
                      SPECTRUM%NTH = {self.spectrum_nth}
                      SPECTRUM%THOFF = {self.spectrum_thoff}
                    /


                    ! -------------------------------------------------------------------- !
                    ! Define the run parameterization via RUN_NML namelist
                    !
                    ! * namelist must be terminated with /
                    ! * definitions & defaults:
                    !     RUN%FLDRY            = F             ! dry run (I/O only, no calculation)
                    !     RUN%FLCX             = F             ! x-component of propagation
                    !     RUN%FLCY             = F             ! y-component of propagation
                    !     RUN%FLCTH            = F             ! direction shift
                    !     RUN%FLCK             = F             ! wavenumber shift
                    !     RUN%FLSOU            = F             ! source terms
                    ! -------------------------------------------------------------------- !
                    &RUN_NML
                      RUN%FLDRY = {bool_to_str(self.run_fldry).upper()}
                      RUN%FLCX = {bool_to_str(self.run_flcx).upper()}
                      RUN%FLCY = {bool_to_str(self.run_flcy).upper()}
                      RUN%FLCTH = {bool_to_str(self.run_flcth).upper()}
                      RUN%FLCK = {bool_to_str(self.run_flck).upper()}
                      RUN%FLSOU = {bool_to_str(self.run_flsou).upper()}
                    /


                    ! -------------------------------------------------------------------- !
                    ! Define the timesteps parameterization via TIMESTEPS_NML namelist
                    !
                    ! * It is highly recommended to set up time steps which are multiple
                    !   between them.
                    !
                    ! * The first time step to calculate is the maximum CFL time step
                    !   which depend on the lowest frequency FREQ1 previously set up and the
                    !   lowest spatial grid resolution in meters DXY.
                    !   reminder : 1 degree=60minutes // 1minute=1mile // 1mile=1.852km
                    !   The formula for the CFL time is :
                    !   Tcfl = DXY / (G / (FREQ1*4*Pi) ) with the constants Pi=3,14 and G=9.8m/s²;
                    !   DTXY  ~= 90% Tcfl
                    !   DTMAX ~= 3 * DTXY   (maximum global time step limit)
                    !
                    ! * The refraction time step depends on how strong can be the current velocities
                    !   on your grid :
                    !   DTKTH ~= DTMAX / 2   ! in case of no or light current velocities
                    !   DTKTH ~= DTMAX / 10  ! in case of strong current velocities
                    !
                    ! * The source terms time step is usually defined between 5s and 60s.
                    !   A common value is 10s.
                    !   DTMIN ~= 10
                    !
                    ! * namelist must be terminated with /
                    ! * definitions & defaults:
                    !     TIMESTEPS%DTMAX      = 0.         ! maximum global time step (s)
                    !     TIMESTEPS%DTXY       = 0.         ! maximum CFL time step for x-y (s)
                    !     TIMESTEPS%DTKTH      = 0.         ! maximum CFL time step for k-th (s)
                    !     TIMESTEPS%DTMIN      = 0.         ! minimum source term time step (s)
                    ! -------------------------------------------------------------------- !
                    &TIMESTEPS_NML
                      TIMESTEPS%DTMAX = {self.timesteps_dtmax}
                      TIMESTEPS%DTXY = {self.timesteps_dtxy}
                      TIMESTEPS%DTKTH = {self.timesteps_dtkth}
                      TIMESTEPS%DTMIN = {self.timesteps_dtmin}
                    /


                    ! -------------------------------------------------------------------- !
                    ! Define the grid to preprocess via GRID_NML namelist
                    !
                    ! * the tunable parameters for source terms, propagation schemes, and
                    !    numerics are read using namelists.
                    ! * Any namelist found in the folowing sections is temporarily written
                    !   to param.scratch, and read from there if necessary.
                    ! * The order of the namelists is immaterial.
                    ! * Namelists not needed for the given switch settings will be skipped
                    !   automatically
                    !
                    ! * grid type can be :
                    !    'RECT' : rectilinear
                    !    'CURV' : curvilinear
                    !    'UNST' : unstructured (triangle-based)
                    !
                    ! * coordinate system can be :
                    !    'SPHE' : Spherical (degrees)
                    !    'CART' : Cartesian (meters)
                    !
                    ! * grid closure can only be applied in spherical coordinates
                    !
                    ! * grid closure can be :
                    !    'NONE' : No closure is applied
                    !    'SMPL' : Simple grid closure. Grid is periodic in the
                    !           : i-index and wraps at i=NX+1. In other words,
                    !           : (NX+1,J) => (1,J). A grid with simple closure
                    !           : may be rectilinear or curvilinear.
                    !    'TRPL' : Tripole grid closure : Grid is periodic in the
                    !           : i-index and wraps at i=NX+1 and has closure at
                    !           : j=NY+1. In other words, (NX+1,J<=NY) => (1,J)
                    !           : and (I,NY+1) => (NX-I+1,NY). Tripole
                    !           : grid closure requires that NX be even. A grid
                    !           : with tripole closure must be curvilinear.
                    !
                    ! * The coastline limit depth is the value which distinguish the sea
                    !   points to the land points. All the points with depth values (ZBIN)
                    !   greater than this limit (ZLIM) will be considered as excluded points
                    !   and will never be wet points, even if the water level grows over.
                    !   It can only overwrite the status of a sea point to a land point.
                    !   The value must have a negative value under the mean sea level
                    !
                    ! * The minimum water depth allowed to compute the model is the absolute
                    !   depth value (DMIN) used in the model if the input depth is lower to
                    !   avoid the model to blow up.
                    !
                    ! * namelist must be terminated with /
                    ! * definitions & defaults:
                    !     GRID%NAME             = 'unset'            ! grid name (30 char)
                    !     GRID%NML              = 'namelists.nml'    ! namelists filename
                    !     GRID%TYPE             = 'unset'            ! grid type
                    !     GRID%COORD            = 'unset'            ! coordinate system
                    !     GRID%CLOS             = 'unset'            ! grid closure
                    !
                    !     GRID%ZLIM             = 0.        ! coastline limit depth (m)
                    !     GRID%DMIN             = 0.        ! abs. minimum water depth (m)
                    ! -------------------------------------------------------------------- !
                    &GRID_NML
                      GRID%NAME = '{self.grid_name}'
                      GRID%NML = '{self.grid_nml}'
                      GRID%TYPE = '{self.grid_type}'
                      GRID%COORD = '{self.grid_coord}'
                      GRID%CLOS = '{self.grid_clos}'
                      GRID%ZLIM = {self.grid_zlim}
                      GRID%DMIN = {self.grid_dmin}
                    /


                    ! -------------------------------------------------------------------- !
                    ! Define the rectilinear grid type via RECT_NML namelist
                    ! - only for RECT grids -
                    !
                    ! * The minimum grid size is 3x3.
                    !
                    ! * If the grid increments SX and SY are given in minutes of arc, the scaling
                    !   factor SF must be set to 60. to provide an increment factor in degree.
                    !
                    ! * If CSTRG='SMPL', then SX is forced to 360/NX.
                    !
                    ! * value <= value_read / scale_fac
                    !
                    ! * namelist must be terminated with /
                    ! * definitions & defaults:
                    !     RECT%NX               = 0        ! number of points along x-axis
                    !     RECT%NY               = 0        ! number of points along y-axis
                    !
                    !     RECT%SX               = 0.       ! grid increment along x-axis
                    !     RECT%SY               = 0.       ! grid increment along y-axis
                    !     RECT%SF               = 1.       ! scaling division factor for x-y axis
                    !
                    !     RECT%X0               = 0.       ! x-coordinate of lower-left corner (deg)
                    !     RECT%Y0               = 0.       ! y-coordinate of lower-left corner (deg)
                    !     RECT%SF0              = 1.       ! scaling division factor for x0,y0 coord
                    ! -------------------------------------------------------------------- !
                    &RECT_NML
                      RECT%NX = {self.rect_nx}
                      RECT%NY = {self.rect_ny}
                      RECT%SX = {self.rect_sx}
                      RECT%SY = {self.rect_sy}
                      RECT%SF = {self.rect_sf}
                      RECT%X0 = {self.rect_x0}
                      RECT%Y0 = {self.rect_y0}
                      RECT%SF0 = {self.rect_sf0}
                    /


                    ! -------------------------------------------------------------------- !
                    ! Define the curvilinear grid type via CURV_NML namelist
                    ! - only for CURV grids -
                    !
                    ! * The minimum grid size is 3x3.
                    !
                    ! * If CSTRG='SMPL', then SX is forced to 360/NX.
                    !
                    ! * value <= scale_fac * value_read + add_offset
                    !
                    ! * IDLA : Layout indicator :
                    !                  1   : Read line-by-line bottom to top. (default)
                    !                  2   : Like 1, single read statement.
                    !                  3   : Read line-by-line top to bottom.
                    !                  4   : Like 3, single read statement.
                    ! * IDFM : format indicator :
                    !                  1   : Free format. (default)
                    !                  2   : Fixed format.
                    !                  3   : Unformatted.
                    ! * FORMAT : element format to read :
                    !               '(....)'  : auto detected (default)
                    !               '(f10.6)' : float type
                    !
                    ! * Example :
                    !      IDF  SF    OFF  IDLA  IDFM  FORMAT    FILENAME
                    !      21   0.25 -0.5  3     1    '(....)'  'x.inp'
                    !      22   0.25  0.5  3     1    '(....)'  'y.inp'
                    !
                    ! * namelist must be terminated with /
                    ! * definitions & defaults:
                    !     CURV%NX               = 0        ! number of points along x-axis
                    !     CURV%NY               = 0        ! number of points along y-axis
                    !
                    !     CURV%XCOORD%SF         = 1.       ! x-coord scale factor
                    !     CURV%XCOORD%OFF        = 0.       ! x-coord add offset
                    !     CURV%XCOORD%FILENAME   = 'unset'  ! x-coord filename
                    !     CURV%XCOORD%IDF        = 21       ! x-coord file unit number
                    !     CURV%XCOORD%IDLA       = 1        ! x-coord layout indicator
                    !     CURV%XCOORD%IDFM       = 1        ! x-coord format indicator
                    !     CURV%XCOORD%FORMAT     = '(....)' ! x-coord formatted read format
                    !
                    !     CURV%YCOORD%SF         = 1.       ! y-coord scale factor
                    !     CURV%YCOORD%OFF        = 0.       ! y-coord add offset
                    !     CURV%YCOORD%FILENAME   = 'unset'  ! y-coord filename
                    !     CURV%YCOORD%IDF        = 22       ! y-coord file unit number
                    !     CURV%YCOORD%IDLA       = 1        ! y-coord layout indicator
                    !     CURV%YCOORD%IDFM       = 1        ! y-coord format indicator
                    !     CURV%YCOORD%FORMAT     = '(....)' ! y-coord formatted read format
                    ! -------------------------------------------------------------------- !
                    &CURV_NML
                      CURV%NX = {self.curv_nx}
                      CURV%NY = {self.curv_ny}
                      CURV%XCOORD%SF = {self.curv_xcoord_sf}
                      CURV%XCOORD%OFF = {self.curv_xcoord_off}
                      CURV%XCOORD%FILENAME = {self.curv_xcoord_filename}
                      CURV%XCOORD%IDF = {self.curv_xcoord_idf}
                      CURV%XCOORD%IDLA = {self.curv_xcoord_idla}
                      CURV%XCOORD%IDFM = {self.curv_xcoord_idfm}
                      CURV%XCOORD%FORMAT = '{self.curv_xcoord_format}'
                      CURV%YCOORD%SF = {self.curv_ycoord_sf}
                      CURV%YCOORD%OFF = {self.curv_ycoord_off}
                      CURV%YCOORD%FILENAME = {self.curv_ycoord_filename}
                      CURV%YCOORD%IDF = {self.curv_ycoord_idf}
                      CURV%YCOORD%IDLA = {self.curv_ycoord_idla}
                      CURV%YCOORD%IDFM = {self.curv_ycoord_idfm}
                      CURV%YCOORD%FORMAT = '{self.curv_ycoord_format}'
                    /


                    ! -------------------------------------------------------------------- !
                    ! Define the unstructured grid type via UNST_NML namelist
                    ! - only for UNST grids -
                    !
                    ! * The minimum grid size is 3x3.
                    !
                    ! * &MISC namelist must be removed
                    !
                    ! * The depth value must have negative values under the mean sea level
                    !
                    ! * The map value must be set as :
                    !    -2 : Excluded boundary point (covered by ice)
                    !    -1 : Excluded sea point (covered by ice)
                    !     0 : Excluded land point
                    !     1 : Sea point
                    !     2 : Active boundary point
                    !     3 : Excluded grid point
                    !     7 : Ice point
                    !
                    ! * the file must be a GMESH grid file containing node and element lists.
                    !
                    ! * Extra open boundary list file with UGOBCFILE in namelist &UNST
                    !   An example is given in regtest ww3_tp2.7
                    !
                    ! * value <= scale_fac * value_read
                    !
                    ! * IDLA : Layout indicator :
                    !                  1   : Read line-by-line bottom to top. (default)
                    !                  2   : Like 1, single read statement.
                    !                  3   : Read line-by-line top to bottom.
                    !                  4   : Like 3, single read statement.
                    ! * IDFM : format indicator :
                    !                  1   : Free format. (default)
                    !                  2   : Fixed format.
                    !                  3   : Unformatted.
                    ! * FORMAT : element format to read :
                    !               '(....)'  : auto detected (default)
                    !               '(f10.6)' : float type
                    !
                    ! * Example :
                    !      IDF  SF   IDLA  IDFM   FORMAT       FILENAME
                    !      20  -1.   4     2     '(20f10.2)'  'ngug.msh'
                    !
                    ! * namelist must be terminated with /
                    ! * definitions & defaults:
                    !     UNST%SF             = 1.       ! unst scale factor
                    !     UNST%FILENAME       = 'unset'  ! unst filename
                    !     UNST%IDF            = 20       ! unst file unit number
                    !     UNST%IDLA           = 1        ! unst layout indicator
                    !     UNST%IDFM           = 1        ! unst format indicator
                    !     UNST%FORMAT         = '(....)' ! unst formatted read format
                    !
                    !     UNST%UGOBCFILE      = 'unset'  ! additional boundary list file
                    ! -------------------------------------------------------------------- !
                    &UNST_NML
                      UNST%SF = {self.unst_sf}
                      UNST%FILENAME = '{self.unst_filename}'
                      UNST%IDLA = {self.unst_idla}
                      UNST%IDFM = {self.unst_idfm}
                      UNST%FORMAT = '{self.unst_format}'
                      UNST%UGOBCFILE = {self.unst_ugobcfile}
                    /


                    ! -------------------------------------------------------------------- !
                    ! Define the spherical multiple-cell grid via SMC_NML namelist
                    ! - only for SMC grids -
                    !
                    ! * SMC cell 'MCELS' and face 'ISIDE & JSIDE' arrays
                    !   and obstruction ratio 'SUBTR'.
                    !
                    ! * The input boundary cell file 'BUNDY' is only needed when NBISMC > 0.
                    !   Boundary cell id list file (unit 35) is only required if boundary
                    !   cell number entered above is non-zero.  The cell id number should be
                    !   the sequential number in the cell array (unit 31) S625MCels.dat.
                    !
                    ! * Extra cell and face arrays for Arctic part if switch ARC is selected.
                    !
                    ! * Example :
                    !      IDF  IDLA  IDFM  FORMAT   FILENAME
                    !      31   1     1    '(....)'  'S6125MCels.dat'
                    !      32   1     1    '(....)'  'S6125ISide.dat'
                    !      33   1     1    '(....)'  'S6125JSide.dat'
                    !      34   1     1    '(....)'  'SMC25Subtr.dat'
                    !      35   1     1    '(....)'  'S6125Bundy.dat'
                    !      36   1     1    '(....)'  'S6125MBArc.dat'
                    !      37   1     1    '(....)'  'S6125AISid.dat'
                    !      38   1     1    '(....)'  'S6125AJSid.dat'
                    !
                    ! * namelist must be terminated with /
                    ! * definitions & defaults:
                    !     SMC%MCELS%FILENAME       = 'unset'  ! MCels filename
                    !     SMC%MCELS%IDF            = 31       ! MCels file unit number
                    !     SMC%MCELS%IDLA           = 1        ! MCels layout indicator
                    !     SMC%MCELS%IDFM           = 1        ! MCels format indicator
                    !     SMC%MCELS%FORMAT         = '(....)' ! MCels formatted read format
                    !
                    !     SMC%ISIDE%FILENAME       = 'unset'  ! ISide filename
                    !     SMC%ISIDE%IDF            = 32       ! ISide file unit number
                    !     SMC%ISIDE%IDLA           = 1        ! ISide layout indicator
                    !     SMC%ISIDE%IDFM           = 1        ! ISide format indicator
                    !     SMC%ISIDE%FORMAT         = '(....)' ! ISide formatted read format
                    !
                    !     SMC%JSIDE%FILENAME       = 'unset'  ! JSide filename
                    !     SMC%JSIDE%IDF            = 33       ! JSide file unit number
                    !     SMC%JSIDE%IDLA           = 1        ! JSide layout indicator
                    !     SMC%JSIDE%IDFM           = 1        ! JSide format indicator
                    !     SMC%JSIDE%FORMAT         = '(....)' ! JSide formatted read format
                    !
                    !     SMC%SUBTR%FILENAME       = 'unset'  ! Subtr filename
                    !     SMC%SUBTR%IDF            = 34       ! Subtr file unit number
                    !     SMC%SUBTR%IDLA           = 1        ! Subtr layout indicator
                    !     SMC%SUBTR%IDFM           = 1        ! Subtr format indicator
                    !     SMC%SUBTR%FORMAT         = '(....)' ! Subtr formatted read format
                    !
                    !     SMC%BUNDY%FILENAME       = 'unset'  ! Bundy filename
                    !     SMC%BUNDY%IDF            = 35       ! Bundy file unit number
                    !     SMC%BUNDY%IDLA           = 1        ! Bundy layout indicator
                    !     SMC%BUNDY%IDFM           = 1        ! Bundy format indicator
                    !     SMC%BUNDY%FORMAT         = '(....)' ! Bundy formatted read format
                    !
                    !     SMC%MBARC%FILENAME       = 'unset'  ! MBArc filename
                    !     SMC%MBARC%IDF            = 36       ! MBArc file unit number
                    !     SMC%MBARC%IDLA           = 1        ! MBArc layout indicator
                    !     SMC%MBARC%IDFM           = 1        ! MBArc format indicator
                    !     SMC%MBARC%FORMAT         = '(....)' ! MBArc formatted read format
                    !
                    !     SMC%AISID%FILENAME       = 'unset'  ! AISid filename
                    !     SMC%AISID%IDF            = 37       ! AISid file unit number
                    !     SMC%AISID%IDLA           = 1        ! AISid layout indicator
                    !     SMC%AISID%IDFM           = 1        ! AISid format indicator
                    !     SMC%AISID%FORMAT         = '(....)' ! AISid formatted read format
                    !
                    !     SMC%AJSID%FILENAME       = 'unset'  ! AJSid filename
                    !     SMC%AJSID%IDF            = 38       ! AJSid file unit number
                    !     SMC%AJSID%IDLA           = 1        ! AJSid layout indicator
                    !     SMC%AJSID%IDFM           = 1        ! AJSid format indicator
                    !     SMC%AJSID%FORMAT         = '(....)' ! AJSid formatted read format
                    ! -------------------------------------------------------------------- !
                    !&SMC_NML
                    ! NOT SUPPORTED. REQUIRES USER INPUT.
                    !/

                    ! -------------------------------------------------------------------- !
                    ! Define the depth to preprocess via DEPTH_NML namelist
                    ! - for RECT and CURV grids -
                    !
                    ! * if no obstruction subgrid, need to set &MISC FLAGTR = 0
                    !
                    ! * The depth value must have negative values under the mean sea level
                    !
                    ! * value <= value_read * scale_fac
                    !
                    ! * IDLA : Layout indicator :
                    !                  1   : Read line-by-line bottom to top.  (default)
                    !                  2   : Like 1, single read statement.
                    !                  3   : Read line-by-line top to bottom.
                    !                  4   : Like 3, single read statement.
                    ! * IDFM : format indicator :
                    !                  1   : Free format.  (default)
                    !                  2   : Fixed format.
                    !                  3   : Unformatted.
                    ! * FORMAT : element format to read :
                    !               '(....)'  : auto detected  (default)
                    !               '(f10.6)' : float type
                    !
                    ! * Example :
                    !      IDF  SF     IDLA  IDFM   FORMAT    FILENAME
                    !      50   0.001  1     1     '(....)'  'GLOB-30M.bot'
                    !
                    ! * namelist must be terminated with /
                    ! * definitions & defaults:
                    !     DEPTH%SF             = 1.       ! scale factor
                    !     DEPTH%FILENAME       = 'unset'  ! filename
                    !     DEPTH%IDF            = 50       ! file unit number
                    !     DEPTH%IDLA           = 1        ! layout indicator
                    !     DEPTH%IDFM           = 1        ! format indicator
                    !     DEPTH%FORMAT         = '(....)' ! formatted read format
                    ! -------------------------------------------------------------------- !
                    &DEPTH_NML
                      DEPTH%SF = {self.depth_sf}
                      DEPTH%FILENAME = '{self.depth_filename}'
                      DEPTH%IDF = {self.depth_idf}
                      DEPTH%IDLA = {self.depth_dla}
                      DEPTH%IDFM = {self.depth_dfm}
                      DEPTH%FORMAT = '{self.depth_format}'
                    /

                    ! -------------------------------------------------------------------- !
                    ! Define the point status map via MASK_NML namelist
                    ! - only for RECT and CURV grids -
                    !
                    ! * If no mask defined, INBOUND can be used to set active boundaries
                    !
                    ! * IDLA : Layout indicator :
                    !                  1   : Read line-by-line bottom to top.  (default)
                    !                  2   : Like 1, single read statement.
                    !                  3   : Read line-by-line top to bottom.
                    !                  4   : Like 3, single read statement.
                    ! * IDFM : format indicator :
                    !                  1   : Free format.  (default)
                    !                  2   : Fixed format.
                    !                  3   : Unformatted.
                    ! * FORMAT : element format to read :
                    !               '(....)'  : auto detected  (default)
                    !               '(f10.6)' : float type
                    !
                    ! * Example :
                    !      IDF  IDLA  IDFM   FORMAT    FILENAME
                    !      60   1     1     '(....)'  'GLOB-30M.mask'
                    !
                    ! * The legend for the input map is :
                    !    -2 : Excluded boundary point (covered by ice)
                    !    -1 : Excluded sea point (covered by ice)
                    !     0 : Excluded land point
                    !     1 : Sea point
                    !     2 : Active boundary point
                    !     3 : Excluded grid point
                    !     7 : Ice point
                    !
                    ! * namelist must be terminated with /
                    ! * definitions & defaults:
                    !     MASK%FILENAME         = 'unset'  ! filename
                    !     MASK%IDF              = 60       ! file unit number
                    !     MASK%IDLA             = 1        ! layout indicator
                    !     MASK%IDFM             = 1        ! format indicator
                    !     MASK%FORMAT           = '(....)' ! formatted read format
                    ! -------------------------------------------------------------------- !
                    &MASK_NML
                      MASK%FILENAME = '{self.mask_filename}'
                      MASK%IDF = {self.mask_idf}
                      MASK%IDLA = {self.mask_idla}
                      MASK%IDFM = {self.mask_idfm}
                      MASK%FORMAT = '{self.mask_format}'
                    /

                    ! -------------------------------------------------------------------- !
                    ! Define the obstruction map via OBST_NML namelist
                    ! - only for RECT and CURV grids -
                    !
                    ! * only used if &MISC FLAGTR = 1 in param.nml
                    !                (transparencies at cell boundaries)
                    !          or if &MISC FLAGTR = 2 in param.nml
                    !                (transparencies at cell centers)
                    !          or if &MISC FLAGTR = 3 in param.nml
                    !                (transparencies at cell boundaries with cont. ice)
                    !          or if &MISC FLAGTR = 4 in param.nml
                    !                (transparencies at cell centers with cont. ice)
                    !
                    ! * value <= value_read * scale_fac
                    !
                    ! * IDLA : Layout indicator :
                    !                  1   : Read line-by-line bottom to top.  (default)
                    !                  2   : Like 1, single read statement.
                    !                  3   : Read line-by-line top to bottom.
                    !                  4   : Like 3, single read statement.
                    ! * IDFM : format indicator :
                    !                  1   : Free format.  (default)
                    !                  2   : Fixed format.
                    !                  3   : Unformatted.
                    ! * FORMAT : element format to read :
                    !               '(....)'  : auto detected  (default)
                    !               '(f10.6)' : float type
                    !
                    ! * Example :
                    !      IDF  SF      IDLA  IDFM   FORMAT    FILENAME
                    !      70   0.0001  1     1     '(....)'  'GLOB-30M.obst'
                    !
                    ! * If the file unit number equals 10, then the data is read from this
                    !   file. The data must follow the above record. No comment lines are
                    !   allowed within the data input.
                    !
                    ! * In the case of unstructured grids, no obstruction file can be added
                    !
                    ! * namelist must be terminated with /
                    ! * definitions & defaults:
                    !     OBST%SF              = 1.       ! scale factor
                    !     OBST%FILENAME        = 'unset'  ! filename
                    !     OBST%IDF             = 70       ! file unit number
                    !     OBST%IDLA            = 1        ! layout indicator
                    !     OBST%IDFM            = 1        ! format indicator
                    !     OBST%FORMAT          = '(....)' ! formatted read format
                    ! -------------------------------------------------------------------- !
                    &OBST_NML
                      OBST%SF = {self.obst_sf}
                      OBST%FILENAME = '{self.obst_filename}'
                      OBST%IDF = {self.obst_idf}
                      OBST%IDLA = {self.obst_idla}
                      OBST%IDFM = {self.obst_idfm}
                      OBST%FORMAT = '{self.obst_format}'
                    /


                    ! -------------------------------------------------------------------- !
                    ! Define the reflexion slope map via SLOPE_NML namelist
                    ! - only for RECT and CURV grids -
                    !
                    ! * only used if &REF1 REFMAP = 2 defined in param.nml
                    !
                    ! * value <= value_read * scale_fac
                    !
                    ! * IDLA : Layout indicator :
                    !                  1   : Read line-by-line bottom to top.  (default)
                    !                  2   : Like 1, single read statement.
                    !                  3   : Read line-by-line top to bottom.
                    !                  4   : Like 3, single read statement.
                    ! * IDFM : format indicator :
                    !                  1   : Free format.  (default)
                    !                  2   : Fixed format.
                    !                  3   : Unformatted.
                    ! * FORMAT : element format to read :
                    !               '(....)'  : auto detected  (default)
                    !               '(f10.6)' : float type
                    !
                    ! * Example :
                    !      IDF  SF      IDLA  IDFM   FORMAT    FILENAME
                    !      80   0.0001  1     1     '(....)'  'GLOB-30M.slope'
                    !
                    ! * In the case of unstructured grids, no sed file can be added
                    !
                    ! * namelist must be terminated with /
                    ! * definitions & defaults:
                    !     SLOPE%SF             = 1.       ! scale factor
                    !     SLOPE%FILENAME       = 'unset'  ! filename
                    !     SLOPE%IDF            = 80       ! file unit number
                    !     SLOPE%IDLA           = 1        ! layout indicator
                    !     SLOPE%IDFM           = 1        ! format indicator
                    !     SLOPE%FORMAT         = '(....)' ! formatted read format
                    ! -------------------------------------------------------------------- !
                    &SLOPE_NML
                      SLOPE%SF = {self.slope_sf}
                      SLOPE%FILENAME = '{self.slope_filename}'
                      SLOPE%IDF = {self.slope_idf}
                      SLOPE%IDLA = {self.slope_idla}
                      SLOPE%IDFM = {self.slope_idfm}
                      SLOPE%FORMAT = '{self.slope_format}'
                    /


                    ! -------------------------------------------------------------------- !
                    ! Define the sedimentary bottom map via SED_NML namelist
                    !
                    ! * only used if &SBT4 SEDMAPD50 = T defined in param.nml
                    !
                    ! * value <= value_read * scale_fac
                    !
                    ! * IDLA : Layout indicator :
                    !                  1   : Read line-by-line bottom to top.  (default)
                    !                  2   : Like 1, single read statement.
                    !                  3   : Read line-by-line top to bottom.
                    !                  4   : Like 3, single read statement.
                    ! * IDFM : format indicator :
                    !                  1   : Free format.  (default)
                    !                  2   : Fixed format.
                    !                  3   : Unformatted.
                    ! * FORMAT : element format to read :
                    !               '(....)'  : auto detected  (default)
                    !               '(f10.6)' : float type
                    !
                    ! * Example :
                    !      IDF SF  IDLA  IDFM   FORMAT    FILENAME
                    !      90  1.  1     2     '(f10.6)' 'SED.txt'
                    !
                    ! * In the case of unstructured grids, no sed file can be added
                    !
                    ! * namelist must be terminated with /
                    ! * definitions & defaults:
                    !     SED%SF               = 1.       ! scale factor
                    !     SED%FILENAME         = 'unset'  ! filename
                    !     SED%IDF              = 90       ! file unit number
                    !     SED%IDLA             = 1        ! layout indicator
                    !     SED%IDFM             = 1        ! format indicator
                    !     SED%FORMAT           = '(....)' ! formatted read format
                    ! -------------------------------------------------------------------- !
                    &SED_NML
                      SED%SF = {self.sed_sf}
                      SED%FILENAME = '{self.sed_filename}'
                      SED%IDFM = {self.sed_idfm}
                      SED%IDLA = {self.sed_idla}
                      SED%IDFM = {self.sed_idfm}
                      SED%FORMAT = '{self.sed_format}'
                    /


                    ! -------------------------------------------------------------------- !
                    ! Define the input boundary points via INBND_COUNT_NML and
                    !                                      INBND_POINT_NML namelist
                    ! - for RECT, CURV and UNST grids -
                    !
                    ! * If no mask defined, INBOUND can be used
                    !
                    ! * If the actual input data is not defined in the actual wave model run
                    !   the initial conditions will be applied as constant boundary conditions.
                    !
                    ! * The number of points is defined by INBND_COUNT
                    !
                    ! * The points must start from index 1 to N
                    !
                    ! * Each line contains:
                    !     Discrete grid counters (IX,IY) of the active point and a
                    !     connect flag. If this flag is true, and the present and previous
                    !     point are on a grid line or diagonal, all intermediate points
                    !     are also defined as boundary points.
                    !
                    ! * Included point :
                    !     grid points from segment data
                    !     Defines as lines identifying points at which
                    !     input boundary conditions are to be defined.
                    !
                    ! * namelist must be terminated with /
                    ! * definitions & defaults:
                    !     INBND_COUNT%N_POINT     = 0        ! number of segments
                    !
                    !     INBND_POINT(I)%X_INDEX  = 0        ! x index included point
                    !     INBND_POINT(I)%Y_INDEX  = 0        ! y index included point
                    !     INBND_POINT(I)%CONNECT  = F        ! connect flag
                    !
                    ! OR
                    !     INBND_POINT(I)          = 0 0 F    ! included point
                    ! -------------------------------------------------------------------- !
                    !&INBND_COUNT_NML
                    ! NOT SUPPORTED. REQUIRES USER INPUT.
                    !/

                    !&INBND_POINT_NML
                    ! NOT SUPPORTED. REQUIRES USER INPUT.
                    !/

                    ! -------------------------------------------------------------------- !
                    ! Define the excluded points and bodies via EXCL_COUNT_NML, EXCL_POINT_NML
                    !                                           and EXCL_BODY_NML namelist
                    ! - only for RECT and CURV grids -
                    !
                    ! * If no mask defined, EXCL can NOT be used
                    !
                    ! * The number of points and bodies are defined by EXCL_COUNT
                    !
                    ! * The points and bodies must start from index 1 to N
                    !
                    ! * Each line contains:
                    !     Discrete grid counters (IX,IY) of the active point and a
                    !     connect flag. If this flag is true, and the present and previous
                    !     point are on a grid line or diagonal, all intermediate points
                    !     are also defined as boundary points.
                    !
                    ! * Excluded point :
                    !     grid points from segment data
                    !     Defined as lines identifying points at which
                    !     input boundary conditions are to be excluded.
                    !
                    ! * Excluded body:
                    !     Define a point in a closed body of sea points to remove the
                    !     entire body of sea points.
                    !
                    ! * namelist must be terminated with /
                    ! * definitions & defaults:
                    !     EXCL_COUNT%N_POINT      = 0        ! number of segments
                    !     EXCL_COUNT%N_BODY       = 0        ! number of bodies
                    !
                    !     EXCL_POINT(J)%X_INDEX   = 0        ! x index excluded point
                    !     EXCL_POINT(J)%Y_INDEX   = 0        ! y index excluded point
                    !     EXCL_POINT(J)%CONNECT   = F        ! connect flag
                    !
                    !     EXCL_BODY(K)%X_INDEX    = 0        ! x index excluded body
                    !     EXCL_BODY(K)%Y_INDEX    = 0        ! y index excluded body
                    ! OR
                    !     EXCL_POINT(J)           = 0 0 F    ! excluded point
                    !     EXCL_BODY(K)            = 0 0      ! excluded body
                    ! -------------------------------------------------------------------- !
                    !&EXCL_COUNT_NML
                    ! NOT SUPPORTED. REQUIRES USER INPUT.
                    !/

                    !&EXCL_POINT_NML
                    ! NOT SUPPORTED. REQUIRES USER INPUT.
                    !/

                    !&EXCL_BODY_NML
                    ! NOT SUPPORTED. REQUIRES USER INPUT.
                    !/


                    ! -------------------------------------------------------------------- !
                    ! Define the output boundary points via OUTBND_COUNT_NML and
                    !                                       OUTBND_LINE_NML namelist
                    ! - only for RECT and CURV grids -
                    !
                    ! * It will creates a nest file with output boundaries for a inner grid.
                    !   The prefered way to do it is to use ww3_bounc program.
                    !
                    ! * These do not need to be defined for data transfer between grids in
                    !    the multi grid driver.
                    !
                    ! * The number of lines are defined by OUTBND_COUNT
                    !
                    ! * The lines must start from index 1 to N
                    !
                    ! * Output boundary points are defined as a number of straight lines,
                    !   defined by its starting point (X0,Y0), increments (DX,DY) and number
                    !   of points. A negative number of points starts a new output file.
                    !
                    ! * Example for spherical grid in degrees :
                    !     '1.75  1.50  0.25 -0.10     3'
                    !     '2.25  1.50 -0.10  0.00    -6'
                    !     '0.10  0.10  0.10  0.00   -10'
                    !
                    ! * namelist must be terminated with /
                    ! * definitions & defaults:
                    !     OUTBND_COUNT%N_LINE   = 0               ! number of lines
                    !
                    !     OUTBND_LINE(I)%X0     = 0.              ! x index start point
                    !     OUTBND_LINE(I)%Y0     = 0.              ! y index start point
                    !     OUTBND_LINE(I)%DX     = 0.              ! x-along increment
                    !     OUTBND_LINE(I)%DY     = 0.              ! y-along increment
                    !     OUTBND_LINE(I)%NP     = 0               ! number of points
                    ! OR
                    !     OUTBND_LINE(I)        = 0. 0. 0. 0. 0   ! included lines
                    ! -------------------------------------------------------------------- !
                    !&OUTBND_COUNT_NML
                    ! NOT SUPPORTED. REQUIRES USER INPUT.
                    !/

                    !&OUTBND_LINE_NML
                    ! NOT SUPPORTED. REQUIRES USER INPUT.
                    !/

                    ! -------------------------------------------------------------------- !
                    ! WAVEWATCH III - end of namelist                                      !
                    ! -------------------------------------------------------------------- !""")

        return txt

    # def to_file(self):
    #     """Write namelist text to file ww3_ounf.nml."""
    #     if os.path.isfile(os.path.join(self.runpath, self.output)):
    #         os.remove(os.path.join(self.runpath, self.output))
    #     with open(os.path.join(self.runpath, self.output), 'w') as f:
    #         f.write(self.text)

    # def run(self):
    #     """Run the program ww3_grid."""
    #     res = run(self.runpath, self.EXE)
    #     self.__setattr__("returncode", res.returncode)
    #     self.__setattr__("stdout", res.stdout)
    #     self.__setattr__("stderr", res.stderr)

    # def update_text(self, block: str, action: str = "add", index: int = -1):
    #     """Update namelist block in the text with an action."""

    #     # add case
    #     if action.lower().startswith("a"):
    #         newtext = add_namelist_block(self.text, block, index)

    #     # remove case
    #     else:
    #         newtext = remove_namelist_block(self.text, block)

    #     # update class attribute
    #     self.__setattr__("text", newtext)
