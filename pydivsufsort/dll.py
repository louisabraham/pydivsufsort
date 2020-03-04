from pathlib import Path
import ctypes
import platform

PATH = Path(__file__).parent

print("----------")
print(platform.system())
print("----------")

if platform.system() == "Windows":
    PATH_LIBDIVSUFSORT = str(next(PATH.glob("divsufsort.dll"))).replace("\\", r"\\")
    PATH_LIBDIVSUFSORT64 = str(next(PATH.glob("divsufsort64.dll"))).replace("\\", r"\\")
    print(PATH_LIBDIVSUFSORT, PATH_LIBDIVSUFSORT64)
else:
    PATH_LIBDIVSUFSORT = next(PATH.glob("libdivsufsort.*"))
    PATH_LIBDIVSUFSORT64 = next(PATH.glob("libdivsufsort64.*"))

libdivsufsort = ctypes.CDLL(PATH_LIBDIVSUFSORT)
libdivsufsort64 = ctypes.CDLL(PATH_LIBDIVSUFSORT64)
