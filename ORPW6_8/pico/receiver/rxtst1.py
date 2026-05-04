import machine, time

uart = machine.UART(0, baudrate=420000,
                    tx=machine.Pin(0), rx=machine.Pin(1),
                    timeout=100, rxbuf=2048)

time.sleep_ms(500)
data = bytearray()
data.extend(uart.read(uart.any()) or b'')

types_found = {}
pos = 0
while pos + 3 < len(data):
    if data[pos] == 0xC8:
        frame_len = data[pos + 1]
        frame_type = data[pos + 2]
        types_found[frame_type] = types_found.get(frame_type, 0) + 1
        pos += frame_len + 2
    else:
        pos += 1

for t, count in types_found.items():
    label = {
        0x16: "RC CHANNELS (to chcemy!)",
        0x14: "Link Statistics",
        0x1C: "Attitude",
        0x08: "GPS",
        0x02: "GPS Extended",
    }.get(t, "nieznany")
    print(f"Type 0x{t:02X}: {count}x  <- {label}")