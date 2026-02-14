import serial
import time

# Otwieramy port UART na RPi
ser = serial.Serial('/dev/ttyUSB0', 420000, timeout=0.1)

# Ramka CRSF: Device Info Request
msg = bytearray([0xEE, 0x02, 0x29, 0x4D]) 

print("Rozpoczynam pętlę testową. Naciśnij Ctrl+C, aby zatrzymać.")

try:
    while True:
        ser.write(msg)
        # Flush zapewnia, że dane fizycznie opuściły bufor RPi
        ser.flush() 
        
        # Krótka przerwa, by oscyloskop zdążył się odświeżyć
        time.sleep(0.05) 
        
        # Opcjonalnie: sprawdź czy coś wróciło
        if ser.in_waiting > 0:
            res = ser.read(ser.in_waiting)
            # Nie drukujemy w pętli, by nie śmiecić w konsoli, 
            # ale możesz odkomentować linię poniżej:
            # print("Jest odpowiedź!")

except KeyboardInterrupt:
    print("\nPętla zatrzymana.")
finally:
    ser.close()
