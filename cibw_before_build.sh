python -m pip install --upgrade pip
python -m pip uninstall numpy
#python -m pip install --only-binary=:all: numpy==1.19.5
python -m pip install oldest-supported-numpy
python -m pip install -r requirements.txt
python -m pip install flake8 pytest
git submodule init
git submodule update

mkdir tempbuild
cd tempbuild
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
