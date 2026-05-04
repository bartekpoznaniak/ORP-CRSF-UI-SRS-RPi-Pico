from machine import I2C, Pin
from pca9685 import PCA9685
import utime

# ==================== KONFIGURACJA =====================
ESC_CHANNEL = 0
NEUTRAL = 307

# Zakresy dla Twojego ESC / H-bridge
CW_MAX_DUTY = 420
CCW_MAX_DUTY = 240

# Przyciski (Pin.IN + pull-up)
BTN_CW = Pin(14, Pin.IN, Pin.PULL_UP)      # obrót w prawo
BTN_CCW = Pin(15, Pin.IN, Pin.PULL_UP)     # obrót w lewo

# ==================== INICJALIZACJA =====================
i2c = I2C(0, sda=Pin(0), scl=Pin(1))
pca = PCA9685(i2c)
pca.freq(50)

current_duty = NEUTRAL
pca.duty(ESC_CHANNEL, current_duty)

print("Start OK. Aktualny duty =", current_duty)

# ==================== FUNKCJE ===========================
def set_duty(d):
    global current_duty
    if d != current_duty:
        current_duty = d
        pca.duty(ESC_CHANNEL, d)
        print("DUTY =", d)

def stop_motor():
    set_duty(NEUTRAL)

def run_cw():
    set_duty(CW_MAX_DUTY)

def run_ccw():
    set_duty(CCW_MAX_DUTY)

# ==================== PĘTLA GŁÓWNA ======================
try:
    while True:
        cw_pressed = (BTN_CW.value() == 0)
        ccw_pressed = (BTN_CCW.value() == 0)

        if cw_pressed and not ccw_pressed:
            run_cw()
        elif ccw_pressed and not cw_pressed:
            run_ccw()
        else:
            stop_motor()

        utime.sleep_ms(20)

except KeyboardInterrupt:
    stop_motor()
    print("STOP.")
