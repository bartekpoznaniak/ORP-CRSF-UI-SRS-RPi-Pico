from machine import I2C, Pin
from pca9685 import PCA9685
import utime

i2c = I2C(0, sda=Pin(0), scl=Pin(1))
pca = PCA9685(i2c)
pca.freq(50)  # 20ms period

ESC_CH = 0
NEUTRAL = 307     # 1.5ms = stop
CW_MIN = 205      # CW slow  
CW_MAX = 512      # CW full
CCW_MIN = 102     # CCW slow
CCW_MAX = NEUTRAL # CCW full

led = Pin("LED", Pin.OUT)
print("CW 20ms ramp (50ms up/down) -> PAUZA 20ms -> CCW 20ms ramp -> powtórz")

def ramp(start, end, steps=25):  # 50ms total ramp (25 kroków x 2ms)
    for i in range(steps + 1):
        duty = int(start + (end - start) * i / steps)
        pca.duty(ESC_CH, duty)
        utime.sleep_ms(2)
    pca.duty(ESC_CH, end)  # trzymaj full

try:
    while True:
        print("CW ramp...")
        ramp(CW_MIN, CW_MAX)  # 50ms CW full
        utime.sleep_ms(1000)    # pauza 20ms full CW
        
        print("CCW ramp...")
        ramp(CCW_MIN, CCW_MAX) # 50ms CCW full  
        utime.sleep_ms(20)     # pauza 20ms full CCW
        
        led.toggle()
        utime.sleep_ms(100)    # między cyklami

except KeyboardInterrupt:
    pca.duty(ESC_CH, NEUTRAL)
    led.value(0)
    print("STOP neutral.")
