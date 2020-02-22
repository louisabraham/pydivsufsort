from setuptools import setup
from setuptools.extension import Extension
from Cython.Build import cythonize

setup(
    ext_modules = cythonize([Extension("pydivsufsort", ["pydivsufsort.pyx"],
                                       libraries=["divsufsort64"])])
)

