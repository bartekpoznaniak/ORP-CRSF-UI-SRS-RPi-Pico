# rc_pico_tx.py  –  Raspberry Pi Pico  (MicroPython)
#
# Rola: scalenie danych z drążków (ADS1115) i UI (RPI5 UART)
#       → budowanie ramki CRSF 0x16 → wysyłanie do HM ES24proTX
#
# Piny:
#   GP0/GP1  – I2C0  SDA/SCL  → ADS1115
#   GP4(TX)  – UART1 TX       → RPI5 GPIO5 (RX)
#   GP5(RX)  – UART1 RX       → RPI5 GPIO4 (TX)
#   GP12     – UART0 TX       → 74HC04 → ES24proTX  (420000 baud)
#
# Mapowanie kanałów CRSF:
#   CH1  A0  prawy pionowo  (góra/dół)
#   CH2  A1  prawy poziomo  (lewo/prawo)
#   CH3  A2  lewy pionowy   (góra/dół)
#   CH4  A3  lewy poziomo   (lewo/prawo)
#   CH5-CH7  bity przycisków z RPI5
#   CH8-CH11 suwaki GUI z RPI5
#   CH12-CH16 rezerwa (992)

import machine
import time
import struct
from ads1x15 import ADS1115

# ─── Stałe CRSF ──────────────────────────────────────────────

CRSF_MIN = 172
CRSF_MAX = 1811
CRSF_CTR = 992

ADS_VREF = 4.096
ADS_RES  = 32768

CRSF_HZ          = 100
CRSF_INTERVAL_US = 1_000_000 // CRSF_HZ   # 10 000 µs

# ─── Kalibracja czujników Halla ──────────────────────────────
# Format: (V_min, V_max, inverted)
# inverted=True gdy wychylenie "dodatnie" daje NIŻSZE napięcie

STICK_CAL = {
    0: (0.45, 2.84, False),  # A0 prawy pionowo  — góra=2.84V
    1: (0.16, 2.83, True),   # A1 prawy poziomo  — prawo=0.16V (odwrócony)
    2: (0.45, 2.90, True),   # A2 lewy pionowy   — góra=0.45V  (odwrócony)
    3: (0.23, 3.03, False),  # A3 lewy poziomo   — prawo=3.03V
}

# ─── Protokół UART RPI5→PICO ─────────────────────────────────

UART_FRAME_LEN = 27
UART_SOF       = 0xAA
UART_EOF       = 0xBB

# ─── Inicjalizacja hardware ──────────────────────────────────

# I2C0 → ADS1115
i2c = machine.I2C(0, sda=machine.Pin(0), scl=machine.Pin(1), freq=100_000)
devices = i2c.scan()
if not devices:
    raise RuntimeError("ADS1115 nie znaleziony na I2C!")
ads = ADS1115(i2c, address=devices[0], gain=1)
print(f"[I2C] ADS1115 @ {hex(devices[0])}")

# UART1  GP4(TX) / GP5(RX)  ← komunikacja z RPI5
uart_rpi = machine.UART(1, baudrate=57600,
                        tx=machine.Pin(4), rx=machine.Pin(5),
                        bits=8, parity=0, stop=1,
                        rxbuf=128)

print("[UART1] RPI5 link gotowy @ 57200 baud (GP4 TX / GP5 RX)")

# UART0  GP12(TX) → 74HC04 → ES24proTX
uart_crsf = machine.UART(0, baudrate=420_000,
                         tx=machine.Pin(12), rx=machine.Pin(13),
                         bits=8, parity=None, stop=1,
                         txbuf=64)
print("[UART0] CRSF TX gotowy @ 420000 baud (GP12)")

# ─── Stan aplikacji ──────────────────────────────────────────

_channels = [CRSF_CTR] * 16   # 16 kanałów CRSF
_gui_ch   = [CRSF_CTR] * 12   # dane od RPI5
_rxbuf    = bytearray()        # bufor UART od RPI5

# ─── Funkcje pomocnicze ──────────────────────────────────────

def map_crsf(v: float, v_min: float, v_max: float) -> int:
    """Napięcie → CRSF 172-1811."""
    r = max(0.0, min(1.0, (v - v_min) / (v_max - v_min)))
    return int(CRSF_MIN + r * (CRSF_MAX - CRSF_MIN))


