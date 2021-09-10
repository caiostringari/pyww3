"""
tests.test_grid.py
~~~~~~~~~~~~~~~~~~~~

Test pyww3.grid.WW3Grid.
"""
import os
import json
import pytest
from pyww3.grid import WW3GRid


class TestWW3Grid:

    def test_global_grid(self):

        datapath = "tests/test_data/"
        runpath = "tests/test_run/"
        grid_name = "GLOB_60_MIN"
        with open(os.path.join(datapath, f'{grid_name}.json')) as f:
            grid_info = json.load(f)

        W = WW3GRid(runpath=runpath,
                    grid_name=grid_info["grid_name"],
                    grid_nml=os.path.join(datapath, grid_info["grid_nml"]),
                    grid_type=grid_info["grid_type"],
                    grid_coord=grid_info["grid_coord"],
                    grid_clos=grid_info["grid_clos"],
                    rect_nx=grid_info["rect_nx"],
                    rect_ny=grid_info["rect_ny"],
                    rect_sx=grid_info["rect_sx"],
                    rect_sy=grid_info["rect_sy"],
                    rect_sf=grid_info["rect_sf"],
                    rect_x0=grid_info["rect_x0"],
                    rect_y0=grid_info["rect_y0"],
                    rect_sf0=grid_info["rect_sf0"],
                    grid_zlim=grid_info["grid_zlim"],
                    grid_dmin=grid_info["grid_dmin"],
                    depth_filename=os.path.join(datapath, grid_info["depth_filename"]),
                    depth_sf=grid_info["depth_sf"],
                    obst_filename=os.path.join(datapath, grid_info["obst_filename"]),
                    obst_sf=grid_info["obst_sf"],
                    mask_filename=os.path.join(datapath, grid_info["mask_filename"]))

        # update namelist blocks that could cause errors.
        W.update_text("&SED_NML", action="remove")
        W.update_text("&SLOPE_NML", action="remove")
        W.update_text("&CURV_NML", action="remove")
        W.update_text("&UNST_NML", action="remove")

        W.timesteps_dtmax = 480.0 * 3
        W.timesteps_dtxy = 160.0 * 3
        W.timesteps_dtkth = 240.0 * 3
        W.timesteps_dtmin = 10.0 * 3
        W.text = W.populate_namelist()
        # W.populate_namelist()

        # print(W)

        W.to_file()
        W.run()

        assert W.returncode == 0

    @pytest.mark.skip(reason="I want only to test the global grid here.")
    def test_unstruc_grid(self):
        datapath = "tests/test_data/"
        grid_name = "UNSTRUCT_BR"
        with open(os.path.join(datapath, f'{grid_name}.json')) as f:
            grid_info = json.load(f)

        W = WW3GRid(runpath="tests/test_run/",
                    grid_name=grid_info["grid_name"],
                    grid_nml=os.path.join(datapath, grid_info["grid_nml"]),
                    grid_type=grid_info["grid_type"],
                    grid_coord=grid_info["grid_coord"],
                    grid_clos=grid_info["grid_clos"],
                    unst_sf=grid_info["unst_sf"],
                    unst_filename=os.path.join(datapath, grid_info["unst_filename"]),
                    unst_idla=grid_info["unst_idla"],
                    unst_idfm=grid_info["unst_idfm"],
                    unst_format=grid_info["unst_format"])

        # update namelist blocks that could cause errors.
        W.update_text("&SED_NML", action="remove")
        W.update_text("&SLOPE_NML", action="remove")
        W.update_text("&OBST_NML", action="remove")
        W.update_text("&MASK_NML", action="remove")
        W.update_text("&DEPTH_NML", action="remove")
        W.update_text("&CURV_NML", action="remove")
        W.update_text("&RECT_NML", action="remove")

        W.to_file()
        W.run()

        assert W.returncode == 0
