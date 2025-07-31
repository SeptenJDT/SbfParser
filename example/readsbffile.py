import argparse
import os
from sbf_parser import SbfParser, load

parser = argparse.ArgumentParser(description="Parse an SBF (Septentrio Binary Format) file.")
parser.add_argument(
    "sbf_file",
    type=str,
    help="Path to the SBF file to be parsed"
)
args = parser.parse_args()

# Example usage
print(f"Parsing file: {args.sbf_file}")
# You can call your actual parsing function here
print("Read file using fobj :")
with open(args.sbf_file, "rb") as fobj:
    for block_desc, infos in load(fobj):
        #print("\t", block_desc, infos.get("TOW", None))
        print(infos)
        print("\n")
