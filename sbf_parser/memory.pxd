# memory.pxd
from libc.stdint cimport uint8_t, uint64_t
from libc.stdio cimport FILE

cdef struct Memory:
    size_t last_decoded
    size_t current
    size_t length
    uint8_t data[2000000]

cdef void memory_clear(Memory *mem)
cdef void memory_compact(Memory *mem)
cdef int memory_save_to_file(Memory *mem, FILE *fp)
cdef int memory_load_from_file(Memory *mem, FILE *fp)
