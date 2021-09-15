"""
tests.test_ounp.py
~~~~~~~~~~~~~~~~~~~~

Test suite for the ounp program abstraction.
"""
import os
import datetime

from pyww3.ounp import WW3Ounp
from common import get_grid

class TestWW3Ounp:

    def test_ounf_single_file(self):

        # search for a grid
        grid = "tests/test_run/mod_def.ww3"
        if not os.path.isfile(grid):
            get_grid(grid)

        W = WW3Ounp(runpath="tests/test_run/",
                    mod_def=grid,
                    ww3_pnt="tests/test_run/out_pnt.ww3",
                    point_timestart=datetime.datetime(2010, 1, 1),
                    point_timestride=480)
        W.to_file()
        W.run()

        assert W.returncode == 0

    def test_ounf_separated_files(self):

        # search for a grid
        grid = "tests/test_run/mod_def.ww3"
        if not os.path.isfile(grid):
            get_grid(grid)

        W = WW3Ounp(runpath="tests/test_run/",
                    mod_def=grid,
                    ww3_pnt="tests/test_run/out_pnt.ww3",
                    point_timestart=datetime.datetime(2010, 1, 1),
                    point_timestride=480,
                    point_samefile=False,
                    file_prefix="spc/ww3.")
        W.to_file()
        W.run()

        assert W.returncode == 0
