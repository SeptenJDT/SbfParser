from sbf_parser import SbfParser
import os
import fcntl
import time
import serial  # Optional, if you want to use pyserial for configuration

#serial_port = '/dev/ttyACM0' # If the mosaic is connected to USB ; Use ttyACM1 for the second virtual com port
serial_port = '/dev/ttyAMA0' # If the mosaic is connected to COM1 of the Pi

# Open the serial port
serial_fd = os.open(serial_port, os.O_RDONLY | os.O_NONBLOCK)
# Optional: configure the serial port using pyserial
ser = serial.Serial(serial_port, baudrate=115200, timeout=0)

# Set non-blocking mode (already done with os.O_NONBLOCK, but shown here for completeness)
flags = fcntl.fcntl(serial_fd, fcntl.F_GETFL)
fcntl.fcntl(serial_fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

parser = SbfParser()

while True:
    try:
        data = os.read(serial_fd, 1024)
        if len(data) == 0:
            time.sleep(0.01)
        else:
            for block_desc, infos in parser.parse(data):
                print(infos)
    except BlockingIOError:
        pass
