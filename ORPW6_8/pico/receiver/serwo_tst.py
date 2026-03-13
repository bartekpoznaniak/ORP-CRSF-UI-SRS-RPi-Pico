from machine import I2C, Pin
from pca9685 import PCA9685
import utime

# Inicjalizacja magistrali (Pico: SDA=GP0, SCL=GP1)
i2c = I2C(0, sda=Pin(0), scl=Pin(1))
pca = PCA9685(i2c)

# Serwa standardowo pracują na 50Hz
pca.freq(50)

print("Test serwa na kanale 0 (zakres 0-180 stopni)...")

try:
    while True:
        # Ruch do 180 stopni
        print("Kierunek: 180")
        for pos in range(102, 512, 5):
            pca.duty(0, pos)
            utime.sleep_ms(20)
            
        # Ruch powrotny do 0 stopni
        print("Kierunek: 0")
        for pos in range(512, 102, -5):
            pca.duty(0, pos)
            utime.sleep_ms(20)
            
except KeyboardInterrupt:
    # Ustawienie w pozycji neutralnej przed wyłączeniem
    pca.duty(0, 307)
    print("Program zatrzymany.")
