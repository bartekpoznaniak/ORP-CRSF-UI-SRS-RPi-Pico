# MicroPython na Raspberry Pi Pico
from machine import UART, Pin
import time, sys, gc

# Konfiguracja zgodna z Twoim okablowaniem:
UART_ID = 1
TX_PIN  = 4   # Pico TX -> RX odbiornika (nieużywane w odczycie)
RX_PIN  = 5   # Pico RX <- TX odbiornika

BAUD = 420000  # CRSF standard
RXBUF = 4096   # duży bufor, by nie gubić bajtów

# Inicjalizacja UART z jawnie ustawionymi parametrami
uart = UART(
    UART_ID,
    baudrate=BAUD,
    bits=8,
    parity=None,
    stop=1,
    tx=Pin(TX_PIN),
    rx=Pin(RX_PIN),
    timeout=0,         # bez wait'u
    timeout_char=1,    # minimalne oczekiwanie na znak
    rxbuf=RXBUF
)

# Prealokowany bufor do szybkich odczytów
chunk = bytearray(512)

print("Start odczytu... (CTRL+C by przerwać)")
last = time.ticks_ms()
count = 0

while True:
    n = uart.readinto(chunk)
    if n and n > 0:
        # pokaż pierwsze 48 bajtów w linii (żeby nie zalać konsoli)
        sys.stdout.write(chunk[:min(n,48)].hex() + "\n")
        count += n
    # co 2s pokaż statystykę
    if time.ticks_diff(time.ticks_ms(), last) > 2000:
        print("odebrano bajtów:", count)
        last = time.ticks_ms()
        gc.collect()
