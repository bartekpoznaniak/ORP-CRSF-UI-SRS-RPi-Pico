import serial
import time

# Lista najczęstszych prędkości w ELRS
baudrates = [420000, 460800, 115200, 921600, 230400]
port = "/dev/ttyAMA0" # Upewnij się, że to ten port na RPi 5

def check_baudrate():
    for baud in baudrates:
        print(f"--- Testuję prędkość: {baud} bps ---")
        try:
            with serial.Serial(port, baud, timeout=0.5) as ser:
                # Czekamy chwilę na bufor
                time.sleep(0.2)
                data = ser.read(100)
                if data:
                    print(f"Odebrano dane: {data.hex().upper()[:40]}")
                    if b'\xc8' in data or b'\xee' in data:
                        print(f"!!! SUKCES !!! Znaleziono ramkę CRSF na baud: {baud}")
                        return baud
                else:
                    print("Brak danych.")
        except Exception as e:
            print(f"Błąd portu: {e}")
    return None

detected_baud = check_baudrate()
