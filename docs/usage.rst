=====
Usage
=====

The main goal of ``pyww3`` is programmatically to provide access to the
parameters that the user has to manually input the WW3 `namelist files`_.

.. _namelist files: https://github.com/NOAA-EMC/WW3/tree/develop/model/nml


For example, if a namelist defines the following:

.. code-block::

    &SPECTRUM_NML
      SPECTRUM%XFR           =  1.1
      SPECTRUM%FREQ1         =  0.04118
      SPECTRUM%NK            =  32
      SPECTRUM%NTH           =  24
    /

You are able to write the same in python as:

.. code-block:: python

    spectrum_xfr: int = 1.1
    spectrum_freq1: int = 0.04118
    spectrum_nk: int = 32
    spectrum_thoff: int = 0


All ``pyww3`` classes use `type hinting`_ and all parameters are converted to the strings
that WW3 is expecting. Data validation is done in the ``__post_init__``
method of each class. The checks include searching for required files and, for
some parameters, checking if the inputs are compatible to the namelist definitions.

.. _type hinting: https://docs.python.org/3/library/typing.html


All classes inherit from ``WW3Base``. This class
implements the methods ``to_file()`` which writes the namelist text to file, ``run()``
which runs a given program and ``update_text()`` which can be used to manipulate
the namelist text ad-hoc. Each class implements the method ``populate_namelist()``
that generates the namelist text.


WW3Grid
-------

Program used to create grids. Only regular spherical grids and unstructured
meshes were tested.

Example:

.. code-block:: python

    from pyww3.grid import WW3Grid

    # dictionary with grid information. This is normally read from a JSON file.
    grid_info = {"grid_nml": "GLOB_60_MIN.nml",
                 "grid_name": "GLOB_60M",
                 "grid_type":"RECT",
                 "grid_coord":"SPHE",
                 "grid_clos": "NONE",
                 "rect_nx": 360,
                 "rect_ny": 157,
                 "rect_sx": 1.0,
                 "rect_sy": 1.0,
                 "rect_sf": 1.0,
                 "rect_x0": -180.0,
                 "rect_y0": -78.0,
                 "rect_sf0" :1.0,
                 "grid_zlim": -0.1,
                 "grid_dmin": 2.5,
                 "depth_filename": "GLOB_60_MIN.depth_ascii",
                 "depth_sf": 0.0010,
                 "obst_filename": "GLOB_60_MIN.obstr_lev1",
                 "obst_sf": 0.010,
                 "mask_filename": "GLOB_60_MIN.maskorig_ascii"}

    # create the instance
    W = WW3GRid(runpath="some/valid/path/",
                grid_name=grid_info["grid_type"],
                grid_nml=grid_info["grid_nml"],
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

    # Update the timesteps. Don't forget to update the namelist text!
    W.timesteps_dtmax = 480.0 * 3
    W.timesteps_dtxy = 160.0 * 3
    W.timesteps_dtkth = 240.0 * 3
    W.timesteps_dtmin = 10.0 * 3
    W.text = W.populate_namelist()

    # write ww3_grid.namelist in the `runpath`.
    W.to_file()

    # run `ww3_grid` in the `runpath`.
    W.run()


WW3Bounc
--------

Program used to post-process spectral netcdf files generated with ``ww3_ounp``.
Usually used to created boundary conditions to a nested simulation.

Example:

.. code-block:: python

    from pyww3.bounc import WW3Bounc

    # create the instance
    W = WW3Bounc(runpath="some/valid/path/",
                 mod_def="mod_def.ww3",
                 bound_file="somefile.nc")

    # write ww3_bounc.namelist in the `runpath`.
    W.to_file()

    # run `ww3_bounc` in the `runpath`.
    W.run()
