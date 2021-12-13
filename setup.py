#!/usr/bin/env python3

from pathlib import Path
import platform
from subprocess import Popen
from setuptools import setup
from setuptools import Extension
from distutils.command.build import build as _build
from distutils.command.install import install as _install
from Cython.Build import cythonize

import numpy

# make the wheel platform specific
# https://stackoverflow.com/a/45150383
try:
    from wheel.bdist_wheel import bdist_wheel as _bdist_wheel

    class bdist_wheel(_bdist_wheel):
        def finalize_options(self):
            _bdist_wheel.finalize_options(self)
            self.root_is_pure = False


except ImportError:
    bdist_wheel = None


class build(_build):
    def run(self):
        if platform.system() == "Windows":
            witness = Path(__file__).parent / "pydivsufsort/divsufsort.dll"
            assert witness.exists(), "Launch ./build.sh first"
        else:
            script = Path(__file__).parent / "build.sh"
            path = script.absolute().as_posix()
            Popen([path], shell=True, executable="/bin/bash").wait()
        super().run()


# idk why this is required for build to execute
class install(_install):
    def run(self):
        super().run()


def read(fname):
    return (Path(__file__).parent / fname).open().read()


extensions = [
    Extension(
        "pydivsufsort.stringalg",
        ["pydivsufsort/stringalg.pyx"],
        include_dirs=[numpy.get_include()],
        # language="c++",
    )
]

setup(
    name="pydivsufsort",
    version="0.0.6",  #
    author="Louis Abraham",
    license="MIT",
    author_email="louis.abraham@yahoo.fr",
    description="String algorithms",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/louisabraham/pydivsufsort",
    packages=["pydivsufsort"],
    package_data={
        "pydivsufsort": [
            # unix
            "libdivsufsort.*",
            "libdivsufsort64.*",
            # windows
            "divsufsort.dll",
            "divsufsort64.dll",
        ]
    },
    ext_modules=cythonize(extensions),
    python_requires=">=3.6",
    install_requires=["wheel", "numpy"],
    tests_require=["pytest"],
    classifiers=[],
    cmdclass={"build": build, "bdist_wheel": bdist_wheel, "install": install},
)
