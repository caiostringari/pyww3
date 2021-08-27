"""
tests.test_bounc.py
~~~~~~~~~~~~~~~~~~~~

Test pyww3.bounc.WW3Bounc.
"""
import pytest
from pyww3.bounc import WW3Bounc


class TestWW3Bounc:

    @pytest.mark.skip(reason="This test fails due to a ww3_bounc bug. "
                             "ww3_bounc cannot process a file with multiple locations in it.")
    def test_WW3Bounc_file(self):

        W = WW3Bounc(runpath="tests/test_run/",
                     mod_def="tests/test_data/GLOB_60M_mod_def.ww3",
                     bound_file="tests/test_run/spc/ww3.201001_spec.nc")
        W.to_file()
        W.run()

        assert W.returncode == 0

    def test_WW3Bounc_path(self):

        W = WW3Bounc(runpath="tests/test_run/",
                     mod_def="tests/test_data/GLOB_60M_mod_def.ww3",
                     bound_file="tests/test_run/spc")
        W.to_file()
        W.run()

        assert W.returncode == 0
