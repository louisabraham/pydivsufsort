#! /bin/bash

cd "${0%/*}"

git submodule init
git submodule update

rm -rf tempbuild
mkdir tempbuild
cd tempbuild
cmake -DBUILD_DIVSUFSORT64=ON -DBUILD_EXAMPLES=OFF -DUSE_OPENMP=ON ../libdivsufsort
make
cd ..
# copy the two largest files, aka the dll of libdivsufsort and libdivsufsort64
mv $(du tempbuild/lib/libdivsufsort* | sort -nr | head -n2 | cut -f2) pydivsufsort
rm -rf tempbuild
