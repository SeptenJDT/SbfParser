#!/usr/bin/env python3
import os
from sbf_parser import SbfParser

def get_binary_file(filename):
    with open(filename, "rb") as f:
        return f.read()


# Generate binary input
binary = (
    b'abcdefg$Rreplie$Ttransmission\nSSSSSSSSSS\n\nNothing$-description$&snmp$@badsbfblock'
+   get_binary_file("../sbf_files/receiver_status.sbf")
)


# Init parser to use memory functionality
parser = SbfParser()

# You can use parser.read() and parser.load() like in decode.py
chunk_size = 10

print(f"Ready binary of size {len(binary)} by chunk of {chunk_size} bytes")
for i in range(0, len(binary), chunk_size):
    binary_sample = binary[i: i + chunk_size]

    result = parser.parse(binary_sample)
    if result:
        for block_info, infos in result: 
            print("chunk [{:>4}, {:>4}[ :".format(i, i+chunk_size), block_info, infos)
    else:
        print("chunk [{:>4}, {:>4}[ : No new block.".format(i, i+chunk_size))

print("End.")