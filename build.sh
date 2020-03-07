#! /bin/bash

# doesn't work on Windows
# we assume we always launch the script
# from its parent directory
cd "${0%/*}"

git submodule init
git submodule update

# very ugly, see https://github.com/joerick/cibuildwheel/issues/289
if [[ $TRAVIS_OS_NAME = 'windows' ]]; then
    pip install Cython numpy
fi

rm -rf tempbuild
mkdir tempbuild
cd tempbuild
cmake -DBUILD_DIVSUFSORT64=ON -DBUILD_EXAMPLES=OFF -DUSE_OPENMP=ON $PLATFORM_OPTION ../libdivsufsort
if [[ $TRAVIS_OS_NAME = 'windows' ]]; then
    cmake --build . --config Release
    OUTPATH="tempbuild/examples/Release/divsufsort"
else
    make
    OUTPATH="tempbuild/lib/libdivsufsort"
fi
cd ..

# copy the two largest files, aka the dll of divsufsort and divsufsort64
mv $(du $OUTPATH* | sort -nr | head -n2 | cut -f2) pydivsufsort
rm -rf tempbuild

