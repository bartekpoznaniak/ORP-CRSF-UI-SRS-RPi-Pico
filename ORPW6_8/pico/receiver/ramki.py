from machine import UART, Pin
import time

uart = UART(1, baudrate=420000, tx=Pin(4), rx=Pin(5))

while True:
    if uart.any():
        frame = uart.read()
        print(frame)   # surowa ramka CRSF
