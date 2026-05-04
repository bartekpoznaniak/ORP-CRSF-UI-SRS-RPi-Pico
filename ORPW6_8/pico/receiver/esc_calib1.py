from machine import I2C, Pin
from pca9685 import PCA9685
import utime

i2c = I2C(0, sda=Pin(0), scl=Pin(1))
pca = PCA9685(i2c)
pca.freq(50)

# Kanał ESC (zmień na swój)
ESC_CHANNEL = 0

# Duty cycle dla PWM ESC (50Hz)
THROTTLE_MIN = 102   # 1ms = min gaz (0%)
THROTTLE_MAX = 512   # 2ms = max gaz (100%)
THROTTLE_SAFE = 102  # bezpieczne 0%

led = Pin("LED", Pin.OUT)  # wbudowana dioda Pico do statusu

print("ESC Kalibracja - podłącz ESC w ciągu 10s!")
print("Po kalibracji PWM normalne 1-2ms")

try:
    # ETAP 1: 10s mruganie LED - czas na podłączenie ESC
    print("Etap 1: Mruganie 10s - podłącz ESC!")
    for _ in range(50):  # 10s @ 200ms/cykl
        led.value(1)
        utime.sleep_ms(100)
        led.value(0)
        utime.sleep_ms(100)
    
    # ETAP 2: MAX THROTTLE (2ms) x 3s - ESC uczy max
    print("Etap 2: MAX THROTTLE 3s - ESC kalibruje MAX")
    pca.duty(ESC_CHANNEL, THROTTLE_MAX)
    utime.sleep(3)
    
    # ETAP 3: MIN THROTTLE (1ms) x 3s - ESC uczy min  
    print("Etap 3: MIN THROTTLE 3s - ESC kalibruje MIN")
    pca.duty(ESC_CHANNEL, THROTTLE_MIN)
    utime.sleep(3)
    
    # ETAP 4: SAFE MIN - gotowe!
    print("KALIBRACJA ZAKOŃCZONA! ESC gotowy (safe min PWM)")
    pca.duty(ESC_CHANNEL, THROTTLE_SAFE)
    led.value(1)  # LED stale ON = sukces
    
    # Demo test (opcjonalne - Ctrl+C zatrzymaj)
    print("Test throttla - Ctrl+C zatrzymaj")
    throttle = 102
    step = 10
    while True:
        pca.duty(ESC_CHANNEL, throttle)
        throttle = THROTTLE_MIN + (throttle - THROTTLE_MIN + step) % (THROTTLE_MAX - THROTTLE_MIN)
        utime.sleep_ms(200)

except KeyboardInterrupt:
    pca.duty(ESC_CHANNEL, THROTTLE_SAFE)
    led.value(0)
    print("Zatrzymano - safe min.")
