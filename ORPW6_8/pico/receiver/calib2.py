from machine import I2C, Pin
from pca9685 import PCA9685
import utime

# ========================= PARAMETRY KALIBRATORA =========================
CW_TEST_DUTY = 420     # test CW (zwiększaj = szybciej)
CCW_TEST_DUTY = 220    # test CCW (zmniejszaj = szybciej)
TEST_TIME_S = 5        # czas testu (s)
ESC_CHANNEL = 0        # kanał PCA
# =========================================================================

i2c = I2C(0, sda=Pin(0), scl=Pin(1))
pca = PCA9685(i2c)
pca.freq(50)
NEUTRAL = 307
led = Pin("LED", Pin.OUT)

print(f"KALIBRATOR: CW={CW_TEST_DUTY} CCW={CCW_TEST_DUTY} | czas={TEST_TIME_S}s")

def test_dir(duty, dir_name):
    print(f"\n=== {dir_name} duty={duty} x{TEST_TIME_S}s ===")
    pca.duty(ESC_CHANNEL, duty)
    led.value(1)
    for t in range(TEST_TIME_S * 10):
        print(f"  {t//10:.1f}s | RPM [1-10]: ", end='\r')
        utime.sleep(0.1)
    pca.duty(ESC_CHANNEL, NEUTRAL)
    led.value(0)
    print("\nSTOP. Enter=next | Q=quit")

try:
    while True:
        test_dir(CW_TEST_DUTY, "CW")
        test_dir(CCW_TEST_DUTY, "CCW")
        cmd = input("Enter=powtórz | Q=koniec: ").strip().upper()
        if cmd == 'Q':
            break
except KeyboardInterrupt:
    pca.duty(ESC_CHANNEL, NEUTRAL)
    print("KONIEC.")
