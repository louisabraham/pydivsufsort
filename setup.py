#!/usr/bin/env python3

import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


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
)

