#!/usr/bin/env python3
import argparse
import sys
import sbf_parser


"""
python replace_header_time.py input.sbf -o processed.sbf -s 100000 -d 30000 -G 2000 -g 100 -dg 1200 --blocks BBSamples ReceiverStatus"
"""


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
    parser.add_argument("-s", "--start-time", type=int, default=130000, help="Start time in milliseconds")
    parser.add_argument("-d", "--duration", type=int, default=0, help="Target duration in milliseconds (0 = keep original duration)")
    parser.add_argument("-G", "--max-gap", type=int, default=1500, help="Maximum gap between blocks in milliseconds")
    parser.add_argument("-g", "--min-gap", type=int, default=1, help="Minimum gap between blocks in milliseconds")
    parser.add_argument("-dg", "--default-gap", type=int, default=1000, help="Default gap between blocks in milliseconds")
    parser.add_argument("--blocks", nargs="+", default=["BBSamples", "ReceiverStatus"], help="Block types to process")
    
    args = parser.parse_args()
    
    # Filter blocks
    selection = []
    analysis = {}
    
    for block_type, infos in sbf_parser.read(args.input_file):
        analysis[block_type] = analysis.get(block_type, 0) + 1

        if block_type in args.blocks:
            selection.append(infos)

    # Analysis
    print("Block decoded:")
    for name, n in sorted(list(analysis.items())):
        print(f"\t{name:20} : {n:4d}")
    print()

    # Check if blocks
    if selection == []:
        print("No blocks in selection")
        sys.exit(1)

    # Calculating deltas
    sbf_out = []
    sbf_out.append(selection[0])
    sbf_out[-1]["TOW"] = args.start_time

    for i in range(1, len(selection)):
        previous_block = sbf_out[-1]
        current_block = selection[i]
        
        delta = current_block["TOW"] - previous_block["TOW"]

        if delta < 0 or delta > args.max_gap:
            delta = args.default_gap
        else:
            delta = max(args.min_gap, delta)
        
        current_block["TOW"] = sbf_out[-1]["TOW"] + delta
        sbf_out.append(current_block)

    # Shrink to target duration if specified
    real_duration = sbf_out[-1]["TOW"] - sbf_out[0]["TOW"]

    if args.duration != 0:
        if real_duration <= 0:
            print(f"Can't shrink duration of {real_duration} to {args.duration}. Try using --min-gap to force non-null duration.")
            sys.exit(1)

        coef = args.duration / real_duration
        start = sbf_out[0]["TOW"]

        for block in sbf_out:
            elapsed = block["TOW"] - start
            block["TOW"] = int(start + elapsed * coef)
        
        print(f"Shrink duration to {args.duration}")

    # Writing blocks
    with open(args.output, "wb") as fobj:
        for block in sbf_out:
            result, binary = sbf_parser.encode(block, payload_priority=0)  # Never use payload
            
            if result != "encoded":
                print(f"Warning: Encoding returned {result} on block {block}")
            fobj.write(binary)


    print("Done.")
    print(f"Output file: {args.output}")

if __name__ == "__main__":
    main()