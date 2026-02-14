import serial
import time

# Inicjalizacja portu UART2 na RPi 5
# /dev/ttyAMA2 odpowiada naszym nowym pinom 27/28
ser = serial.Serial(
    port='/dev/ttyAMA2',
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)

print("Wysyłam dane przez UART2 (Pin 27)... Sprawdź oscyloskop!")

try:
    while True:
        data = b"Hello RPi5 UART2\n"
        ser.write(data)
        print(f"Wysłano: {data.decode().strip()}")
        time.sleep(1)  # Przerwa, żebyś zdążył przyjrzeć się przebiegowi
except KeyboardInterrupt:
    print("\nZakończono.")
finally:
    ser.close()
