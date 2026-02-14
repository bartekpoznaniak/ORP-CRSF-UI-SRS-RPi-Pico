import serial
import time

# Celujemy w nowy port, który właśnie się pojawił
ser = serial.Serial(
    port='/dev/ttyAMA2', 
    baudrate=9600,
    timeout=1
)

print("Nadaję na UART2 (Pin 27). Sprawdzaj oscyloskop!")

try:
    while True:
        # Wysyłamy paczkę danych
        ser.write(b'AT\r\n') 
        print("Wysłano: AT")
        time.sleep(0.5)
except KeyboardInterrupt:
    ser.close()
