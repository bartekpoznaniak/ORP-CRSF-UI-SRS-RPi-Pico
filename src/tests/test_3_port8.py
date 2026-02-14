import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

pins = [0,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27]

print("SZYBKI test GPIO RPi5 (~5s)...")

for pin in pins:
    GPIO.setup(pin, GPIO.OUT)

try:
    for pin in pins:
        print(f"GPIO{pin}", end=' ')
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(pin, GPIO.LOW)
        time.sleep(0.1)
        time.sleep(0.2)  # Krótka pauza
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()
print("\nGOTOWE!")
