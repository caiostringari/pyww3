# import pytest

import datetime

from pyww3.shel import WW3Shel


class TestWW3Shel:

    def test_shel(self):
        W = WW3Shel(nproc=8,
                    runpath="tests/test_run/",
                    mod_def="tests/test_data/GLOB_60_MIN.ww3grid",
                    domain_start=datetime.datetime(2010, 1, 1, 0),
                    domain_stop=datetime.datetime(2010, 1, 1, 2),
                    input_forcing_winds=True,
                    input_forcing_ice_conc=True,
                    date_field_stride=3600,
                    date_point_stride=3600,
                    date_restart_stride=3600,
                    type_point_file="tests/test_data/boundary_point_list.txt")
        W.to_file()  # write ww3_shel.nml
        W.run()  # run the simulation
        assert W.returncode == 0
