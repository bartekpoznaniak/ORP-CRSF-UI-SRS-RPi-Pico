import serial
import time

port = "/dev/ttyAMA0"
baud = 9600 # Niska prędkość - multimetr łatwiej wyłapie spadek napięcia

try:
    ser = serial.Serial(port, baud, timeout=1)
    print(f"Nadaję ciągły sygnał na {port} (Pin 8). Sprawdź teraz!")
    
    while True:
        # Wysyłamy bardzo długi blok zer - to wymusi stan niski na linii przez dłuższy czas
        ser.write(b'\x00' * 100)
        time.sleep(0.01)
        
except Exception as e:
    print(f"Błąd: {e}")
