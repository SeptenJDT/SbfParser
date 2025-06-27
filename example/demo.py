#!/usr/bin/env python3
import os
from sbf_parser import SbfParser, load

print("Read file using fobj :")
with open("log 1.sbf", "rb") as fobj:
    for block_desc, infos in load(fobj):
        print("\t", block_desc, infos.get("TOW", None))
print("")


