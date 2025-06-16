#!/usr/bin/env python3
import os
from sbf_parser import SbfParser

def get_binary_file(filename):
    with open(filename, "rb") as f:
        return f.read()


# Generate binary input
binary = get_binary_file("../sbf_files/receiver_status.sbf")
n = len(binary) // 2


# Init parser to use memory functionality
parser = SbfParser()

print("Read first half of the block:")
for block_info, infos in parser.parse(binary[0:n]):
    print("\t", block_info, infos)
print("End.")
print()


# Save memory and restore memory to another parser.
# This can be used if you need to save memory between two different calls on your python function

parser.save_memory("./local_files/memory.bin")
parser.clear_memory() # If you want to clear memory

parser2 = SbfParser()
parser2.load_memory("./local_files/memory.bin")
parser2.memory_infos()

print("Read second half of the block:")
for block_info, infos in parser2.parse(binary[n::]):
    print("\t", block_info, infos)
print("End.")
print()

