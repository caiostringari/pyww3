# pyww3

[![Documentation Status](https://readthedocs.org/projects/pyww3/badge/?version=latest)](https://pyww3.readthedocs.io/en/latest/?badge=latest) [![PyPI version](https://badge.fury.io/py/pyww3.svg)](https://badge.fury.io/py/pyww3) [![CircleCI](https://circleci.com/gh/caiostringari/pyww3/tree/main.svg?style=svg)](https://circleci.com/gh/caiostringari/pyww3/tree/main)

Python wrapper for NOAA's WaveWatchIII (WW3) Model.

This package wraps around the WW3's executables by properly defining the namelists (``.nml``) required to drive the model's executables.

**Warning:** This is very much work-in-progress and the API is not stable. Use at your own risk.


## Requirements


``pyww3`` requires ``WaveWatchIII`` to be properly compiled with `netCDF4` available in your ``$PATH``. Please follow the installation instructions from [NOAA](https://github.com/NOAA-EMC/WW3/wiki/Quick-Start/).


Programs supported: `ww3_grid`, `ww3_prnc`, `ww3_shel`, `ww3_ounf`, `ww3_ounp` and `ww3_bounc`.

Note that I don't have plans to support programs that require ASCII input (such as `ww3_outf`) even tough they may have an associated namelist.

You will need `python 3.7+` because of the extensive usage of `dataclasses`.

The only python dependency is `xarray` with `netcdf` support. `pip install netcdf4 xarray` should be enough to get you going.


## Getting Started


### Installation:

```bash
pip install pyww3
```

Development mode:

```
git clone git://github.com/caiostringari/pyww3
cd pyww3
pip install -e .
```

Runnig all tests:

```
pytest
```

Individual tests:

- `ww3_grid` with `pytest tests/test_01_grid.py`
- `ww3_prnc` with `pytest tests/test_02_prnc.py`
- `ww3_shel` with `pytest tests/test_03_shel.py`
- `ww3_ounf` with `pytest tests/test_04_ounf.py`
- `ww3_ounp` with `pytest tests/test_05_ounp.py`
- `ww3_bounc` with `pytest tests/test_06_bounc.py`


## Documentation

[**READTHEDOCS**](https://pyww3.readthedocs.io/en/latest/)

**Note:** I am still documenting everything.

## Examples:

**Global Simulation ↦** [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1Py-aMvTMxDiyjpPXBoIe5eQx8iRm47zF?usp=sharing)


## TODO

- Add the documentation (working in progress)
- Add support for ``ww3_multi`` ?


## Credits

- This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage) project template.

- WW3 is maintained and distributed by NOAA's Environmental Modeling Center (EMC).

## Disclaimer

There is no warranty for the program, to the extent permitted by applicable law except when otherwise stated in writing the copyright holders and/or other parties provide the program “as is” without warranty of any kind, either expressed or implied, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose. the entire risk as to the quality and performance of the program is with you. should the program prove defective, you assume the cost of all necessary servicing, repair or correction.
