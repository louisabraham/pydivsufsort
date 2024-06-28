#!/usr/bin/env python3


import os
import platform
from setuptools.command.build_py import build_py
from pathlib import Path
from subprocess import Popen
import sysconfig

import numpy
from Cython.Build import cythonize
from setuptools import Extension, setup

PROFILE = os.environ.get("PROFILE", False)

if PROFILE:
    from Cython.Compiler.Options import get_directive_defaults

    directive_defaults = get_directive_defaults()
    directive_defaults["linetrace"] = True
    directive_defaults["binding"] = True


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


class CustomBuildPy(build_py):
    def run(self):
        if platform.system() == "Windows":
            witness = Path(__file__).parent / "pydivsufsort/divsufsort.dll"
            assert witness.exists(), "Launch ./build.sh first"
        elif platform.system() == "Darwin":
            script = Path(__file__).parent / "build.sh"
            path = script.absolute().as_posix()
            mach = sysconfig.get_platform()
            print("Building for", mach, platform.machine())
            if mach.endswith("x86_64"):
                arch = "x86_64"
            elif mach.endswith("arm64"):
                arch = "arm64"
            else:
                # support universal2
                arch = platform.machine()
            Popen(
                [path],
                shell=False,
                env={
                    **os.environ,
                    "PLATFORM_OPTION": "-DCMAKE_OSX_ARCHITECTURES=" + arch,
                },
            ).wait()
        else:
            script = Path(__file__).parent / "build.sh"
            path = script.absolute().as_posix()
            Popen([path], shell=True, executable="/bin/bash").wait()
        super().run()


def read(fname):
    return (Path(__file__).parent / fname).open().read()


extensions = [
    Extension(
        "pydivsufsort.stringalg",
        ["pydivsufsort/stringalg.pyx"],
        include_dirs=[numpy.get_include()],
        language="c++",
        define_macros=[("CYTHON_TRACE", "1")] if PROFILE else None,
    )
]

setup(
    name="pydivsufsort",
    version="0.0.14",
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
    cmdclass={"build_py": CustomBuildPy, "bdist_wheel": bdist_wheel},
)
