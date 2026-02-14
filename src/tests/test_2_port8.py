import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Dostępne GPIO na RPi5 (0-27, pomiń ID_SD jeśli problemy)
pins = [0,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27]

print("Test wszystkich GPIO RPi5 (podłącz LED/multimetr)...")

# Setup WSZYSTKICH pinów na start
for pin in pins:
    GPIO.setup(pin, GPIO.OUT)

try:
    for pin in pins:
        print(f"Mrugam GPIO{pin} (pin fiz: pinout.xyz)...")
        for _ in range(5):  # 5 mrugnięć
            GPIO.output(pin, GPIO.HIGH)
            time.sleep(0.2)
            GPIO.output(pin, GPIO.LOW)
            time.sleep(0.2)
        time.sleep(1)  # Pauza między pinami
except KeyboardInterrupt:
    print("\nPrzerwano przez użytkownika.")
finally:
    GPIO.cleanup()  # Cleanup TYLKO na końcu
    print("GPIO wyczyszczone.")
