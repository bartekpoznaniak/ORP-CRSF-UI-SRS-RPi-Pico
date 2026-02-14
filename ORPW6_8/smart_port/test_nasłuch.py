 
import serial, time, binascii

PORT = "/dev/ttyUSB0"
BAUD = 420000

ser = serial.Serial(PORT, baudrate=BAUD, bytesize=8, parity='N', stopbits=1, timeout=0.2)

t_end = time.time() + 5.0
buf = bytearray()

while time.time() < t_end:
    chunk = ser.read(4096)
    if chunk:
        buf += chunk

print("RX bytes:", len(buf))
print(binascii.hexlify(buf[:300], sep=b' ').decode())
