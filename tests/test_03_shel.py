import os
import datetime
from pyww3.shel import WW3Shel
from common import get_data, get_grid

class TestWW3Shel:

    def test_shel(self):

        # search for a grid
        grid = "tests/test_run/mod_def.ww3"
        if not os.path.isfile(grid):
            get_grid(grid)

        W = WW3Shel(nproc=8,
                    runpath="tests/test_run/",
                    mod_def=grid,
                    domain_start=datetime.datetime(2010, 1, 1, 0),
                    domain_stop=datetime.datetime(2010, 1, 1, 6),
                    input_forcing_winds=True,
                    input_forcing_ice_conc=True,
                    date_field_stride=3600,
                    date_point_stride=3600,
                    date_restart_stride=3600,
                    type_point_file="tests/test_data/boundary_point_list.txt")
        W.to_file()  # write ww3_shel.nml
        W.run(mpi=True, nproc=W.nproc)  # run the simulation with MPI
        assert W.returncode == 0
