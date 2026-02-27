import serial

ser = serial.Serial("/dev/ttyAMA2", baudrate=115200, timeout=2)
ser.write(b"PING\n")
odp = ser.readline()
print(f"Odebralem: {odp}")
ser.close()
