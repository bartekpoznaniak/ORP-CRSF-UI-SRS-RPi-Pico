import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(14, GPIO.OUT)  # GPIO14 = pin 8

try:
    while True:
        GPIO.output(14, GPIO.HIGH)   # Włącz LED
        time.sleep(0.5)
        GPIO.output(14, GPIO.LOW)    # Wyłącz
        time.sleep(0.5)
except KeyboardInterrupt:
    print("\nZatrzymano.")
GPIO.cleanup()
