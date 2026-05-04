from machine import I2C, Pin
from pca9685 import PCA9685
import utime

# ==================== KONFIGURACJA =====================
ESC_CHANNEL = 0
FREQ_HZ = 50

NEUTRAL = 307

# Zakresy z Twoich testów
CW_MIN_DUTY  = 205
CW_MAX_DUTY  = 520
CCW_MIN_DUTY = 0
CCW_MAX_DUTY = 240

# Globalne granice (nie wyjedziemy poza nie)
GLOBAL_MIN = CCW_MIN_DUTY
GLOBAL_MAX = CW_MAX_DUTY

# Krok zmiany
STEP = 3

# Przyciski (pull-up, aktywne w stanie niskim)
BTN_UP   = Pin(14, Pin.IN, Pin.PULL_UP)   # inkrementacja
BTN_DOWN = Pin(15, Pin.IN, Pin.PULL_UP)   # dekrementacja

# Debounce i auto-repeat
DEBOUNCE_MS      = 25       # filtr drgań styków
REPEAT_DELAY_MS  = 400      # po tylu ms przytrzymania rusza auto-repeat
REPEAT_RATE_MS   = 60       # co ile ms kolejny krok w auto-repeat

# ==================== SPRZĘT ===========================
i2c = I2C(0, sda=Pin(0), scl=Pin(1))
pca = PCA9685(i2c)
pca.freq(FREQ_HZ)

current_duty = NEUTRAL
pca.duty(ESC_CHANNEL, current_duty)
print("Start. DUTY =", current_duty)

# ==================== POMOCNICZE =======================
def clamp(x, lo, hi):
    return lo if x < lo else hi if x > hi else x

def set_duty(d):
    global current_duty
    d = clamp(d, GLOBAL_MIN, GLOBAL_MAX)
    if d != current_duty:
        current_duty = d
        pca.duty(ESC_CHANNEL, d)
        # Info dodatkowe: kierunek względem NEUTRAL
        if d > NEUTRAL:
            dir_txt = "CW"
        elif d < NEUTRAL:
            dir_txt = "CCW"
        else:
            dir_txt = "NEUTRAL"
        print("DUTY =", d, "| DIR =", dir_txt)

def btn_pressed(btn: Pin) -> bool:
    """Prosty debounce: sprawdź niski -> odczekaj -> potwierdź niski."""
    if btn.value() == 0:
        utime.sleep_ms(DEBOUNCE_MS)
        return btn.value() == 0
    return False

def handle_button(btn: Pin, delta: int):
    """
    Obsługa przycisku z autorepeat:
    - pojedynczy krok po kliknięciu
    - po przytrzymaniu: powtarzanie co REPEAT_RATE_MS
    """
    if not btn_pressed(btn):
        return

    # pojedynczy krok
    set_duty(current_duty + delta)

    # auto-repeat po przytrzymaniu
    t0 = utime.ticks_ms()
    while btn.value() == 0:
        if utime.ticks_diff(utime.ticks_ms(), t0) >= REPEAT_DELAY_MS:
            # powtarzaj kroki w pętli
            set_duty(current_duty + delta)
            utime.sleep_ms(REPEAT_RATE_MS)
        else:
            utime.sleep_ms(5)

# ==================== PĘTLA GŁÓWNA =====================
try:
    while True:
        handle_button(BTN_UP,   +STEP)
        handle_button(BTN_DOWN, -STEP)
        utime.sleep_ms(10)

except KeyboardInterrupt:
    # awaryjnie zostawiamy na ostatniej wartości (nie wracamy do 307)
    print("Przerwano. Ostatni DUTY =", current_duty)
