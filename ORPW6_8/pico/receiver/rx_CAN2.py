import machine
import sys
import gc
import micropython
import time
from mcp2515 import MCP2515, CAN_500KBPS, MCP_8MHz

try:
    machine.UART(1).deinit()
except:
    pass

machine.Pin(5, machine.Pin.IN, machine.Pin.PULL_UP)
uart = machine.UART(1, baudrate=420000, tx=machine.Pin(4), rx=machine.Pin(5),
                    timeout=0, rxbuf=1024)
spi = machine.SPI(0, baudrate=1_000_000, polarity=0, phase=0,
                  sck=machine.Pin(18), mosi=machine.Pin(19), miso=machine.Pin(16))
cs = machine.Pin(17, machine.Pin.OUT)
cs.value(1)
can = MCP2515(spi, cs)
can.begin(CAN_500KBPS, MCP_8MHz)
#CAN_ID_FIRE  = 0x100

CAN_ID_FIRE  = 0x100
CAN_ID_OSW1  = 0x110   # oświetlenie 1
CAN_ID_OSW2  = 0x111   # oświetlenie 2

FIRE_PAYLOAD = bytearray([0xF1, 0x12, 0xE0, 0x00, 0x00, 0x00, 0x00, 0x00])
OSW_ON       = bytearray([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
OSW_OFF      = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])

FIRE_COOLDOWN = 500   # ms
OSW_COOLDOWN  = 300   # ms


_ch  = [0] * 16

@micropython.native
def decode_channels(payload, channels):
    bit_buf = 0
    bit_count = 0
    idx = 0
    for byte in payload:
        bit_buf |= byte << bit_count
        bit_count += 8
        while bit_count >= 11:
            channels[idx] = bit_buf & 0x07FF
            bit_buf >>= 11
            bit_count -= 11
            idx += 1
            if idx >= 16:
                return

buffer = bytearray()
gc.collect()
gc.disable()

sys.stdout.write('\x1b[2J\x1b[H\x1b[?25l')

# Rate-limit: wyświetlaj max co 100ms (10Hz) - UART czyta cały czas 50Hz!
last_display = time.ticks_ms()
_last_gc = 0

_fire_armed   = True
_fire_last    = 0
_osw_last_ch6 = -1    # poprzedni stan ch6 — edge detection
_osw_last_sent = 0

try:
    while True:
        # UART zawsze czyta pełną prędkością
        n = uart.any()
        if n:
            d = uart.read(n)
            if d:
                buffer.extend(d)

        pos = 0
        while pos + 3 < len(buffer):
            if buffer[pos] not in (0xC8, 0xEE):
                pos += 1
                continue

            frame_len = buffer[pos + 1]
            full_len = frame_len + 2

            if full_len < 4 or full_len > 64:
                pos += 1
                continue

            if pos + full_len > len(buffer):
                break

            if buffer[pos + 2] == 0x16:
                decode_channels(memoryview(buffer)[pos+3:pos+full_len-1], _ch)
                now = time.ticks_ms()

                # FIRE
                ch13 = _ch[12]
                if ch13 == 2 and _fire_armed:
                    can.sendMsgBuf(CAN_ID_FIRE, 0, 8, FIRE_PAYLOAD)
                    _fire_armed = False
                    _fire_last  = now
                if ch13 == 0 and not _fire_armed:
                    if time.ticks_diff(now, _fire_last) > FIRE_COOLDOWN:
                        _fire_armed = True

                # OSW
                ch6 = _ch[5]
                if ch6 != _osw_last_ch6:
                    if time.ticks_diff(now, _osw_last_sent) > OSW_COOLDOWN:
                        if ch6 == 2:
                            can.sendMsgBuf(CAN_ID_OSW1, 0, 8, OSW_ON)
                            can.sendMsgBuf(CAN_ID_OSW2, 0, 8, OSW_OFF)
                        elif ch6 == 4:
                            can.sendMsgBuf(CAN_ID_OSW2, 0, 8, OSW_ON)
                            can.sendMsgBuf(CAN_ID_OSW1, 0, 8, OSW_OFF)
                        elif ch6 == 0:
                            can.sendMsgBuf(CAN_ID_OSW1, 0, 8, OSW_OFF)
                            can.sendMsgBuf(CAN_ID_OSW2, 0, 8, OSW_OFF)
                        _osw_last_ch6  = ch6
                        _osw_last_sent = now

                # DISPLAY
                if time.ticks_diff(now, last_display) >= 100:
                    out  = '\x1b[H=== CRSF MONITOR (PICO) ===\n'
                    out += f'RAW TYPE: 0x16 | LEN: {full_len}\n'
                    out += '----------------------------------------\n'
                    for i in range(0, 16, 2):
                        out += f'CH{i+1:02}: {_ch[i]:<5} | CH{i+2:02}: {_ch[i+1]:<5}\n'
                    out += '----------------------------------------\n'
                    sys.stdout.write(out)
                    last_display = now

            pos += full_len          # ← POZA if 0x16, jeden poziom wyżej
            _last_gc += 1
            if _last_gc >= 20:
                gc.collect()
                _last_gc = 0
        if pos > 0:
            buffer = buffer[pos:]

except KeyboardInterrupt:
    pass
finally:
    gc.enable()
    sys.stdout.write('\x1b[?25h\nZatrzymano.\n')
