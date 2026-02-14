import lgpio
import time

# Fizyczny pin 16 to GPIO 23 w numeracji BCM
PIN = 23 

# Otwieramy dostęp do chipa GPIO (na RPi 5 to zazwyczaj chip 0)
h = lgpio.gpiochip_open(0)
lgpio.gpio_claim_output(h, PIN)

print(f"Sygnał wysłany na GPIO {PIN} (Fizyczny pin 16). Spójrz na oscyloskop!")

try:
    while True:
        lgpio.gpio_write(h, PIN, 1) # Stan wysoki 3.3V
        time.sleep(0.2)             # Szybsze mruganie, żeby łatwiej złapać trigger
        lgpio.gpio_write(h, PIN, 0) # Stan niski 0V
        time.sleep(0.2)
except KeyboardInterrupt:
    print("\nZatrzymano.")
finally:
    lgpio.gpiochip_close(h)
