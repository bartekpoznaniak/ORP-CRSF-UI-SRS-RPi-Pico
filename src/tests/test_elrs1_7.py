import serial
import time

port = "/dev/ttyAMA0"
# Lista prędkości do sprawdzenia (od standardowych po te po Twoich zmianach)
baudrates = [115200, 420000, 460800, 500000, 921600, 1000000]

# Ramka CRSF Ping
ping_frame = bytes([0xC8, 0x04, 0x28, 0x00, 0xCF])

print("Rozpoczynam skanowanie baudrate...")

for baud in baudrates:
    try:
        ser = serial.Serial(port, baud, timeout=0.5)
        print(f"Testuję: {baud}...", end=" ", flush=True)
        
        # Wysyłamy ping dwa razy dla pewności
        ser.write(ping_frame)
        time.sleep(0.1)
        ser.write(ping_frame)
        time.sleep(0.2)
        
        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting)
            print(f"\n[!!!] ZNALEZIONO! Na prędkości {baud} moduł odpowiedział: {response.hex().upper()}")
            ser.close()
            break
        else:
            print("brak odpowiedzi.")
        
        ser.close()
    except Exception as e:
        print(f"Błąd przy {baud}: {e}")

print("\nSkanowanie zakończone.")
