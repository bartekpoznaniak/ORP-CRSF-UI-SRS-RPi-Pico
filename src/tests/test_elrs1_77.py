import serial
import time

# Port UART na RPi 5 (GPIO 14/15)
# Ustawiamy prędkość, którą zapisałeś w module
# ser = serial.Serial('/dev/ttyAMA0', 420000, timeout=1)
ser = serial.Serial('/dev/ttyUSB0', 420000, timeout=1)
# Prosta ramka CRSF (Device Info request)
# To jest sygnał dla modułu: "Hej, tu Twoja aparatura!"
request_frame = b'\xee\x02\x2f\xa0' 

print("Wysyłam ramkę inicjalizacyjną do ES24TX...")

try:
    while True:
        ser.write(request_frame)
        time.sleep(0.5) # Wysyłaj co pół sekundy
        if ser.in_waiting > 0:
            data = ser.read(ser.in_waiting)
            print(f"Odebrano telemetrię: {data.hex()}")
except KeyboardInterrupt:
    ser.close()
    print("\nZatrzymano.")
