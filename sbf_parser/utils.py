# Initial code by Louis-Max Harter 2025

import sys
import sbf_parser


def replace_header_time(input_file, blocks_names, start_time=0, duration=0, max_gap=1500, min_gap=1, default_gap=1000):
    # Filter blocks
    selection = []
    analysis = {}
    
    for block_type, infos in sbf_parser.read(input_file):
        analysis[block_type] = analysis.get(block_type, 0) + 1

        if block_type in blocks_names:
            selection.append(infos)

    # Analysis
    print("Block selected:")
    for name in sorted(blocks_names):
        print(f"\t{name:20} : {analysis.get(name, 0):4d}")
    print()

    print("Block filtered:")
    for name, n in sorted(analysis.items()):
        if name not in blocks_names:
            print(f"\t{name:20} : {n:4d}")
    print()

    # Check if blocks
    if selection == []:
        print("No blocks in selection")
        sys.exit(1)

    # Calculating deltas
    sbf_out = []
    sbf_out.append(selection[0])
    sbf_out[-1]["TOW"] = start_time

    for i in range(1, len(selection)):
        previous_block = sbf_out[-1]
        current_block = selection[i]
        
        delta = current_block["TOW"] - previous_block["TOW"]

        if delta < 0 or delta > max_gap:
            delta = default_gap
        else:
            delta = max(min_gap, delta)
        
        current_block["TOW"] = sbf_out[-1]["TOW"] + delta
        sbf_out.append(current_block)

    # Shrink to target duration if specified
    real_duration = sbf_out[-1]["TOW"] - sbf_out[0]["TOW"]

    if duration != 0:
        if real_duration <= 0:
            print(f"Can't shrink duration of {real_duration} to {duration}. Try using --min-gap to force non-null duration.")
            sys.exit(1)

        coef = duration / real_duration
        start = sbf_out[0]["TOW"]

        for block in sbf_out:
            elapsed = block["TOW"] - start
            block["TOW"] = int(start + elapsed * coef)
        
        print(f"Shrink duration to {duration}")
    print("Done.")

    return sbf_out