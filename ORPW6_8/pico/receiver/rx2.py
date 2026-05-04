import machine, time

uart = machine.UART(0, baudrate=420000,
                    tx=machine.Pin(0), rx=machine.Pin(1),
                    timeout=100, rxbuf=256)

print("Czekam 3 sekundy na bajty...")
time.sleep(3)
n = uart.any()
print(f"Odebrano bajtow: {n}")
if n:
    print([hex(b) for b in uart.read(min(n, 16))])
else:
    print("ZERO bajtow - TX wylaczony lub zly pin")