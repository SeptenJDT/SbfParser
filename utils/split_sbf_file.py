from sbf_parser import read
import argparse
import time
import os

# python split_sbf_file.py input.sbf output.sbf 1000 2000

def main():
    parser = argparse.ArgumentParser(description='Split SBF file based on TOW timestamps')
    parser.add_argument('input_path', help='Path of the file to split')
    parser.add_argument('output_path', help='Path of the output file')
    parser.add_argument('start_TOW', type=int, help='Start recording after TOW')
    parser.add_argument('end_TOW', type=int, help='Stop recording after TOW')
    
    args = parser.parse_args()
    is_reading = False

    size_parsed = 0
    size_input = os.stat(args.input_path).st_size
    start = time.time()
    last_percent_progress = -1

    # Open output file once in append mode
    with open(args.output_path, "ab") as f_output:
        for i, (block_type, infos) in enumerate(read(args.input_path)):
            # Get time
            TOW = infos.get("TOW", None)
            if TOW is not None:
                is_reading = (args.start_TOW < TOW < args.end_TOW)

            # Writing
            if is_reading:
                f_output.write(infos["payload"])

            # Progress
            size_parsed += len(infos["payload"])
            progress = int(100 * size_parsed/size_input); 
            if last_percent_progress != progress:
                last_percent_progress = progress
                print("{:>10} | {:6.0f} MB : TOW : {:>10} ({:02.0f}%) {}".format(
                    i, size_parsed / (1024*1024), 
                    "X" if TOW is None else str(TOW), 
                    100 * size_parsed/size_input,
                    "Saving to file" if is_reading else ""
                ))

    end = time.time()
    print("\nParsing completed in {:.2f} seconds".format(end - start))
    print("Speed: {:.2f} MB/s".format((size_parsed / (1024*1024)) / (end - start)))

if __name__ == "__main__":
    main()
