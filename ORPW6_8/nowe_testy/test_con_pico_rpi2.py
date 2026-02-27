import serial

ser = serial.Serial("/dev/ttyAMA2", baudrate=115200, timeout=2)

print("=== RPi5 <-> Pico UART ===")

# RPi5 -> Pico
ser.write(b"RPI5: Witaj Pico!\n")
odp1 = ser.readline()
print(f"Pico: {odp1.decode().strip()}")

# Pico -> RPi5 (już działa!)
print("Komunikacja OK!")

ser.close()
