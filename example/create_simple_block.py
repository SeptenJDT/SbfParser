#!/usr/bin/env python3
from sbf_parser import load, encode

def create_extEnvent_block():
    print("Create a simple ExtEvent block.")

    event_block = {
        'blockName': 'ExtEvent',
        'TOW': 123456789,  # Time of Week in milliseconds
        'WNc': 2120,       # Week number (continuous)
        'Source': 1,       # Source identifier
        'Polarity': 0,     # Polarity (0 = rising edge)
        'Offset': 0.005,   # Time offset in seconds
        'RxClkBias': 0.0,  # Receiver clock bias
        'PVTAge': 0        # Age of PVT in ms
    }

    # Serialize the block
    result, block_bytes = encode(event_block)

    # Print some information about the created block
    print(f"Created ExtEvent block with {len(block_bytes)} bytes (result: {result})")
    print(f"First 8 bytes (header): {block_bytes[:8].hex()}")

    # Write the block to a file
    with open('local_files/ext_event.sbf', 'wb') as f:
        f.write(block_bytes) 
        
    print(f"Wrote ExtEvent block to sbf_files/ext_event.sbf")

    input_file = "local_files/ext_event.sbf"
    print(f"\nDecoding {input_file}")
    with open(input_file, 'rb') as f:
        sbf_blocks = []

        for block_name, block_data in load(f):
            sbf_blocks.append((block_name, block_data))
            
        print(f"First block Type    : {sbf_blocks[0][0]}")
        print(f"First block Content : {sbf_blocks[0][1]}")
        print(f"Total blocks decoded: {len(sbf_blocks)}")

if __name__ == "__main__":
    create_extEnvent_block()