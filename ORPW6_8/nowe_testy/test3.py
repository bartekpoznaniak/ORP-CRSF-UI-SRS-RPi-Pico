import serial
import time

# Lista standardowych prędkości dla ELRS
bauds = [115200, 420000, 525000, 921600, 1870000]
handshake = bytearray([0xEE, 0x04, 0x29, 0x4B])

print("Rozpoczynam skanowanie prędkości UART...")

for b in bauds:
    print(f"Testuję prędkość: {b} bodów...")
    try:
        ser = serial.Serial('/dev/ttyUSB0', b, timeout=0.1)
        # Wysyłaj ramkę przez 5 sekund dla każdej prędkości
        start_time = time.time()
        while time.time() - start_time < 5:
            ser.write(handshake)
            if ser.in_waiting > 0:
                res = ser.read(ser.in_waiting)
                print(f"!!! MODUŁ ODPOWIEDZIAŁ przy {b} bodach: {res.hex(' ')}")
                ser.close()
                exit()
            time.sleep(0.1)
        ser.close()
    except Exception as e:
        print(f"Błąd przy {b}: {e}")

print("Skanowanie zakończone. Jeśli moduł nadal wszedł w WiFi, sprawdź Dip-Switche.")
