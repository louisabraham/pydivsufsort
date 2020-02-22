cimport cdivsufsort64 as c

cdef c.uint8_t inp[10];
for i in range(10):
    inp[i] = i

cdef c.saidx64_t out[10];


print(c.divsufsort64(inp, out, 10))
print(out)
