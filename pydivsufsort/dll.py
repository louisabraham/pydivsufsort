from pathlib import Path
import ctypes

PATH = Path(__file__).parent

PATH_LIBDIVSUFSORT = next(PATH.glob("libdivsufsort.so*"))
PATH_LIBDIVSUFSORT64 = next(PATH.glob("libdivsufsort64.so*"))

libdivsufsort = ctypes.CDLL(PATH_LIBDIVSUFSORT)
libdivsufsort64 = ctypes.CDLL(PATH_LIBDIVSUFSORT64)
