import serial
import time

# Ustawienia Twojego FTDI
ser = serial.Serial('/dev/ttyUSB0', 420000, timeout=0.1)

# Ramka CRSF: Sync, Len, Type (0x29 - Device Info), CRC
# To powinno zmusić moduł do odpowiedzi
ping_frame = bytearray([0xEE, 0x04, 0x29, 0x00]) # Uproszczony ping

print("Wysyłam zapytanie do modułu ES24TX Pro...")

try:
    while True:
        ser.write(ping_frame)
        time.sleep(0.5)
        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting)
            print(f"MODUŁ ODPOWIEDZIAŁ: {response.hex(' ')}")
        else:
            print("Cisza na linii...")
except KeyboardInterrupt:
    ser.close()
