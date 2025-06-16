#!/usr/bin/env python3
from operator import itemgetter
from sbf_parser import load, encode
import os
import filecmp
import traceback
import sys
import argparse

# Payload priority options
PAYLOAD_PRIORITY_NO_PAYLOAD = -3
PAYLOAD_PRIORITY_ONLY_NOT_IMPLEMENTED = -2
PAYLOAD_PRIORITY_ONLY_ON_FAIL = -1
PAYLOAD_PRIORITY_ALWAYS = 0

def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Decode and re-encode SBF files with specified payload priority.'
    )
    parser.add_argument('--input_file', 
        default="../sbf_files/log_0000.sbf",
        # log_0000.sbf large_0000.sbf receiver_status.sbf all_0000.sbf
        help='Input SBF file to process. Default to sbf_files/all_0000.sbf'
    )
    parser.add_argument('--priority', type=int, choices=[
        PAYLOAD_PRIORITY_NO_PAYLOAD, 
        PAYLOAD_PRIORITY_ONLY_NOT_IMPLEMENTED,
        PAYLOAD_PRIORITY_ONLY_ON_FAIL,
        PAYLOAD_PRIORITY_ALWAYS
    ],  default=PAYLOAD_PRIORITY_ONLY_NOT_IMPLEMENTED,
        help='Payload priority level for encoding'
    )
    return parser.parse_args()

def process_sbf_file(input_file, output_file, payload_priority):
    try:
        print(f"\n-------- Decoding {input_file}")
        sbf_blocks = []
        with open(input_file, 'rb') as f:
            for block_name, block_data in load(f):
                sbf_blocks.append((block_name, block_data))
                
        # print(f"First block Type    : {sbf_blocks[0][0]}")
        # print(f"First block Content : {sbf_blocks[0][1]}")
        print(f"Total blocks decoded: {len(sbf_blocks)}")

        print(f"\n-------- Re-encoding to {output_file}")
        result = {}
        with open(output_file, 'wb') as f:
            for block_name, block_data in sbf_blocks:
                try:
                    # Store the block and write it to the file
                    status, block_bytes = encode(block_data, payload_priority=payload_priority)
                    result[status] = result.get(status, 0) + 1

                    f.write(block_bytes)

                except ValueError as e:
                    if "Block structure definition not found" in str(e):
                        print(f"Warning: Skipping encoding of block '{block_name}' due to missing definition in blocks.py.")
                    else:
                        # print("Block data :", block_data)
                        traceback.print_exc()
                        print("")
                except Exception as e:
                    print(f"An unexpected error occurred encoding block {block_name}")
                    traceback.print_exc()

        print(f"Re-encoded file written to {output_file}")
        
        # Verify if the re-encoded file matches the original
        original_size = os.path.getsize(input_file)
        reencoded_size = os.path.getsize(output_file)
        print(f"Original   file size: {original_size} bytes")
        print(f"Re-encoded file size: {reencoded_size} bytes")
        print(f"Status :")
        for status, count in result.items():
            print(f"\t{status} : {count}")
        print()

        if filecmp.cmp(input_file, output_file):
            print("Success! Re-encoded file is identical to the original.")
        else:                
            print(f"Warning             : Re-encoded file differs from the original.")
            
    except Exception as e:
        print(f"Error processing SBF file: {e}")

def main():
    args = parse_arguments()
    for input_file, output_file in (
        (args.input_file, 'local_files/re-encoded.sbf'),
        ('local_files/re-encoded.sbf', 'local_files/re-re-encoded.sbf'),
        ('local_files/re-re-encoded.sbf', 'local_files/re-re-re-encoded.sbf')
    ):
        process_sbf_file(input_file, output_file, args.priority)

    # Comparing content before and after encoding
    before = []
    with open("local_files/re-encoded.sbf", 'rb') as f:
        for block_name, block_data in load(f):
            before.append((block_name, block_data))
    after = []
    with open("local_files/re-re-encoded.sbf", 'rb') as f:
        for block_name, block_data in load(f):
            after.append((block_name, block_data))
    again = []
    with open("local_files/re-re-re-encoded.sbf", 'rb') as f:
        for block_name, block_data in load(f):
            again.append((block_name, block_data))

    if len(before) != len(after):
        print(f"Before and after are not of the same length :")
        print(f"\tBefore : {len(before)}")
        print(f"\tBefore : {len(after)}")

    print("\nYou will get the difference between original, re-encoded.sbf and re-re-encoded.sbf")
    count_blocks = {}
    n = 70 # number of caractere preview
    missed_blocks = {}
    miss_match_count = 0

    for b,a,ag in zip(before, after, again):
        block = b[0]

        if not block in count_blocks.keys():
            count_blocks[block] = 0
        count_blocks[block] += 1

        if b != a: 
            miss_match_count += 1
            
            if not block in missed_blocks.keys():
                missed_blocks[block] = 0
            missed_blocks[block] += 1

            if missed_blocks[block] == 1: # print first miss-matched
                str_before = repr(b)
                str_after = repr(a)
                str_again = repr(ag)
                diff_pos = next((i for i in range(min(len(str_before), len(str_after))) 
                            if str_before[i] != str_after[i]), min(len(str_before), len(str_after)))

                print(f"\nMiss-match detected for block : {block}")
                # print(f"\tbefore: {b}")
                # print(f"\tafter : {a}")
                print()    
                print(f"\tDifference starts at position {diff_pos}:")
                print(f"\tbefore: ...{str_before[diff_pos - n : diff_pos + n]}...")
                print(f"\tafter : ...{str_after[diff_pos - n : diff_pos + n]}...")
                print(f"\tafter : ...{str_again[diff_pos - n : diff_pos + n]}...")
                print(f"\t           {' ' * min(n, diff_pos)}^")
            

    if miss_match_count == 0:
        print(f"No miss-match detected.")
    else:
        print(f"{miss_match_count} miss-match detected out of {len(before)} blocks.")
        print(f"Block concerned :")
        for block, occ in sorted(list(missed_blocks.items()), key=itemgetter(1), reverse=True):
            print(f"\t{block}: {occ} / {count_blocks[block]}")

    tested = sorted(list(count_blocks.keys()))
    print(f"Block tested {len(tested)}:")
    print(" ".join(tested))


if __name__ == "__main__":
    main()
