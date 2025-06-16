from sbf_parser import SbfParser
import os
import sys
import fcntl
from time import sleep

# You can read directly from a serial connexion using :
# cat /dev/ttyACM0 | python3 read_stdin.py

# Set stdin to non-blocking
fd = sys.stdin.fileno()
flags = fcntl.fcntl(fd, fcntl.F_GETFL)
fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

parser = SbfParser()

while True:
    # Read up to 1024 bytes from stdin
    try:
        data = os.read(fd, 1024)  # returns immediately
        if len(data) == 0:
            sleep(0.01) # 10ms
        else:
            for block_desc, infos in parser.parse(data):
                print(infos)
    
    except BlockingIOError:
        pass
