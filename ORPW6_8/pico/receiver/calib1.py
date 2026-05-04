from machine import I2C, Pin
from pca9685 import PCA9685
import utime

# ========================= KALIBRATOR SYMETRII =========================
CW_TEST_DUTY = 420     # START CW (zwiększaj jeśli za wolno)
CCW_TEST_DUTY = 220    # START CCW (zmniejszaj jeśli za wolno)  
TEST_TIME_S = 5        # czas testu na duty (s)
ESC_CHANNEL = 0
# ======================================================================

i2c = I2C(0, sda=Pin(0), scl=Pin(1))
pca = PCA9685(i2c)
pca.freq(50)
NEUTRAL = 307
led = Pin("LED", Pin.OUT)

def test_direction(duty, direction):
    print(f"\n=== {direction} duty={duty} przez {TEST_TIME_S}s ===")
    pca.duty(ESC_CHANNEL, duty)
    led.value(1)
    for t in range(TEST_TIME_S * 10):
        print(f"  Czas {t//10:.1f}s | RPM wizualnie: [1-10]?")
        utime.sleep(0.1)
    pca.duty(ESC_CHANNEL, NEUTRAL)
    led.value(0)
    print("STOP. Ctrl+C wyjście, Enter następny test")

print("KALIBRATOR SYMETRII ESC 2-way")
print("Testuje duty -> wizualnie oceń RPM (1 słabo, 10 full)")
print("Zmień CW_TEST_DUTY/CCW_TEST_DUTY na górze -> restart")

try:
    while True:
        # TEST CW
        test_direction(CW_TEST_DUTY, "CW")
        
        # TEST CCW  
        test_direction(CCW_TEST_DUTY, "CCW")
        
        input()  # czekaj Enter

except KeyboardInterrupt:
    pca.duty(ESC_CHANNEL, NEUTRAL)
    print("\nKONIEC - neutral.")
