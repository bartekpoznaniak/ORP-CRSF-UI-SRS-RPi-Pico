import lgpio
import time

# Fizyczny pin 8 = GPIO 14 (BCM)
PIN = 14 

h = lgpio.gpiochip_open(0)
lgpio.gpio_claim_output(h, PIN)

print(f"Testuję Fizyczny Pin 8 (GPIO {PIN}). Szukaj prostokąta na oscylu!")

try:
    while True:
        lgpio.gpio_write(h, PIN, 1)
        time.sleep(0.1) # 100ms - szybki przebieg
        lgpio.gpio_write(h, PIN, 0)
        time.sleep(0.1)
except KeyboardInterrupt:
    lgpio.gpiochip_close(h)
