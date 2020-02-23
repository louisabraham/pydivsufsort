from setuptools import setup
from setuptools.extension import Extension
from Cython.Build import cythonize

import numpy

setup(
    ext_modules = cythonize([Extension("pydivsufsort", ["pydivsufsort.pyx"],
                                       libraries=["divsufsort64"],
                                       include_dirs=[numpy.get_include()])])
)

