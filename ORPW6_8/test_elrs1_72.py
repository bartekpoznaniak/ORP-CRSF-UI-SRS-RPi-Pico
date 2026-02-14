import serial
import time

# Zmieniamy na AMA10 - to jest fizyczny UART na pinach 8 i 10 w RPi 5
port = "/dev/ttyAMA10"
baud = 115200

try:
    ser = serial.Serial(port, baud, timeout=1)
    print(f"Nadaję na {port}... Teraz sprawdź miernikiem Pin 1!")
    
    while True:
        ser.write(b'\x55' * 20)
        time.sleep(0.05)
        
except Exception as e:
    print(f"Błąd portu {port}: {e}")

