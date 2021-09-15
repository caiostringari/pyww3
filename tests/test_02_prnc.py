"""
tests.test_curves.py
~~~~~~~~~~~~~~~~~~~~

Test suite for the prnc program abstraction.
"""
import os

import datetime

from pyww3.prnc import WW3Prnc
from common import get_data, get_grid


class TestPrnc:

    # test winds from ECMWF
    def test_Era5_winds(self):

        # download data
        get_data("wind", "tests/test_data/Era5_2010_01_winds_2days.nc")

        # search for a grid
        grid = "tests/test_run/mod_def.ww3"
        if not os.path.isfile(grid):
            get_grid(grid)

        W = WW3Prnc(runpath="tests/test_run/",
                    mod_def=grid,
                    forcing_field="WINDS",
                    forcing_grid_latlon=True,
                    file_filename="tests/test_data/Era5_2010_01_winds_2days.nc",
                    file_longitude="longitude",
                    file_latitude="latitude",
                    file_var_1="u10",
                    file_var_2="v10",
                    forcing_timestart=datetime.datetime(2010, 1, 1),
                    forcing_timestop=datetime.datetime(2010, 1, 1, 2))

        W.reverse_latitudes("reversed_winds.nc")
        W.to_file()
        W.run()
        assert W.returncode == 0

    # test ice concentration from ECMWF
    def test_Era5_ice_conc(self):

        # download data
        get_data("ice", "tests/test_data/Era5_2010_01_ice_2days.nc")

        # search for a grid
        grid = "tests/test_run/mod_def.ww3"
        if not os.path.isfile(grid):
            get_grid(grid)

        W = WW3Prnc(runpath="tests/test_run/",
                    mod_def=grid,
                    forcing_field="ICE_CONC",
                    forcing_grid_latlon=True,
                    file_filename="tests/test_data/Era5_2010_01_ice_2days.nc",
                    file_longitude="longitude",
                    file_latitude="latitude",
                    file_var_1="siconc",
                    forcing_timestart=datetime.datetime(2010, 1, 1),
                    forcing_timestop=datetime.datetime(2010, 1, 1, 2))

        W.reverse_latitudes("reversed_ice.nc")
        W.to_file()
        W.run()
        assert W.returncode == 0
