#! /bin/bash
set -e

# doesn't work on Windows
# we assume we always launch the script
# from its parent directory
cd "${0%/*}"

if git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    git submodule init
    git submodule update
fi

rm -rf tempbuild
mkdir tempbuild
cd tempbuild
cmake -DBUILD_DIVSUFSORT64=ON -DBUILD_EXAMPLES=OFF -DUSE_OPENMP=ON -DCMAKE_POLICY_VERSION_MINIMUM=3.5 $PLATFORM_OPTION ../libdivsufsort

# test if we are on Windows
if [ -n "$WINDIR" ]; then
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

