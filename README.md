1. Install <https://github.com/y-256/libdivsufsort/> with the option `-DBUILD_DIVSUFSORT64=ON`
2.
``` bash
python setup.py build_ext -i
```
3.
``` bash
LD_LIBRARY_PATH=/usr/local/lib python example.py
```
