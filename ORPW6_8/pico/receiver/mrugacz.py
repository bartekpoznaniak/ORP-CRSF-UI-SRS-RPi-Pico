from machine import Pin
import time

# Dla Pico W użyj Pin("LED", Pin.OUT), dla zwykłego Pico Pin(25, Pin.OUT)
led = Pin("LED", Pin.OUT)

while True:
    for i in range(1000):
        led.toggle()
        time.sleep(0.2)
