cimport numpy as np

cdef extern from "divsufsort64.h" nogil:
    np.int32_t divsufsort64(const np.uint8_t *T, np.int64_t *SA, np.int64_t n)

