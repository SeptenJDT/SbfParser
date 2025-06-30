#!/usr/bin/env python3
import argparse
import sys
from sbf_parser import encode, replace_header_time

class WideArgumentDefaultsHelpFormatter(argparse.ArgumentDefaultsHelpFormatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, width=140, **kwargs)


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Replace header time in SBF files with configurable parameters. "
                   "This tool processes SBF (Septentrio Binary Format) files and "
                   "modifies the time-of-week (TOW) values in selected block types.",
        formatter_class=WideArgumentDefaultsHelpFormatter,
    )
    
    parser.add_argument("input_file", help="Input SBF file path")
    parser.add_argument("-o", "--output", default="output.sbf", help="Output SBF file path")
    parser.add_argument("-s", "--start-time", type=int, default=0, help="Start time in milliseconds")
    parser.add_argument("-d", "--duration", type=int, default=0, help="Target duration in milliseconds (0 = keep original duration)")
    parser.add_argument("-G", "--max-gap", type=int, default=1500, help="Maximum gap between blocks in milliseconds")
    parser.add_argument("-g", "--min-gap", type=int, default=1, help="Minimum gap between blocks in milliseconds")
    parser.add_argument("-dg", "--default-gap", type=int, default=1000, help="Default gap between blocks in milliseconds")
    parser.add_argument("--blocks", default=["BBSamples", "ReceiverStatus"], help="Block types to process")
    
    """
    python replace_header_time.py input.sbf -o processed.sbf -s 100000 -d 30000 -G 2000 -g 100 -dg 1200 --blocks BBSamples+ReceiverStatus"
    """
    args = parser.parse_args()
    blocks_names = args.blocks.split("+")


    # Update header time
    sbf_out = replace_header_time(args.input_file, blocks_names, args.start_time, args.duration, args.max_gap, args.min_gap, args.default_gap)

    # Writing blocks
    with open(args.output, "wb") as fobj:
        for block in sbf_out:
            result, binary = encode(block, payload_priority=0)  # Never use payload
            
            if result != "encoded":
                print(f"Warning: Encoding returned {result} on block {block}")
            fobj.write(binary)


    print("Done.")
    print(f"Output file: {args.output}")
    

if __name__ == "__main__":
    main()