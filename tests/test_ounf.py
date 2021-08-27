"""
tests.test_ounf.py
~~~~~~~~~~~~~~~~~~~~

Test pyww3.ounf.WW3Ounf.
"""

import datetime

from pyww3.ounf import WW3Ounf


class TestWW3Ounf:

    def test_ounf(self):

        W = WW3Ounf(runpath="tests/test_run/",
                    mod_def="tests/test_data/GLOB_60_MIN.ww3grid",
                    ww3_grd="tests/test_run/out_grd.ww3",
                    field_timestart=datetime.datetime(2010, 1, 1),
                    field_timestride=3600)
        W.to_file()
        W.run()

        assert W.returncode == 0
