git submodule init
git submodule update

mkdir tempbuild
cd tempbuild
echo "****************************"
echo $CIBW_PLATFORM
echo $CIBW_ARCHS
echo $CIBW_ENVIRONMENT
echo "****************************"
cmake -DBUILD_DIVSUFSORT64=ON -DBUILD_EXAMPLES=OFF -DUSE_OPENMP=ON $PLATFORM_OPTION ../libdivsufsort
if [ "$RUNNER_OS" == "Windows" ]; then
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
