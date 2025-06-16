# Created by Louis-Max Harter 2025

# type: ignore 
# memory.pyx
from libc.stdio cimport FILE, fopen, fclose, fwrite, fread, fflush
from libc.stdlib cimport malloc, free
from libc.string cimport memcpy, memmove
from libc.stdint cimport uint8_t
from .memory cimport *


cdef struct Memory:
    size_t last_decoded
    size_t current
    size_t length
    uint8_t data[2000000] # 2MB

cdef void memory_clear(Memory *mem):
    mem.last_decoded = 0
    mem.current = 0
    mem.length = 0

cdef void memory_compact(Memory *mem):
    if mem.last_decoded == 0:
        return

    cdef size_t remaining = mem.length - mem.last_decoded

    memcpy(mem.data, mem.data + mem.last_decoded, remaining)
    mem.current -= mem.last_decoded
    mem.length = remaining
    mem.last_decoded = 0

cdef int memory_save_to_file(Memory *mem, FILE *fp):
    if fwrite(&mem.last_decoded, sizeof(size_t), 1, fp) != 1:
        return 1
    if fwrite(&mem.current, sizeof(size_t), 1, fp) != 1:
        return 2
    if fwrite(&mem.length, sizeof(size_t), 1, fp) != 1:
        return 3
    if fwrite(mem.data, sizeof(uint8_t), mem.length, fp) != mem.length:
        return 4
    if fflush(fp):
        return 5
    return 0

cdef int memory_load_from_file(Memory *mem, FILE *fp):
    if fread(&mem.last_decoded, sizeof(size_t), 1, fp) != 1:
        return 1
    if fread(&mem.current, sizeof(size_t), 1, fp) != 1:
        return 2
    if fread(&mem.length, sizeof(size_t), 1, fp) != 1:
        return 3
    if fread(mem.data, sizeof(uint8_t), mem.length, fp) != mem.length:
        return 4
    return 0


