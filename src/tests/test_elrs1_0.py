import serial
import time

# Ustawienie portu ttyAMA10 (z Twojej malinki)
ser = serial.Serial('/dev/ttyAMA10', 460800, timeout=1)

print("Testowanie mostu radiowego Airport...")

try:
    while True:
        ser.write(b'RADIOLINK_DZIALA\n')
        time.sleep(0.2) # Chwila na przelot danych przez radio
        if ser.in_waiting > 0:
            dane = ser.read(ser.in_waiting)
            print(f"POWRÓT Z ODBIORNIKA: {dane.decode(errors='ignore').strip()}")
        else:
            print("Dane nie wracają (sprawdź zworkę na Nano)")
        time.sleep(0.8)
except KeyboardInterrupt:
    print("Test przerwany.")
    ser.close()
