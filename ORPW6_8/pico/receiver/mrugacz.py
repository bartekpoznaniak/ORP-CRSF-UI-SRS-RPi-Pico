from machine import Pin
import utime
led = Pin("LED", Pin.OUT)
print("Mrugacz v3")
for i in range(10):
    led.toggle()
    print(f"Mrug {i+1}")
    utime.sleep_ms(300)
print("KONIEC!")
