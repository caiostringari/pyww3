from logging import warning
import os

from glob import glob
from natsort import natsorted

from dataclasses import dataclass
import shutil
from textwrap import dedent as dtxt

from .ww3 import WW3Base
from .utils import (verify_runpath, verify_mod_def, verify_ww3_file)


@dataclass
class WW3Bounc(WW3Base):
    """This class abstracts the program ww3_bounc. It is an extension of the class
    :class:`pyww3.ww3.WW3Base()`.
    """

    # withoput these two parameters, everything breaks
    runpath: str
    mod_def: str

    EXE = "ww3_bounc"
    DATE_FORMAT = "%Y%m%d %H%M%S"
    bound_file: str  # input file or path
    output: str = "ww3_bounc.nml"

    bound_mode: str = "WRITE"
    bound_interp: int = 2
    bound_verbose: int = 1

    def __post_init__(self):
        """Validate the class initialization"""

        # verify if all files are valid
        verify_runpath(self.runpath)
        verify_mod_def(self.runpath, self.mod_def)

        # check if file or directory

        # make sure path exists and create a file list
        if os.path.isdir(self.bound_file):
            lastp = os.path.basename(os.path.normpath(self.bound_file))
            dst = os.path.join(self.runpath, lastp)

            if not os.path.isdir(dst):

                error = f"Folder {lastp} not in the runpath. I am creating it for you."
                warning(error)
                os.makedirs(dst, exist_ok=True)

            # copy files overs and create a list
            filelist = []
            fnames = natsorted(glob(os.path.join(self.bound_file, "*")))
            for f in fnames:
                fdst = os.path.join(dst, os.path.basename(f))
                if not fdst:
                    shutil.copy(f, fdst)
                filelist.append(os.path.basename(f))

            # write the file list
            with open(os.path.join(self.runpath, "spec.list"), "w") as f:
                for fname in filelist:
                    f.write(os.path.join(lastp, fname) + "\n")

            self.__setattr__("bound_file", "spec.list")

        # if file, make sure it is in the runpath
        else:
            verify_ww3_file(self.runpath, self.bound_file)
            # update bound_file location
            self.__setattr__("bound_file", os.path.basename(self.bound_file))

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
                   ! WAVEWATCH III - ww3_bounc.nml - Boundary input post-processing       !
                   ! -------------------------------------------------------------------- !

                   ! -------------------------------------------------------------------- !
                   ! Define the input boundaries to preprocess via BOUND_NML namelist
                   !
                   ! * namelist must be terminated with /
                   ! * definitions & defaults:
                   ! ['WRITE'|'READ']
                   !     BOUND%MODE                 = 'WRITE'

                   ! interpolation [1(nearest),2(linear)]
                   !     BOUND%INTERP               = 2

                   ! [0|1|2]
                   !     BOUND%VERBOSE              = 1

                   ! input _spec.nc listing file
                   !     BOUND%FILE                 = 'spec.list'
                   ! -------------------------------------------------------------------- !
                   &BOUND_NML
                     BOUND%MODE                 = '{self.bound_mode}'
                     BOUND%INTERP               = {self.bound_interp}
                     BOUND%VERBOSE              = {self.bound_verbose}
                     BOUND%FILE                 = '{self.bound_file}'
                   /
                   ! -------------------------------------------------------------------- !
                   ! WAVEWATCH III - end of namelist                                      !
                   ! -------------------------------------------------------------------- !""")
        return txt

    # def to_file(self):
    #     """Write namelist text to file ww3_bounc.nml."""
    #     if os.path.isfile(os.path.join(self.runpath, self.output)):
    #         os.remove(os.path.join(self.runpath, self.output))
    #     with open(os.path.join(self.runpath, self.output), 'w') as f:
    #         f.write(self.text)

    # def run(self):
    #     """Run the program ww3_bounc."""
    #     res = run(self.runpath, self.EXE)
    #     self.__setattr__("returncode", res.returncode)
    #     self.__setattr__("stdout", res.stdout)
    #     self.__setattr__("stderr", res.stderr)
