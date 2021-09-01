# pyww3

[![Documentation Status](https://readthedocs.org/projects/pyww3/badge/?version=latest)](https://pyww3.readthedocs.io/en/latest/?badge=latest) [![PyPI version](https://badge.fury.io/py/pyww3.svg)](https://badge.fury.io/py/pyww3)

Python wrapper for NOAA's WaveWatchIII (WW3) Model.

This package wraps around the WW3's executables by properly defining the namelists (``.nml``) required to drive the model's executables.

**Warning:** This is very much work-in-progress and the API is not stable. Use at your own risk.


## Requirements


``pyww3`` requires ``WaveWatchIII`` to be properly compiled with `netCDF4` available in your ``$PATH``. Please follow the installation instructions from [NOAA](https://github.com/NOAA-EMC/WW3/wiki/Quick-Start/).


Programs supported: `ww3_grid`, `ww3_prnc`, `ww3_shel`, `ww3_ounf`, `ww3_ounp` and `ww3_bounc`.

Note that I don't have plans to support programs that require ASCII input (such as `ww3_outf`) even tough they may have an associated namelist.

You will need `python 3.7+` because of the extensive usage of `dataclasses`.


## Getting Started

All the implemented classes have the same structure and methods. For example,
to run simulation with ``ww3_shel`` you do::

```python
import datetime
from pyww3.shel import WW3Shel
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
W.to_file() # writes ww3_shel.nml in the run path
W.run()  # run the simulation
print(W.stdout) # print the output given by WW3
```


## TODO

- Add support for ``ww3_multi`` ?


## Credits

- This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage) project template.

- WW3 is maintained and distributed by NOAA's Environmental Modeling Center (EMC).

## Disclaimer

There is no warranty for the program, to the extent permitted by applicable law except when otherwise stated in writing the copyright holders and/or other parties provide the program “as is” without warranty of any kind, either expressed or implied, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose. the entire risk as to the quality and performance of the program is with you. should the program prove defective, you assume the cost of all necessary servicing, repair or correction.
