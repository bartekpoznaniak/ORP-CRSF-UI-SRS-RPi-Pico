import serial
ser = serial.Serial('/dev/serial0', 115200, timeout=1)
ser.write(b'TEST')
print(ser.read(4)) # Powinno wypisać b'TEST'
