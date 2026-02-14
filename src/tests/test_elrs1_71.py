import serial
import time

port = "/dev/ttyAMA0"
baud = 115200

try:
    ser = serial.Serial(port, baud, timeout=1)
    print(f"START: Ciągłe nadawanie na {port} ({baud} bps)")
    print("Teraz możesz spokojnie zmierzyć napięcie na pinie RX modułu.")
    print("Naciśnij Ctrl+C, aby przerwać.")

    # Ramka, którą moduł powinien zinterpretować jako dane
    test_frame = bytes([0xC8, 0x04, 0x28, 0x00, 0xCF])

    while True:
        ser.write(test_frame)
        # Krótka przerwa, aby multimetr zdążył zareagować na zmianę stanu
        time.sleep(0.05) 
        
except KeyboardInterrupt:
    print("\nZatrzymano przez użytkownika.")
except Exception as e:
    print(f"Błąd: {e}")
finally:
    if 'ser' in locals():
        ser.close()
