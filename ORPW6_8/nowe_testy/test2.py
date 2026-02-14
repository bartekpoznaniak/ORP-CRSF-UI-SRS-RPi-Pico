import serial
import time

# Otwieramy port na Twoim FTDI
ser = serial.Serial('/dev/ttyUSB0', 420000, timeout=0.1)

# Ramka CRSF: Sync(0xEE), Len(0x04), Type(0x29 - Device Info), CRC(0x4B)
# To jest poprawny, binarny pakiet 'zaczepny'
handshake = bytearray([0xEE, 0x04, 0x29, 0x4B])

print("Próbuję wybudzić UART w ES24TX Pro... (Naciśnij Ctrl+C by przerwać)")

try:
    while True:
        ser.write(handshake)
        # Sprawdzamy czy coś wróciło
        if ser.in_waiting > 0:
            data = ser.read(ser.in_waiting)
            print(f"SUKCES! Moduł odpowiedział: {data.hex(' ')}")
            # Jeśli tu dojdziesz, dioda powinna zmienić rytm!
        time.sleep(0.1) # Wysyłaj 10 razy na sekundę
except KeyboardInterrupt:
    ser.close()
