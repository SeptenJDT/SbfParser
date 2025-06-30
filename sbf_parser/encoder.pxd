# Initial code by Louis-Max (2023)
# Based on the sbfPythonParser by Jashandeep Sohi, Marco Job, and Meven Jeanne-Rose

from libc.stdint cimport uint8_t, uint16_t, uint32_t, uint64_t, int8_t, int16_t, int32_t, int64_t
from libc.stdlib cimport malloc, free
from libc.string cimport memcpy, memset
from libc.stdio cimport FILE, fwrite, fopen, fclose

ctypedef uint8_t u1
ctypedef uint16_t u2
ctypedef uint32_t u4
ctypedef uint64_t u8
ctypedef int8_t i1
ctypedef int16_t i2
ctypedef int32_t i4
ctypedef int64_t i8
ctypedef float f4
ctypedef double f8
ctypedef char c1

# SBF header structure (matching the one in sbf.pyx)
cdef struct Header:
    uint16_t Sync
    uint16_t CRC
    uint16_t ID
    uint16_t Length

# Helper functions
cdef dict type_to_format 

cdef extern from "c_crc.h":
    uint16_t crc16(const void*, size_t, uint16_t)
