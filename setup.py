#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('docs/readme.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['netcdf4', 'xarray']

test_requirements = ['pytest>=3.7', ]

setup(
    author="Caio Stringari",
    author_email='caio.stringari@gmail.com',
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Python wrapper for NOAA's WaveWatchIII Model",
    entry_points={
        'console_scripts': [
            'pyww3=pyww3.cli:main',
        ],
    },
    install_requires=requirements,
    license="GNU General Public License v3.0",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords=['Wavewatch', "WW3"],
    name='pyww3',
    packages=find_packages(),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/caiostringari/pyww3',
    version='0.1.4',
    zip_safe=False,
)
