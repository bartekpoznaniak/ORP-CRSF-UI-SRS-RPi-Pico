import serial
import time

# Testujemy stabilność TX na RPi 5
ser = serial.Serial('/dev/ttyAMA0', 420000)
test_pattern = b'\xEE\xAA' * 10 # Charakterystyczny wzór 101010...

print("Wysyłam wzór testowy na oscyloskop...")
try:
    while True:
        ser.write(test_pattern)
        time.sleep(0.01) # Mała przerwa dla przejrzystości na ekranie oscyloskopu
except KeyboardInterrupt:
    ser.close()
