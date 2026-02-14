import serial
import time

# Otwieramy port FTDI              420000
ser = serial.Serial('/dev/ttyUSB0',420000, timeout=0.1)
# EE 02 29 4D
msg = bytearray([0xEE, 0x02, 0x29, 0x4D]) 

print("Pętla testowa na FTDI (/dev/ttyUSB1) ruszyła...")

try:
    while True:
        ser.write(msg)
        ser.flush()
        time.sleep(0.05) # 50ms przerwy dla stabilnego obrazu
except KeyboardInterrupt:
    print("\nZatrzymano.")
finally:
    ser.close()
