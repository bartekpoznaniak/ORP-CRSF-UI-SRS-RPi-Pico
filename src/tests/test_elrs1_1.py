import serial
import time

# Standardowa prędkość dla ELRS to 420000. 
# Jeśli masz starszy firmware, może to być 115200.
port = "/dev/ttyAMA0" # Domyślny UART na RPi 5
baud = 420000

try:
    ser = serial.Serial(port, baud, timeout=1)
    print(f"Otwarto port {port} przy {baud} bps. Czekam na dane z ES24TX...")
    
    while True:
        if ser.in_waiting > 0:
            # Czytamy surowe bajty
            data = ser.read(ser.in_waiting)
            # CRSF zaczyna się od bajtu synchronizacji 0xEE, 0xC8 lub 0xEA
            print(f"Odebrano {len(data)} bajtów. Hex: {data.hex().upper()[:50]}...")
        time.sleep(0.1)
except Exception as e:
    print(f"Błąd: {e}")
