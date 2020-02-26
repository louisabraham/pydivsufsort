#! /bin/sh

rm -rf libdivsufsort
mkdir libdivsufsort
curl -L https://github.com/y-256/libdivsufsort/tarball/master | tar xz --strip-components=1 -C libdivsufsort
rm -rf tempbuild
mkdir tempbuild
cd tempbuild
cmake -DBUILD_DIVSUFSORT64=ON -DBUILD_EXAMPLES=OFF ../libdivsufsort
make
cd ..
# copy the two largest files, aka the dll of libdivsufsort and libdivsufsort64
mv $(du tempbuild/lib/libdivsufsort* | sort -nr | head -n2 | cut -f2) pydivsufsort
rm -rf tempbuild libdivsufsort
