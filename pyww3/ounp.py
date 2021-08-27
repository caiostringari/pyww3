"""
Abstracts the ww3_ounp program.
"""
from logging import warning
import os

import datetime

from dataclasses import dataclass
from textwrap import dedent as dtxt

from .utils import (run, bool_to_str, verify_runpath, verify_mod_def,
                    verify_ww3_out)

from .namelists import remove_namelist_block, add_namelist_block


@dataclass
class WW3Ounp:

    # withoput these two parameters, everything breaks
    runpath: str
    mod_def: str

    EXE = "ww3_ounp"
    DATE_FORMAT = "%Y%m%d %H%M%S"
    output: str = "ww3_ounp.nml"
    ww3_pnt: str = "out_pnt.ww3"

    point_timestart: datetime.datetime = datetime.datetime(1900, 1, 1)
    point_timestride: int = 0
    point_timecount: int = 1000000000
    point_timesplit: int = 6
    point_list: str = "all"
    point_samefile: bool = True
    point_buffer: int = 150
    point_type: int = 1
    point_dimorder = True

    file_prefix: str = "ww3."
    file_netcdf: int = 4

    spectra_output: int = 3
    spectra_scale_fac: int = 1
    spectra_output_fac: int = 0

    param_output: int = 4

    source_output: int = 4
    source_scale_fac: int = 0
    source_output_fac: int = 0
    source_table_fac: int = 0
    source_spectrum: bool = True
    source_input: bool = True
    source_interactions: bool = True
    source_dissipation: bool = True
    source_bottom: bool = True
    source_ice: bool = True
    source_total: bool = True

    def __post_init__(self):
        """Validates the class initialization"""

        # verify if all files are valid
        verify_runpath(self.runpath)
        verify_mod_def(self.runpath, self.mod_def)
        verify_ww3_out(self.runpath, self.ww3_pnt)

        # update date to match the simulation date
        self.__setattr__("field_timestart", self.point_timestart)

        # create the namelist text here
        self.__setattr__("text", self.populate_namelist())

        # check if file_prefix contais a folder
        if "/" in self.file_prefix:
            dirname = os.path.join(self.runpath, os.path.dirname(self.file_prefix))
            if not os.path.isdir(dirname):
                os.makedirs(dirname, exist_ok=True)
                error = f"Path \'{dirname}\' does not exist in the runpath. I am creating it for you."
                warning(error)

    # NOTE: I am doing this this way instead of reading it from a file
    # because f-strings in a file allow for arbitrary code execution,
    # and are thefore a security issue. Writting everything here at
    # least controls what is being executed.
    def populate_namelist(self):
        """Create the namelist text using NOAA's latest template."""
        txt = dtxt(f"""\
                    ! -------------------------------------------------------------------- !
                    ! WAVEWATCH III - ww3_ounp.nml - Point output post-processing          !
                    ! -------------------------------------------------------------------- !


                    ! -------------------------------------------------------------------- !
                    ! Define the output fields to postprocess via POINT_NML namelist
                    !
                    !
                    ! * namelist must be terminated with /
                    ! * definitions & defaults:
                    ! Stop date for the output field
                    !     POINT%TIMESTART            = '19000101 000000'

                    ! Time stride for the output field
                    !     POINT%TIMESTRIDE           = '0'

                    ! Number of time steps
                    !     POINT%TIMECOUNT            = '1000000000'

                    ! [4(yearly),6(monthly),8(daily),10(hourly)]
                    !     POINT%TIMESPLIT            = 6

                    ! List of points index ['all'|'1 2 3']
                    !     POINT%LIST                 = 'all'

                    ! All the points in the same file
                    !     POINT%SAMEFILE             = T

                    ! Number of points to process per pass
                    !     POINT%BUFFER               = 150

                    ! [0=inventory | 1=spectra | 2=mean param | 3=source terms]
                    !     POINT%TYPE                 = 1

                    ! [time,station=T | station,time=F]
                    !     POINT%DIMORDER             = T
                    ! -------------------------------------------------------------------- !
                    &POINT_NML
                      POINT%TIMESTART = '{self.point_timestart.strftime(self.DATE_FORMAT)}'
                      POINT%TIMESTRIDE = '{self.point_timestride}'
                      POINT%TIMECOUNT = '{self.point_timecount}'
                      POINT%TIMESPLIT = {self.point_timesplit}
                      POINT%LIST = '{self.point_list}'
                      POINT%SAMEFILE = {bool_to_str(self.point_samefile).upper()}
                      POINT%BUFFER = {self.point_buffer}
                      POINT%TYPE = {self.point_type}
                      POINT%DIMORDER = {bool_to_str(self.point_dimorder).upper()}
                    /

                    ! -------------------------------------------------------------------- !
                    ! Define the content of the output file via FILE_NML namelist
                    !
                    ! * namelist must be terminated with /
                    ! * definitions & defaults:
                    !     FILE%PREFIX        = 'ww3.'            ! Prefix for output file name
                    !     FILE%NETCDF        = 3                 ! Netcdf version [3|4]
                    ! -------------------------------------------------------------------- !
                    &FILE_NML
                      FILE%PREFIX = '{self.file_prefix}'
                      FILE%NETCDF = {self.file_netcdf}
                    /


                    ! -------------------------------------------------------------------- !
                    ! Define the type 0, inventory of file
                    !
                    ! * namelist must be terminated with /
                    ! * definitions & defaults:
                    !            No additional input, the above time range is ignored.
                    ! -------------------------------------------------------------------- !

                    ! -------------------------------------------------------------------- !
                    ! Define the type 1, spectra via SPECTRA_NML namelist
                    !
                    ! Table of 1-D spectra content :
                    !   - time, station id, station name, longitude, latitude
                    !   - frequency : unit Hz, center band frequency
                    !                 linear log scale (XFR factor)
                    !   - ffp, f, th1m, sth1m, alpha : 1D spectral parameters
                    !   - dpt, ust, wnd, wnddir : mean parameters
                    !
                    ! Transfert file content :
                    !   - time, station id, station name, longitude, latitude
                    !   - frequency : unit Hz, center band frequency
                    !                  linear log scale (XFR factor)
                    !   - frequency1 : unit Hz, lower band frequency
                    !   - frequency2 : unit Hz, upper band frequency
                    !   - direction : unit degree, convention to, origin East, trigonometric order
                    !   - efth(time,station,frequency,direction) : 2D spectral density
                    !   - dpt, wnd, wnddir, cur, curdir : mean parameters
                    !
                    ! Spectral partitioning content :
                    !   - time, station id, station name, longitude, latitude
                    !   - npart : number of partitions
                    !   - hs, tp, lm, th1m, sth1m, ws, tm10, t01, t02 : partitioned parameters
                    !   - dpt, wnd, wnddir, cur, curdir : mean parameters
                    !
                    !
                    ! * namelist must be terminated with /
                    ! * definitions & defaults:
                    !     SPECTRA%OUTPUT        = 3            ! 1: Print plots
                    !                                          ! 2: Table of 1-D spectra
                    !                                          ! 3: Transfer file
                    !                                          ! 4: Spectral partitioning
                    !     SPECTRA%SCALE_FAC     = 1            ! Scale factor (-1=disabled)
                    !     SPECTRA%OUTPUT_FAC    = 0            ! Output factor (0=normalized)
                    ! -------------------------------------------------------------------- !
                    &SPECTRA_NML
                      SPECTRA%OUTPUT = {self.spectra_output}
                      SPECTRA%SCALE_FAC = {self.spectra_scale_fac}
                      SPECTRA%OUTPUT_FAC = {self.spectra_output_fac}
                    /


                    ! -------------------------------------------------------------------- !
                    ! Define the type 2, mean parameter via PARAM_NML namelist
                    !
                    ! Forcing parameters content :
                    ! - dpt, wnd, wnddir, cur, curdir
                    !
                    ! Mean wave parameters content :
                    ! - hs, lm, tr, th1p, sth1p, fp, th1m, sth1m
                    !
                    ! Nondimensional parameters (U*) content :
                    ! - ust, efst, fpst, cd, alpha
                    !
                    ! Nondimensional parameters (U10) content :
                    ! - wnd, efst, fpst, cd, alpha
                    !
                    ! Validation table content :
                    ! - wnd, wnddir, hs, hsst, cpu, cmu, ast
                    !
                    ! WMO stantdard output content :
                    ! - wnd, wnddir, hs, tp
                    !
                    ! * namelist must be terminated with /
                    ! * definitions & defaults:
                    !     PARAM%OUTPUT      = 4                ! 1: Forcing parameters
                    !                                          ! 2: Mean wave parameters
                    !                                          ! 3: Nondimensional pars. (U*)
                    !                                          ! 4: Nondimensional pars. (U10)
                    !                                          ! 5: Validation table
                    !                                          ! 6: WMO standard output
                    ! -------------------------------------------------------------------- !
                    &PARAM_NML
                      PARAM%OUTPUT = {self.param_output}
                    /


                    ! -------------------------------------------------------------------- !
                    ! Define the type 3, source terms via SOURCE_NML namelist
                    !
                    ! Table of 1-D S(f) content :
                    !   - time, station id, station name, longitude, latitude
                    !   - frequency       : unit Hz, center band frequency
                    !   - ef(frequency)   : 1D spectral density
                    !   - Sin(frequency)  : input source term
                    !   - Snl(frequency)  : non linear interactions source term
                    !   - Sds(frequency)  : dissipation source term
                    !   - Sbt(frequency)  : bottom source term
                    !   - Sice(frequency) : ice source term
                    !   - Stot(frequency) : total source term
                    !   - dpt, ust, wnd   : mean parameters
                    !
                    ! Table of 1-D inverse time scales (1/T = S/F) content :
                    !   - time, station id, station name, longitude, latitude
                    !   - frequency : unit Hz, center band frequency
                    !   - ef(frequency)    : 1D spectral density
                    !   - tini(frequency)  : input inverse time scales source term
                    !   - tnli(frequency)  : non linear interactions inverse time
                    !                        scales source term
                    !   - tdsi(frequency)  : dissipation inverse time scales source term
                    !   - tbti(frequency)  : bottom inverse time scales source term
                    !   - ticei(frequency) : ice inverse time scales source term
                    !   - ttoti(frequency) : total inverse time scales source term
                    !   - dpt, ust, wnd    : mean parameters
                    !
                    ! Transfert file content :
                    !   - time, station id, station name, longitude, latitude
                    !   - frequency : unit Hz, center band frequency
                    !                 linear log scale (XFR factor)
                    !   - frequency1 : unit Hz, lower band frequency
                    !   - frequency2 : unit Hz, upper band frequency
                    !   - direction  : unit degree, convention to, origin East, trigonometric order
                    !   - efth(frequency,direction) : 2D spectral density
                    !   - Sin(frequency,direction)  : input source term
                    !   - Snl(frequency,direction)  : non linear interactions source term
                    !   - Sds(frequency,direction)  : dissipation source term
                    !   - Sbt(frequency,direction)  : bottom source term
                    !   - Sice(frequency,direction) : ice source term
                    !   - Stot(frequency,direction) : total source term
                    !   - dpt, wnd, wnddir, cur, curdir, ust : mean parameters
                    !
                    !
                    ! * namelist must be terminated with /
                    ! * definitions & defaults:
                    !     SOURCE%OUTPUT         = 4            ! 1: Print plots
                    !                                          ! 2: Table of 1-D S(f)
                    !                                          ! 3: Table of 1-D inv. time scales
                    !                                               (1/T = S/F)
                    !                                          ! 4: Transfer file
                    !     SOURCE%SCALE_FAC     = 0             ! Scale factor (-1=disabled)
                    !     SOURCE%OUTPUT_FAC    = 0             ! Output factor (0=normalized)
                    !     SOURCE%TABLE_FAC     = 0             ! Table factor
                    !                                             0 : Dimensional.
                    !                                             1 : N.dim. in terms of U10
                    !                                             2 : N.dim. in terms of U*
                    !                                             3-5: like 0-2 with f norm by fp.
                    !     SOURCE%SPECTRUM      = T             ! [T|F]
                    !     SOURCE%INPUT         = T             ! [T|F]
                    !     SOURCE%INTERACTIONS  = T             ! [T|F]
                    !     SOURCE%DISSIPATION   = T             ! [T|F]
                    !     SOURCE%BOTTOM        = T             ! [T|F]
                    !     SOURCE%ICE           = T             ! [T|F]
                    !     SOURCE%TOTAL         = T             ! [T|F]
                    ! -------------------------------------------------------------------- !
                    &SOURCE_NML
                      SOURCE%OUTPUT = {self.source_output}
                      SOURCE%SCALE_FAC = {self.source_scale_fac}
                      SOURCE%OUTPUT_FAC = {self.source_output_fac}
                      SOURCE%TABLE_FAC = {self.source_table_fac}
                      SOURCE%SPECTRUM = {bool_to_str(self.source_spectrum).upper()}
                      SOURCE%INPUT = {bool_to_str(self.source_input).upper()}
                      SOURCE%INTERACTIONS = {bool_to_str(self.source_interactions).upper()}
                      SOURCE%DISSIPATION = {bool_to_str(self.source_dissipation).upper()}
                      SOURCE%BOTTOM = {bool_to_str(self.source_bottom).upper()}
                      SOURCE%ICE = {bool_to_str(self.source_ice).upper()}
                      SOURCE%TOTAL = {bool_to_str(self.source_total).upper()}
                    /


                    ! -------------------------------------------------------------------- !
                    ! WAVEWATCH III - end of namelist                                      !
                    ! -------------------------------------------------------------------- !""")

        return txt

    def to_file(self):
        """Write namelist text to file ww3_ounp.nml."""
        if os.path.isfile(os.path.join(self.runpath, self.output)):
            os.remove(os.path.join(self.runpath, self.output))
        with open(os.path.join(self.runpath, self.output), 'w') as f:
            f.write(self.text)

    def run(self):
        """Run the program ww3_ounp."""
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
