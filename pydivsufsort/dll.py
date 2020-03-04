from pathlib import Path
import ctypes
import platform

PATH = Path(__file__).parent

if platform.system() == "Windows":
    find_dll = lambda x: str(next(PATH.glob(x)))
    PATH_LIBDIVSUFSORT = find_dll("divsufsort.dll")
    PATH_LIBDIVSUFSORT64 = find_dll("divsufsort64.dll")
else:
    PATH_LIBDIVSUFSORT = next(PATH.glob("libdivsufsort.*"))
    PATH_LIBDIVSUFSORT64 = next(PATH.glob("libdivsufsort64.*"))

libdivsufsort = ctypes.CDLL(PATH_LIBDIVSUFSORT)
libdivsufsort64 = ctypes.CDLL(PATH_LIBDIVSUFSORT64)
