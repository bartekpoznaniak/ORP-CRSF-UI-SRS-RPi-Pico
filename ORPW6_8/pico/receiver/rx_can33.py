# ============================================================
#  CAN MASTER — Raspberry Pi Pico + MCP2515
#  CRSF (ELRS) → CAN bus
#
#  Konfiguracja:
#    SWITCH_MAP  — przyciski na CH6 (maska bitu → CAN ID)
#    FIRE_*      — wyzwalacz na CH13
# ============================================================

import machine
import sys
import gc
import micropython
import time
from mcp2515 import MCP2515, CAN_500KBPS, MCP_8MHz

# ============================================================
#  Hardware init
# ============================================================
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

# ============================================================
#  Konfiguracja suwaków (CH9-CH12)
#  Format: indeks_kanału → CAN_ID
# ============================================================
SLIDER_MAP = {
    8:  0x120,   # CH9
    9:  0x121,   # CH10
    10: 0x122,   # CH11
    11: 0x123,   # CH12
}

SLIDER_COOLDOWN  = 50    # ms — jak często wysyłać podczas ruchu
SLIDER_DEADBAND  = 10    # jednostki CRSF — ignoruj mikrodrgania

# ============================================================
#  Konfiguracja ARM (CH5)
# ============================================================
CAN_ID_ARM    = 0x101
ARM_THRESHOLD = 1000   # powyżej tej wartości = ARMED
ARM_COOLDOWN  = 500    # ms

