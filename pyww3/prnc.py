"""
Abstracts the ww3_prnc program.
"""
import os
import re

import datetime

import xarray as xr
import numpy as np

from logging import warning
from dataclasses import dataclass
from textwrap import dedent as dtxt

from .utils import (bool_to_str, verify_runpath, verify_mod_def)

from .ww3 import WW3Base


@dataclass
class WW3Prnc(WW3Base):
    """
    Abstraction class for ww3_prnc.
    """

    # withoput these two parameters, everything breaks
    runpath: str
    mod_def: str

    # user must give these parameters
    forcing_field: str
    forcing_grid_latlon: bool
    file_filename: str
    file_longitude: str
    file_latitude: str
    file_var_1: str

    EXE = "ww3_prnc"
    DATE_FORMAT = "%Y%m%d %H%M%S"
    output: str = "ww3_prnc.nml"

    # these are more or less optional
    file_var_2: str = " "
    file_var_3: str = " "
    forcing_timestart: datetime.datetime = datetime.datetime(1900, 1, 1)
    forcing_timestop: datetime.datetime = datetime.datetime(2900, 12, 31)
    file_timeshift: str = "00000000 000000"

    VALID_FORCING_FIELDS = ["ICE_PARAM1",
                            "ICE_PARAM2",
                            "ICE_PARAM3",
                            "ICE_PARAM4",
                            "ICE_PARAM5",
                            "MUD_DENSITY",
                            "MUD_THICKNESS",
                            "MUD_VISCOSITY",
                            "WATER_LEVELS",
                            "CURRENTS",
                            "WINDS",
                            "WIND_AST",
                            "ATM_MOMENTUM",
                            "AIR_DENSITY",
                            "ICE_CONC",
                            "ICE_BERG",
                            "DATA_ASSIM"]

    # validate the data types and values, where possible
    def __post_init__(self):
        """Validates the class initialization"""

        # verify if all files are valid
        verify_runpath(self.runpath)
        verify_mod_def(self.runpath, self.mod_def)

        # path of the netcdf file we are trying to process
        runnc = os.path.abspath(os.path.join(self.runpath,
                                os.path.basename(self.file_filename)))

        if not isinstance(self.forcing_timestart, datetime.datetime):
            error = ("Please set \'forcing_timestart\' to a valid"
                     " datetime.datetime.")
            raise ValueError(error)

        if not isinstance(self.forcing_timestart, datetime.datetime):
            error = ("Please set \'forcing_timestop\' to a valid"
                     " datetime.datetime.")
            raise ValueError(error)

        if self.forcing_field not in self.VALID_FORCING_FIELDS:
            error = ("Please set \'forcing_field\' to valid"
                     f" forcing field. Options are {self.VALID_FORCING_FIELDS}")
            raise ValueError(error)

        # set forcing_grid_latlon to either t or f
        if isinstance(self.forcing_grid_latlon, bool):
            if self.forcing_grid_latlon:
                self.__setattr__("forcing_grid_latlon", "t")
            else:
                self.__setattr__("forcing_grid_latlon", "f")
        else:
            error = "forcing_grid_latlon must be a boolean."
            raise ValueError(error)

        # try to load the netcdf to validate againt what was passed to the
        # class constructor.
        if not os.path.isfile(self.file_filename):
            error = f"No such file or directory \'{self.file_filename}\'"
            raise ValueError(error)

        if not os.path.isfile(runnc):
            error = (f"Could not find the forcing file \'{self.file_filename}\' in the run path. "
                     "I am creating a link for you.")
            warning(error)
            os.symlink(os.path.abspath(self.file_filename), runnc)

            # update the class to use the correct file
            self.__setattr__("file_filename", os.path.basename(runnc))
        else:
            # update the class to use the correct file
            self.__setattr__("file_filename", os.path.basename(runnc))

        try:
            nc = xr.open_dataset(os.path.join(self.runpath,
                                              self.file_filename))
            coord_names = list(nc.coords.keys())
            var_names = list(nc.keys())
        except Exception:
            error = ("Problem with input netcdf. Please use a valid file.")
            raise ValueError(error)

        # verify coordinates
        for attr, tryval in zip(["file_longitude", "file_latitude"],
                                [("lo", "x"), ("la", "y")]):
            key = self.__getattribute__(attr)
            if key not in nc.coords:
                wrn = (f"Warning: could not find coordinate \'{key}\' "
                       f" in the input data. Options are {coord_names}.")
                warning(warning)
                try:
                    res = [value.lower() for value in coord_names if value.startswith(tryval)][0]
                    self.__setattr__(attr, res)
                    wrn = (f"Setting \'{attr}\' to \'{res}\'."
                           " If this is wrong, please set the correct value when building the class.")
                    warning(wrn)
                except Exception:
                    raise ValueError("Could not set coordinate name automatically.")

        # verify data variables
        for attr in ["file_var_1", "file_var_2", "file_var_3"]:
            key = self.__getattribute__(attr)
            if key == " ":
                pass  # this skip empty variables, which are allowed
            else:
                if key not in var_names:
                    error = f"Variable \'{key}\' is not in the dataset. Options are \'{var_names}\'."
                    raise ValueError(error)

        nc.close()

        # validate timeshift
        error = f"file_timeshift must conform to {self.DATE_FORMAT}."
        nparts = len(self.file_timeshift.split())

        if nparts < 2:
            raise ValueError(error)

        p1 = re.search("^[0-9]{8}$", self.file_timeshift.split()[0])
        p2 = re.search("^[0-9]{6}$", self.file_timeshift.split()[1])

        if not (p1 and p2):
            raise ValueError(error)

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
                    ! WAVEWATCH III - ww3_prnc.nml - Field preprocessor        !
                    ! -------------------------------------------------------- !

                    ! -------------------------------------------------------- !
                    ! Define the forcing fields to preprocess via FORCING_NML namelist
                    !
                    ! * only one FORCING%FIELD can be set at true
                    ! * only one FORCING%grid can be set at true
                    ! * tidal constituents FORCING%tidal is only available
                    !   on grid%asis with FIELD%level or FIELD%current
                    !
                    ! * namelist must be terminated with /
                    ! * definitions & defaults:

                    !     Start date for the forcing field
                    !     FORCING%TIMESTART            = '19000101 000000'

                    !     Stop date for the forcing field
                    !     FORCING%TIMESTOP             = '29001231 000000'
                    !
                    !     Ice thickness (1-component)
                    !     FORCING%FIELD%ICE_PARAM1     = f

                    !     Ice viscosity (1-component)
                    !     FORCING%FIELD%ICE_PARAM2     = f

                    !     Ice density (1-component)
                    !     FORCING%FIELD%ICE_PARAM3     = f

                    !     Ice modulus (1-component)
                    !     FORCING%FIELD%ICE_PARAM4     = f

                    !     Ice floe mean diameter (1-component)
                    !     FORCING%FIELD%ICE_PARAM5     = f

                    !     Mud density (1-component)
                    !     FORCING%FIELD%MUD_DENSITY    = f

                    !     Mud thickness (1-component)
                    !     FORCING%FIELD%MUD_THICKNESS  = f

                    !     Mud viscosity (1-component)
                    !     FORCING%FIELD%MUD_VISCOSITY  = f

                    !     Level (1-component)
                    !     FORCING%FIELD%WATER_LEVELS   = f

                    !     Current (2-components)
                    !     FORCING%FIELD%CURRENTS       = f

                    !     Wind (2-components)
                    !     FORCING%FIELD%WINDS          = f

                    !     Wind and air-sea temp. dif. (3-components)
                    !     FORCING%FIELD%WIND_AST       = f

                    !     Ice concentration (1-component)
                    !     FORCING%FIELD%ICE_CONC       = f

                    !     Icebergs and sea ice concentration (2-components)
                    !     FORCING%FIELD%ICE_BERG       = f

                    !     Data for assimilation (1-component)
                    !     FORCING%FIELD%DATA_ASSIM     = f

                    !
                    !     Transfert field 'as is' on the model grid
                    !     FORCING%GRID%ASIS            = f

                    !     Define field on regular lat/lon or cartesian grid
                    !     FORCING%GRID%LATLON          = f

                    !
                    !     Set the tidal constituents [FAST | VFAST | 'M2 S2 N2']
                    !     FORCING%TIDAL                = 'unset'
                    ! -------------------------------------------------------- !
                    &FORCING_NML
                      FORCING%TIMESTART = '{self.forcing_timestart.strftime(self.DATE_FORMAT)}'
                      FORCING%TIMESTOP = '{self.forcing_timestop.strftime(self.DATE_FORMAT)}'
                      FORCING%FIELD%{self.forcing_field} = t
                      FORCING%GRID%LATLON = {bool_to_str(self.forcing_grid_latlon).lower()}
                    /


                    ! -------------------------------------------------------- !
                    ! Define the content of the input file via FILE_NML namelist
                    !
                    ! * input file must respect netCDF format and CF conventions
                    ! * input file must contain :
                    !      -dimension : time, name expected to be called time
                    !      -dimension : longitude/latitude, names can defined in the namelist
                    !      -variable : time defined along time dimension
                    !      -attribute : time with attributes units written as ISO8601 convention
                    !      -attribute : time with attributes calendar set to standard as CF
                    !                   convention
                    !      -variable : longitude defined along longitude dimension
                    !      -variable : latitude defined along latitude dimension
                    !      -variable : field defined along time,latitude, longitude dimensions
                    ! * FILE%VAR(I) must be set for each field component
                    !
                    ! * namelist must be terminated with /
                    ! * definitions & defaults:

                    ! relative path input file name
                    !     FILE%FILENAME      = 'unset'
                    ! longitude/x dimension name
                    !     FILE%LONGITUDE     = 'unset'

                    ! latitude/y dimension name
                    !     FILE%LATITUDE      = 'unset'

                    ! field component
                    !     FILE%VAR(I)        = 'unset'

                    ! shift the time value to 'YYYYMMDD HHMMSS'
                    !     FILE%TIMESHIFT     = '00000000 000000'
                    ! -------------------------------------------------------- !
                    &FILE_NML
                      FILE%FILENAME = '{self.file_filename}'
                      FILE%LONGITUDE = '{self.file_longitude}'
                      FILE%LATITUDE = '{self.file_latitude}'
                      FILE%VAR(1) = '{self.file_var_1}'
                      FILE%VAR(2) = '{self.file_var_2}'
                      FILE%VAR(3) = '{self.file_var_3}'
                      FILE%TIMESHIFT = '{self.file_timeshift}'
                    /

                    ! -------------------------------------------------------- !
                    ! WAVEWATCH III - end of namelist                          !
                    ! -------------------------------------------------------- !""")

        return txt

    def reverse_latitudes(self, newfilename):
        """Reverse latitudes if requested"""

        # open the dataset
        inp = os.path.join(self.runpath, self.file_filename)
        ds = xr.open_dataset(inp)
        attr = self.__getattribute__("file_latitude")

        reverse_lat = ds[attr][::-1]

        dy = np.diff(ds[attr].values)
        if dy[0] < 0:

            newds = ds.reindex({attr: reverse_lat})

            print("Reversing latitudes, please wait...")

            # write to file
            out = os.path.join(self.runpath, os.path.basename(newfilename))
            newds.to_netcdf(out)
            newds.close()

            # update class attribute
            self.__setattr__("file_filename", os.path.basename(out))

            # update namelist
            self.__setattr__("text", self.populate_namelist())

        else:
            print("Latitudes seem file, I am not reversing them.")
            self.__setattr__("file_filename",
                             os.path.basename(self.file_filename))
            self.__setattr__("text", self.populate_namelist())

        ds.close()