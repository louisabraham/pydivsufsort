#! /bin/sh

rm -rf libdivsufsort
mkdir libdivsufsort
curl -L https://github.com/y-256/libdivsufsort/tarball/master | tar xz --strip-components=1 -C libdivsufsort
mkdir build
cd build
cmake -DBUILD_DIVSUFSORT64=ON -DBUILD_EXAMPLES=OFF ../libdivsufsort
make
cd ..
# copy the two largest files, aka the dll of libdivsufsort and libdivsufsort64
mv $(du build/lib/libdivsufsort* | sort -nr | head -n2 | cut -f2) pydivsufsort
rm -rf build libdivsufsort
