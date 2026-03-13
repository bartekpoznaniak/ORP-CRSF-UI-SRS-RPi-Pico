import serial

ser = serial.Serial("/dev/ttyAMA2", baudrate=115200, timeout=1)
ser.write(b"Test z Thonny!\n")
print(ser.readline().decode().strip())
ser.close()
