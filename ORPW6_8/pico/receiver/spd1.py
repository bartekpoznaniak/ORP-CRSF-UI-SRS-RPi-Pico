from machine import I2C, Pin
from pca9685 import PCA9685
import utime

# PARAMETRY
ESC_CH = 0
NEUTRAL = 307
SPEED_STEP = 10        # krok prędkości (+/-10 duty)
MAX_DUTY = 512

i2c = I2C(0, sda=Pin(0), scl=Pin(1))
pca = PCA9685(i2c)
pca.freq(50)
led = Pin("LED", Pin.OUT)

cw_duty = 307
ccw_duty = 307
mode_cw = True  # True=CW, False=CCW

print("KLAWIATURA STEROWANIE:")
print("↑/↓: prędkość | ←: CCW | →: CW | SPACE: stop | Q: quit")
print("Aktualne: CW={} | CCW={}".format(cw_duty, ccw_duty))

def set_motor(duty):
    pca.duty(ESC_CH, duty)
    led.value(duty != NEUTRAL)
    print(f"Duty: {duty} | RPM wizualnie: [1-10]?", end='\r')

set_motor(NEUTRAL)

while True:
    try:
        # Symulacja klawiatury przez serial (wpisz cyfry!)
        cmd = input("Wpisz: +10/-10/SWITCH/STOP/Q: ").strip().upper()
        
        if cmd == 'Q':
            break
        elif cmd == 'STOP' or cmd == 'SPACE':
            cw_duty = ccw_duty = NEUTRAL
            set_motor(NEUTRAL)
        elif cmd == 'SWITCH':
            mode_cw = not mode_cw
            duty = cw_duty if mode_cw else ccw_duty
            set_motor(duty)
            print(f"\nTryb: {'CW' if mode_cw else 'CCW'}")
        elif cmd.startswith('+'):
            step = int(cmd[1:])
            if mode_cw:
                cw_duty = min(MAX_DUTY, cw_duty + step)
                set_motor(cw_duty)
            else:
                ccw_duty = max(102, ccw_duty - step)  # CCW niżej=szybciej
                set_motor(ccw_duty)
        elif cmd.startswith('-'):
            step = int(cmd[1:])
            if mode_cw:
                cw_duty = max(205, cw_duty - step)
                set_motor(cw_duty)
            else:
                ccw_duty = min(307, ccw_duty + step)
                set_motor(ccw_duty)
        else:
            print("\nBłąd! +10/-10/SWITCH/STOP/Q")
            
    except (KeyboardInterrupt, ValueError):
        set_motor(NEUTRAL)
        print("\nSTOP.")

pca.duty(ESC_CH, NEUTRAL)
print("KONIEC.")
