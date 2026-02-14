import serial
import time

port = "/dev/ttyAMA0"
# Przetestujemy dwie główne prędkości, na których moduł mógłby przyjąć komendę
bauds = [420000, 460800, 115200]

def send_wifi_command(ser):
    # Ramka CRSF: Sync, Len, Type (0x2D - Enter Wi-Fi), CRC
    wifi_frame = bytes([0xEE, 0x02, 0x2D, 0x1E])
    ser.write(wifi_frame)

for b in bauds:
    print(f"Próba wymuszenia Wi-Fi na {b} bps...")
    try:
        with serial.Serial(port, b, timeout=0.5) as ser:
            for _ in range(10): # Wyślij 10 razy dla pewności
                send_wifi_command(ser)
                time.sleep(0.1)
    except:
        pass
    time.sleep(1)

print("Koniec. Sprawdź diodę.")
