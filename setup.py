#!/usr/bin/env python3

from pathlib import Path
from subprocess import Popen
from setuptools import setup
from distutils.command.build import build as _build
from distutils.command.install import install as _install

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
        script = Path(__file__).parent / "build.sh"
        Popen([script.absolute().as_posix()], shell=True, executable="/bin/bash").wait()
        super().run()


# idk why this is required for build to execute
class install(_install):
    def run(self):
        super().run()


def read(fname):    
    return (Path(__file__).parent / fname).open().read()


setup(
    name="pydivsufsort",
    version="0.0",
    author="Louis Abraham",
    license="MIT",
    author_email="louis.abraham@yahoo.fr",
    description="String algorithms",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/louisabraham/pydivsufsort",
    packages=["pydivsufsort"],
    package_data={'pydivsufsort': ['libdivsufsort.so*', 'libdivsufsort64.so*']},
    python_requires=">=3.5",
    classifiers=[],
    cmdclass={'build': build, 'bdist_wheel': bdist_wheel, 'install': install},
)