# ============================================================
#  Payloady CAN
# ============================================================
OSW_ON       = bytearray([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
OSW_OFF      = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
FIRE_PAYLOAD = bytearray([0xF1, 0x12, 0xE0, 0x00, 0x00, 0x00, 0x00, 0x00])

# ============================================================
#  Konfiguracja FIRE (CH13)
# ============================================================
CAN_ID_FIRE   = 0x100
FIRE_COOLDOWN = 500   # ms

# ============================================================
#  Konfiguracja przełączników (CH6)
#  Dodanie nowego przycisku = jedna linia tutaj
# ============================================================
SWITCH_MAP = {
    0x02: 0x110,   # P1
    0x04: 0x111,   # P2
    0x08: 0x112,   # P3
    0x10: 0x113,   # P4
    0x20: 0x114,   # P5
    0x40: 0x115,   # P6
}

OSW_COOLDOWN = 400   # ms

# ============================================================
#  Stan przełączników — generowany automatycznie ze SWITCH_MAP
# ============================================================
_sw_state = {mask: False for mask in SWITCH_MAP}
_sw_sent  = {mask: 0     for mask in SWITCH_MAP}



_arm_last      = False
_arm_last_sent = 0

_slider_last      = {ch: -1 for ch in SLIDER_MAP}   # -1 = nigdy nie wysłany
_slider_last_sent = {ch: 0  for ch in SLIDER_MAP}

# ============================================================
#  Funkcja obsługi suwaków
# ============================================================
def process_sliders(channels, now):
    for ch_idx, can_id in SLIDER_MAP.items():
        raw = channels[ch_idx]                        # 172–1810
        val = (raw - 172) * 255 // (1810 - 172)      # mapuj → 0–255
        val = max(0, min(255, val))                   # clamp

        # Wyślij tylko gdy zmiana > deadband
        if abs(val - _slider_last[ch_idx]) > SLIDER_DEADBAND:
            if time.ticks_diff(now, _slider_last_sent[ch_idx]) > SLIDER_COOLDOWN:
                payload = bytearray([val, 0x00, 0x00, 0x00,
                                     0x00, 0x00, 0x00, 0x00])
                can.sendMsgBuf(can_id, 0, 8, payload)
                sys.stdout.write('SLIDER CH{} → 0x{:03X} val={}\n'.format(
                    ch_idx + 1, can_id, val))
                _slider_last[ch_idx]      = val
                _slider_last_sent[ch_idx] = now



# ============================================================
#  Funkcja obsługi przełączników
# ============================================================
def process_switches(ch_value, now):
    for mask, can_id in SWITCH_MAP.items():
        current = bool(ch_value & mask)
        if current != _sw_state[mask]:
            if time.ticks_diff(now, _sw_sent[mask]) > OSW_COOLDOWN:
                can.sendMsgBuf(can_id, 0, 8,
                               OSW_ON if current else OSW_OFF)
                sys.stdout.write('SW 0x{:03X} {}\n'.format(
                    can_id, "ON " if current else "OFF"))
                _sw_state[mask] = current
                _sw_sent[mask]  = now
# ============================================================
#  Funkcja obsługi arm
# ============================================================         
def process_arm(ch_value, now):
    global _arm_last, _arm_last_sent
    armed_now = ch_value > ARM_THRESHOLD   # 172=False, 1810=True

    if armed_now != _arm_last:
        if time.ticks_diff(now, _arm_last_sent) > ARM_COOLDOWN:
            can.sendMsgBuf(CAN_ID_ARM, 0, 8,
                           OSW_ON if armed_now else OSW_OFF)
            sys.stdout.write('ARM: {}\n'.format(
                "ARMED  " if armed_now else "DISARMED"))
            _arm_last      = armed_now
            _arm_last_sent = now
# ============================================================
#  Dekoder kanałów CRSF
# ============================================================
_ch = [0] * 16

@micropython.native
def decode_channels(payload, channels):
    bit_buf   = 0
    bit_count = 0
    idx = 0
    for byte in payload:
        bit_buf   |= byte << bit_count
        bit_count += 8
        while bit_count >= 11:
            channels[idx] = bit_buf & 0x07FF
            bit_buf   >>= 11
            bit_count  -= 11
            idx += 1
            if idx >= 16:
                return

# ============================================================
#  Zmienne robocze
# ============================================================
buffer       = bytearray()
last_display = time.ticks_ms()
_last_gc     = 0

_fire_armed  = True
_fire_last   = 0

gc.collect()
gc.disable()

sys.stdout.write('\x1b[2J\x1b[H\x1b[?25l')

# ============================================================
#  Pętla główna
# ============================================================
try:
    while True:
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
            full_len  = frame_len + 2

            if full_len < 4 or full_len > 64:
                pos += 1
                continue

            if pos + full_len > len(buffer):
                break

            if buffer[pos + 2] == 0x16:
                decode_channels(memoryview(buffer)[pos+3:pos+full_len-1], _ch)
                now = time.ticks_ms()

                # --- FIRE (CH13) ---
                ch13 = _ch[12]
                if ch13 == 2 and _fire_armed:
                    can.sendMsgBuf(CAN_ID_FIRE, 0, 8, FIRE_PAYLOAD)
                    sys.stdout.write('\x1b[10;0H>>> FIRE! CAN wysłany <<<\n')
                    _fire_armed = False
                    _fire_last  = now
                if ch13 == 0 and not _fire_armed:
                    if time.ticks_diff(now, _fire_last) > FIRE_COOLDOWN:
                        _fire_armed = True

                # --- Przełączniki (CH6) ---
                process_switches(_ch[5], now)

                # --- ARM (CH5) ---
                process_arm(_ch[4], now)  
                # --- Sliders ch9-ch12 ---
                process_sliders(_ch, now)

                # --- Display 10 Hz ---

                if time.ticks_diff(now, last_display) >= 100:
                    out  = '\x1b[H=== CAN MASTER (PICO) ===\n'
                    out += f'RAW TYPE: 0x16 | LEN: {full_len}\n'
                    out += '----------------------------------------\n'
                    for i in range(0, 16, 2):
                        out += f'CH{i+1:02}: {_ch[i]:<5} | CH{i+2:02}: {_ch[i+1]:<5}\n'
                    out += '----------------------------------------\n'
                    out += 'ARM: {}\n'.format("*** ARMED ***" if _arm_last else "disarmed")

                    slider_line = ' '.join(
                        'S{}:{:3d}'.format(i + 1, max(0, min(255,
                            (_ch[ch] - 172) * 255 // (1810 - 172))))
                        for i, ch in enumerate(SLIDER_MAP)
                    )
                    out += slider_line + '\n'

                    sw_line = ' '.join(
                        'P{}:{}'.format(
                            list(SWITCH_MAP.keys()).index(m) + 1,
                            "ON " if _sw_state[m] else "OFF"
                        )
                        for m in SWITCH_MAP
                    )
                    out += sw_line + '\n'

                    sys.stdout.write(out)
                    last_display = now


#                 if time.ticks_diff(now, last_display) >= 100:
#                     out  = '\x1b[H=== CAN MASTER (PICO) ===\n'
#                     out += f'RAW TYPE: 0x16 | LEN: {full_len}\n'
#                     out += '----------------------------------------\n'
#                     for i in range(0, 16, 2):
#                         out += f'CH{i+1:02}: {_ch[i]:<5} | CH{i+2:02}: {_ch[i+1]:<5}\n'
#                     out += '----------------------------------------\n'
#                     out += 'ARM: {}\n'.format("*** ARMED ***" if _arm_last else "disarmed")
#                     slider_line = ' '.join('S{}:{:3d}'.format(i + 1, max(0, min(255,(_ch[ch] - 172) * 255 // (1810 - 172))))
#                     for i, ch in enumerate(SLIDER_MAP)
# )
#                     out += slider_line + '\n'
#                     out += sw_line + '\n'
#                     sw_line = ' '.join(
#                         'P{}:{}'.format(
#                             list(SWITCH_MAP.keys()).index(m) + 1,
#                             "ON " if _sw_state[m] else "OFF"
#                         )
#                         for m in SWITCH_MAP
#                     )
#                     out += sw_line + '\n'
#                     sys.stdout.write(out)
#                     last_display = now

            pos      += full_len
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