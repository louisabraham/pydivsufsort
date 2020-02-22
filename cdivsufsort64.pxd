cdef extern from "<stdint.h>" nogil:

    ctypedef unsigned char  uint8_t
    ctypedef signed int     int32_t
    ctypedef signed long    int64_t


cdef extern from "divsufsort64.h" nogil:
    ctypedef uint8_t sauchar_t
    ctypedef int32_t saint_t
    ctypedef int64_t saidx64_t;

    saint_t divsufsort64(const sauchar_t *T, saidx64_t *SA, saidx64_t n)

