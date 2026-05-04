from machine import I2C, Pin
from pca9685 import PCA9685
import utime


RAMP_TIME_MS = 500
PAUSE_TIME_MS = 500  
#CW_MIN_DUTY = 205
CW_MAX_DUTY = 365
CCW_MIN_DUTY = 200    # ZMIANA: pełny zakres CCW (min!)
#CCW_MAX_DUTY = 230    # ZMIANA: mocniej (niżej = szybciej CCW)
CYCLE_PAUSE_MS = 200
RAMP_STEPS = 50
ESC_CHANNEL = 0

# ========================= PARAMETRY - ZMIENIAJ TUTAJ =========================
# RAMP_TIME_MS = 500        # czas rampy (ms)
# PAUSE_TIME_MS = 500       # pauza na full (ms)  
# CW_MIN_DUTY = 205        # CW min prędkość (102-512)
# CW_MAX_DUTY = 420        # CW max
# CCW_MIN_DUTY = 220       # CCW min
# CCW_MAX_DUTY = 250       # CCW max (neutral)
# CYCLE_PAUSE_MS = 200     # pauza między CW+CCW
# RAMP_STEPS = 50          # kroki w ramie (więcej = płynniej)
# ESC_CHANNEL = 0          # kanał PCA9685
# =============================================================================

i2c = I2C(0, sda=Pin(0), scl=Pin(1))
pca = PCA9685(i2c)
pca.freq(50)
NEUTRAL = 307
led = Pin("LED", Pin.OUT)

step_ms = RAMP_TIME_MS // RAMP_STEPS

print(f"Skonfigurowano: rampa {RAMP_TIME_MS}ms, pauza {PAUSE_TIME_MS}ms")

def ramp(start, end):
    for i in range(RAMP_STEPS + 1):
        duty = int(start + (end - start) * i / RAMP_STEPS)
        pca.duty(ESC_CHANNEL, duty)
        utime.sleep_ms(step_ms)

try:
    while True:
        print("CW..",CW_MAX_DUTY)
        ramp(CW_MAX_DUTY, CW_MAX_DUTY)
        utime.sleep_ms(PAUSE_TIME_MS)
        
        print("CCW..",CCW_MIN_DUTY)
        ramp(CCW_MIN_DUTY, CCW_MIN_DUTY)
        utime.sleep_ms(PAUSE_TIME_MS)
        
        led.toggle()
        utime.sleep_ms(CYCLE_PAUSE_MS)

except KeyboardInterrupt:
    pca.duty(ESC_CHANNEL, NEUTRAL)
    led.value(0)
    print("STOP.")
