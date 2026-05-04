from machine import I2C, Pin
from pca9685 import PCA9685
import utime

i2c = I2C(0, sda=Pin(0), scl=Pin(1))
pca = PCA9685(i2c)
pca.freq(50)

ESC_CH = 0  # kanał ESC
NEUTRAL = 307  # 1.5ms = STOP
FORWARD_MIN = 205  # ~1.1ms forward slow
FORWARD_MAX = 512  # 2ms forward full
REVERSE_MIN = 102  # 1ms reverse slow  
REVERSE_MAX = 307  # 1.5ms reverse full (nie przekraczaj!)

led = Pin("LED", Pin.OUT)

def esc_set(duty):
    pca.duty(ESC_CH, duty)
    print(f"PWM duty: {duty}")

print("ESC 2-kierunkowy TEST - Ctrl+C stop")
led.value(1)

try:
    while True:
        # Forward slow → full
        print("FORWARD...")
        for d in range(FORWARD_MIN, FORWARD_MAX+1, 20):
            esc_set(d)
            utime.sleep(0.3)
        
        # Neutral stop 2s
        print("STOP")
        esc_set(NEUTRAL)
        utime.sleep(2)
        
        # Reverse slow → full
        print("REVERSE...")
        for d in range(REVERSE_MIN, NEUTRAL, 10):
            esc_set(d)
            utime.sleep(0.3)
        
        # Stop
        esc_set(NEUTRAL)
        utime.sleep(2)

except KeyboardInterrupt:
    esc_set(NEUTRAL)
    led.value(0)
    print("STOP neutral.")
