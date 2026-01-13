import sys
import os
import os.path
try:
    if sys.version_info[0] == 2:
        try:
            from distutils.core import setup
            from distutils.extension import Extension
        except ImportError:
            from setuptools import setup, Extension
    else:
        from setuptools import setup, Extension
except ImportError:
    print("Error: setuptools or distutils not found. Please install setuptools:")
    print("    pip install setuptools")
    sys.exit(1)

import pybind11
import numpy
import pkgconfig
import shlex

try:
    cvmfs_env_root=os.environ['SROOT']
except KeyError:
    cvmfs_env_root="/usr/local/"

try:
    env_prefix=os.environ['PREFIX']
except KeyError:
    env_prefix="/usr/local/"

if sys.platform == 'win32' or sys.platform == 'win64':
    print('Windows is not a supported platform.')
    quit()
else:
    include_dirs = [
            '../../public/',
            numpy.get_include(),
            pybind11.get_include(),
            env_prefix+'/include',
            cvmfs_env_root + "/include/",
            cvmfs_env_root + "/include/hdf5/serial/",
            ]
    if sys.version[0]=='3':
        libraries = [
                'python{}m'.format(sys.version[0:3]),
                'LeptonWeighter',
                ]
    elif sys.version[0]=='2':
         libraries = [
                'python{}'.format(sys.version[0:3]),
                'LeptonWeighter',
                ]
    else:
        raise Exception("Python version {} not supported".format(sys.version[0]))
    library_dirs = [
            '../lib/',
            env_prefix+'/lib/',
            env_prefix+'/lib64/',
            cvmfs_env_root + "/lib/",
            cvmfs_env_root + "/lib64/",
            ]

    files = ['lepton_weighter_pybind11.cpp']

setup(name = 'LeptonWeighter', author = "Carlos A. Arguelles",
        ext_modules = [
            Extension('LeptonWeighter',files,
                library_dirs=library_dirs,
                libraries=libraries,
                include_dirs=include_dirs,
                extra_compile_args=['-O3','-fPIC','-std=c++11'] + shlex.split(pkgconfig.cflags('squids')) + shlex.split(pkgconfig.cflags('nusquids')) + shlex.split(pkgconfig.cflags('cfitsio')),
                extra_link_args=shlex.split(pkgconfig.libs('squids')) + shlex.split(pkgconfig.libs('nusquids')) + shlex.split(pkgconfig.libs('cfitsio')),
                depends=[]),
            ]
        )

