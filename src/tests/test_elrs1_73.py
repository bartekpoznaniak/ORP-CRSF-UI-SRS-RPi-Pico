import serial
import time

port = "/dev/ttyAMA0"
# Dwie prędkości, o które podejrzewamy moduł
bauds = [420000, 460800]

# Standardowa ramka kanałów CRSF (wszystkie kanały na środek)
rc_frame = bytes([
    0xEE, 0x18, 0x16, 0xE0, 0x03, 0x1F, 0x00, 0x00, 
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
    0x00, 0x24
])

try:
    while True:
        for b in bauds:
            print(f">>> Przełączam na: {b} bps. Obserwuj diodę...")
            with serial.Serial(port, b, timeout=0.1) as ser:
                start_time = time.time()
                # Wysyłaj ramki przez 5 sekund na danej prędkości
                while time.time() - start_time < 5:
                    ser.write(rc_frame)
                    time.sleep(0.01) # Częstotliwość 100Hz
            time.sleep(0.5) # Krótka przerwa przed zmianą prędkości

except KeyboardInterrupt:
    print("\nZatrzymano.")
