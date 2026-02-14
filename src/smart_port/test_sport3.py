import serial
import time

# Otwieramy port UART na RPi
ser = serial.Serial('/dev/serial0', 420000, timeout=0.1)

# Ramka CRSF: Sync, Len, Type (0x29 - Device Info Request), Payload, CRC
# To jest standardowe zapytanie o status urządzenia
msg = bytearray([0xEE, 0x02, 0x29, 0x4D]) 

try:
    print("Wysyłam zapytanie do ES24TX...")
    ser.write(msg)
    
    # Dajemy modułowi chwilę i patrzymy na oscyloskop/bufor
    time.sleep(0.1)
    if ser.in_waiting > 0:
        response = ser.read(ser.in_waiting)
        print(f"Odebrano odpowiedź (HEX): {response.hex()}")
    else:
        print("Brak odpowiedzi w buforze UART.")
finally:
    ser.close()
