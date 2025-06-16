#!/usr/bin/env python3
import os
import time
from sbf_parser import load

file_path = "../sbf_files/large_0000.sbf"
n = 10

file_size = os.stat(file_path).st_size


def get_status(iteration, duration):
    return f"{round(duration/i, 1)}s/iterations {round(duration, 1)}s total {round(file_size*iteration/(1000000 * duration), 1)} mo/s"


print("Starting stress-test ...")
print("File size :", file_size)
start = time.time()
elements = []

for i in range(1, n + 1):
    elements = []
    with open(file_path, 'rb') as f:
        for block_name, block_data in load(f):
            elements.append((block_name, block_data))
    print(f"{i}/{n} : " + get_status(i, time.time() - start))

duration = time.time() - start
print()
print(f"{len(elements)} blocks decoded in {round(duration, 2)}s")
print(get_status(n, time.time() - start))


