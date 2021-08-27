"""
tests.test_ounp.py
~~~~~~~~~~~~~~~~~~~~

Test suite for the ounp program abstraction.
"""

import datetime

from pyww3.ounp import WW3Ounp


class TestWW3Ounp:

    def test_ounf_single_file(self):

        W = WW3Ounp(runpath="tests/test_run/",
                    mod_def="tests/test_data/GLOB_60_MIN.ww3grid",
                    ww3_pnt="tests/test_run/out_pnt.ww3",
                    point_timestart=datetime.datetime(2010, 1, 1),
                    point_timestride=3600)
        W.to_file()
        W.run()

        assert W.returncode == 0

    def test_ounf_separated_files(self):

        W = WW3Ounp(runpath="tests/test_run/",
                    mod_def="tests/test_data/GLOB_60_MIN.ww3grid",
                    ww3_pnt="tests/test_run/out_pnt.ww3",
                    point_timestart=datetime.datetime(2010, 1, 1),
                    point_timestride=3600,
                    point_samefile=False,
                    file_prefix="spc/ww3.")
        W.to_file()
        W.run()

        assert W.returncode == 0
