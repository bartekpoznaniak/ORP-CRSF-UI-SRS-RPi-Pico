
from machine import I2C, Pin
from pca9685 import PCA9685
import utime

# Inicjalizacja magistrali
i2c = I2C(0, sda=Pin(0), scl=Pin(1))
pca = PCA9685(i2c)

# Ustawienie częstotliwości PWM (50Hz jest typowe dla serw, dla LED może być wyższe, np. 1000Hz)
pca.freq(50)

print("Rozpoczynam test PWM na kanale 0...")

try:
    while True:
        # Pętla rozjaśniająca/ściemniająca (wartości od 0 do 4095)
        for i in range(0, 4096, 64):
            pca.duty(0, i) # kanał 0, wypełnienie i
            utime.sleep_ms(10)
        for i in range(4095, -1, -64):
            pca.duty(0, i)
            utime.sleep_ms(10)
            
except KeyboardInterrupt:
    pca.duty(0, 0) # Wyłącz po zatrzymaniu programu
    print("Program zatrzymany.")