def read_sticks() -> list:
    """Odczyt 4 kanałów ADS1115 z kalibracją Halla."""
    vals = []
    for ch in range(4):
        raw = ads.read(4, ch)
        v   = raw * (ADS_VREF / ADS_RES)
        v_min, v_max, inverted = STICK_CAL[ch]
        crsf = map_crsf(v, v_min, v_max)
        if inverted:
            crsf = CRSF_MIN + CRSF_MAX - crsf
        vals.append(crsf)
        time.sleep_ms(3)
    return vals


def crc8_dvb_s2(data: bytes) -> int:
    crc = 0
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = ((crc << 1) ^ 0xD5) if (crc & 0x80) else (crc << 1)
    return crc & 0xFF


def pack_channels(channels: list) -> bytes:
    """Pakuje 16 kanałów 11-bit → 22 bajty CRSF payload."""
    payload  = bytearray(22)
    cur_byte = 0
    cur_bit  = 0
    for val in channels:
        val = max(0, min(2047, int(val)))
        for j in range(11):
            if val & (1 << j):
                payload[cur_byte] |= (1 << cur_bit)
            cur_bit += 1
            if cur_bit == 8:
                cur_byte += 1
                cur_bit  = 0
    return bytes(payload)


def build_crsf_frame(channels: list) -> bytes:
    """Buduje pełną ramkę CRSF RC_CHANNELS_PACKED (0x16)."""
    frame_type = 0x16
    payload    = pack_channels(channels)
    crc        = crc8_dvb_s2(bytes([frame_type]) + payload)
    return bytes([0xEE, 0x18, frame_type]) + payload + bytes([crc])


# ─── Parser ramki UART od RPI5 ───────────────────────────────
def try_parse_rpi_frame(buf: bytearray):
    """Szuka i parsuje ramkę SOF…EOF w buforze."""
    while len(buf) >= UART_FRAME_LEN:
        if buf[0] != UART_SOF:
            buf[:] = buf[1:]
            continue
        if buf[UART_FRAME_LEN - 1] != UART_EOF:
            buf[:] = buf[1:]
            continue
        payload = buf[1:25]
        crc_rx  = buf[25]
        crc_cal = 0
        for b in payload:
            crc_cal ^= b
        if crc_rx != crc_cal:
            print(f"[PARSE] CRC FAIL rx={crc_rx:#04x} cal={crc_cal:#04x}")
            buf[:] = buf[1:]
            continue
        values = list(struct.unpack("<12H", payload))
        buf[:] = buf[UART_FRAME_LEN:]
        return values, buf
    return None, buf




# ─── Pętla główna ────────────────────────────────────────────
print("[MAIN] Start pętli CRSF @ 100 Hz\n")

last_crsf_us = time.ticks_us()

while True:

    # 1. Odbierz dane od RPI5 (non-blocking)
    if uart_rpi.any():
        raw = uart_rpi.read(uart_rpi.any())
        if raw:
            # print(f"[RX] {raw.hex()}")
            _rxbuf.extend(raw)
        # Ogranicz bufor do max 5 ramek żeby nie rosnął w nieskończoność
        if len(_rxbuf) > UART_FRAME_LEN * 5:
            # Znajdź ostatni SOF i zacznij od niego
            last_sof = _rxbuf.rfind(UART_SOF)
            if last_sof > 0:
                _rxbuf[:] = _rxbuf[last_sof:]
    # Opróżnij bufor
        while True:
            result, _rxbuf = try_parse_rpi_frame(_rxbuf)
            if result is None:
                break
            _gui_ch = result

    # 2. Sprawdź czy czas na ramkę CRSF
    now = time.ticks_us()
    if time.ticks_diff(now, last_crsf_us) >= CRSF_INTERVAL_US:
        last_crsf_us = now

        # 2a. Drążki → CH1-CH4
        sticks = read_sticks()
        _channels[0] = sticks[0]
        _channels[1] = sticks[1]
        _channels[2] = sticks[2]
        _channels[3] = sticks[3]

        # 2b. GUI → CH5-CH16
        for i in range(12):
            _channels[4 + i] = _gui_ch[i]

        # 2c. Buduj i wyślij ramkę CRSF
        frame = build_crsf_frame(_channels)
        uart_crsf.write(frame)

        # DEBUG — zakomentuj po testach
        # print(_channels[:8])

    # 3. Micro-yield
    time.sleep_us(500)
