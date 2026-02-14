import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

pins = [0,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27]

print("SYNCHRONICZNY test: WSZYSTKIE piny ON/OFF razem (Ctrl+C stop)...")

# Setup wszystkich
for pin in pins:
    GPIO.setup(pin, GPIO.OUT)

try:
    while True:
        # WSZYSTKIE ON
        for pin in pins:
            GPIO.output(pin, GPIO.HIGH)
        time.sleep(0.2)
        
        # WSZYSTKIE OFF
        for pin in pins:
            GPIO.output(pin, GPIO.LOW)
        time.sleep(0.2)
        
except KeyboardInterrupt:
    print("\nZatrzymano.")
finally:
    GPIO.cleanup()
    print("GPIO wyczyszczone.")
