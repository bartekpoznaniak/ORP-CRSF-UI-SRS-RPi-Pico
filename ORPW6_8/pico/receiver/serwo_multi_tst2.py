from machine import I2C, Pin
from pca9685 import PCA9685
import utime
import math

i2c = I2C(0, sda=Pin(0), scl=Pin(1))
pca = PCA9685(i2c)
pca.freq(50)

# Konfiguracja
SERVO_CHANNELS = [0, 1, 2]  # Kanały, do których wpięte są serwa
OFFSET_STEP = 15            # Przesunięcie w stopniach między serwami
MIN_DUTY = 102              # 0 stopni
MAX_DUTY = 512              # 180 stopni

def get_duty(angle):
    # Mapowanie kąta 0-180 na duty 102-512
    return int(MIN_DUTY + (angle / 180) * (MAX_DUTY - MIN_DUTY))

print("Test wielu serw z przesunięciem...")

try:
    t = 0
    while True:
        for i, ch in enumerate(SERVO_CHANNELS):
            # Obliczanie kąta za pomocą funkcji sinus dla płynnego ruchu
            # Każde kolejne serwo (i) ma dodany offset
            angle = 90 + 90 * math.sin(t + (i * math.radians(OFFSET_STEP)))
            pca.duty(ch, get_duty(angle))
        
        t += 0.1  # Prędkość ruchu
        utime.sleep_ms(40)

except KeyboardInterrupt:
    for ch in SERVO_CHANNELS:
        pca.duty(ch, 307) # Powrót do środka
    print("Zatrzymano.")
