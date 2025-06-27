#!/usr/bin/env python3
import os
import sbf_parser
from sbf_parser import load

def get_binary_file(filename):
    with open(filename, "rb") as f:
        return f.read()


# Generate example file
with open("./local_files/test.sbf", "wb") as fobj:
    fobj.write(
        b'abcdefg$Rreplie$Ttransmission\nSSSSSSSSSS\n\nNothing$-description$&snmp$@badsbfblock'
    +   get_binary_file("../sbf_files/receiver_status.sbf")
    )


"""
# Summary :
def read(path)
def load(fobj)
def parse(bytearray)
"""

print("Read file using path :")
for block_desc, infos in sbf_parser.read("./local_files/test.sbf"):
    print("\t", block_desc, infos)
print("")


print("Read file using fobj :")
with open("local_files/test.sbf", "rb") as fobj:
    for block_desc, infos in sbf_parser.load(fobj):
        print("\t", block_desc, infos)
print("")


print("Read binary :")
with open("local_files/test.sbf", "rb") as fobj:
    binary = fobj.read()

    for block_desc, infos in sbf_parser.parse(binary):
        print("\t", block_desc, infos)
print("")

