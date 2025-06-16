#!/usr/bin/env python3
from sbf_parser import load, encode
import datetime

print("Create a ReceiverStatus block with AGCState sub-blocks.""")

current_time = datetime.datetime.now()
week_number = int((current_time - datetime.datetime(1980, 1, 6)).days / 7)
tow = int(((current_time.hour * 3600 + current_time.minute * 60 + current_time.second) * 1000) + 
            (current_time.microsecond / 1000))

rx_status = {
    'blockName': 'ReceiverStatus',
    'blockType': 'SBF',
    'TOW': tow,
    'WNc': week_number,
    'CPULoad': 1,        # CPU load in percent
    'ExtError': 2,        # External error code
    'UpTime': 10000000,       # Seconds since boot
    'RxState': 20000000,         # Receiver state (1 = tracking)
    'RxError': 40000000,         # Receiver error flags
    'N': 2,               # Number of AGC states
    'SBLength': 4,        # Size of sub-block
    'CmdCount': 64,        # Command count
    'Temperature': 128,    # Temperature in degrees
    'AGCState': [         # List of AGC states
        {
            'FrontendID': 1,
            'Gain': 2,
            'SampleVar': 4,
            'BlankingStat': 8
        },
        {
            'FrontendID': 16,
            'Gain': 32,
            'SampleVar': 64,
            'BlankingStat': 128
        }
    ]
}

try:
    result, rx_status_bytes = encode(rx_status)
    with open('local_files/receiver_status.sbf', 'wb') as f:
        f.write(rx_status_bytes)

    print(f"Created ReceiverStatus block with {len(rx_status_bytes)} bytes")
    print(f"Wrote ReceiverStatus block to sbf_files/receiver_status.sbf")

except Exception as e:
    print(f"Error creating ReceiverStatus block: {e}")
    exit(1)

input_file = "local_files/receiver_status.sbf"
print(f"\nDecoding {input_file}")
with open(input_file, 'rb') as f:
    sbf_blocks = []

    for block_name, block_data in load(f):
        sbf_blocks.append((block_name, block_data))
        
    print(f"First block Type    : {sbf_blocks[0][0]}")
    print(f"First block Content : {sbf_blocks[0][1]}")
    print(f"Total blocks decoded: {len(sbf_blocks)}")