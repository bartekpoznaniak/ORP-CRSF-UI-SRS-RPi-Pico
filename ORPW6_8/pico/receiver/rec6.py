# pico_logger_safe_fixed_crc.py — CRSF monitor na Pico z poprawnym dekodowaniem 11-bit + CRC
from machine import UART, Pin
import sys, time

# --- Bezpieczne I/O ---
def safe_write(s):
    sys.stdout.write(s)

def safe_flush():
    try:
        sys.stdout.flush()
    except AttributeError:
        pass

# --- Sprzęt / UART ---
UART_ID = 1
TX_PIN  = 4   # Pico TX -> nieużywane w czytniku, ale ustawiamy
RX_PIN  = 5   # Pico RX <- SB Nano TX
BAUD    = 420000

uart = UART(UART_ID, baudrate=BAUD, bits=8, parity=None, stop=1,
            tx=Pin(TX_PIN), rx=Pin(RX_PIN),
            timeout=0, timeout_char=1, rxbuf=8192)

# --- Bufor cykliczny ---
BUF_SIZE = 16384
buf = bytearray(BUF_SIZE)
buf_start = 0
buf_len = 0

def compact_if_needed():
    global buf_start, buf_len
    if buf_start and buf_len:
        buf[:buf_len] = buf[buf_start:buf_start+buf_len]
    buf_start = 0

def feed_from_uart():
    global buf_start, buf_len
    free_tail = BUF_SIZE - (buf_start + buf_len)
    if free_tail == 0:
        compact_if_needed()
        free_tail = BUF_SIZE - (buf_start + buf_len)
        if free_tail == 0:
            # awaryjnie czyść
            buf_start = 0
            buf_len = 0
            free_tail = BUF_SIZE
    mv = memoryview(buf)
    n = uart.readinto(mv[buf_start + buf_len : buf_start + buf_len + free_tail])
    if n:
        buf_len += n
        return n
    return 0

def consume(n):
    global buf_start, buf_len
    buf_start += n
    buf_len   -= n
    if buf_start > (BUF_SIZE // 2):
        compact_if_needed()

# --- CRC8-ATM ---
def crc8_atm(data):
    crc = 0
    for b in data:
        crc ^= b
        for _ in range(8):
            crc = ((crc << 1) ^ 0x07) & 0xFF if (crc & 0x80) else ((crc << 1) & 0xFF)
    return crc

# --- Dekodery CRSF ---
def decode_channels_packed_11bit(payload, max_ch=16):
    out = []
    for ch in range(max_ch):
        bit_index = ch * 11
        byte_index = bit_index >> 3
        bit_offset = bit_index & 0x07
        if byte_index + 2 >= len(payload):
            break
        v = (payload[byte_index]
             | (payload[byte_index+1] << 8)
             | (payload[byte_index+2] << 16))
        v = (v >> bit_offset) & 0x07FF
        out.append(v)
    return out

def to_us(raw):
    us = 1000 + int((raw - 172) * (1000.0 / (1811 - 172)))
    if us < 800:  us = 800
    if us > 2200: us = 2200
    return us

def parse_linkstats(payload):
    if len(payload) < 10:
        return None
    s8 = lambda x: x - 256 if x > 127 else x
    return {
        "rssi1": s8(payload[0]),
        "rssi2": s8(payload[1]),
        "lq":    payload[2],
        "snr":   s8(payload[3]),
        "rf":    payload[4],
        "txp":   payload[5],
    }

# ANSI: wyczyść ekran i ukryj kursor
safe_write("\033[2J\033[H\033[?25l")
safe_flush()

last_print = time.ticks_ms()
last_rx_ms = time.ticks_ms()
channels_us = [1500]*16
linkstats = None
failsafe = True
FAILSAFE_MS = 200
PRINT_MS = 50

safe_write("CRSF monitor (Pico) — UART1 420k, GPIO4/5\n")
safe_flush()

# Dodatkowe: licznik złych ramek do diagnostyki
bad_crc = 0
bad_len = 0

try:
    while True:
        feed_from_uart()

        # Parser ramek
        while buf_len >= 4:
            first = buf[buf_start]
            if first not in (0xC8, 0xEE):  # CRSF adres
                consume(1)
                continue

            if buf_len < 2:
                break

            L = buf[buf_start + 1]  # LEN = TYPE + PAYLOAD + CRC
            if L < 2 or L > 64:     # sanity (CRSF typowo nie jest ogromny)
                bad_len += 1
                consume(1)
                continue

            total = 2 + L           # ADDR + LEN + (TYPE..CRC)
            if total > buf_len:
                break  # czekamy na resztę

            # memoryview na ramkę
            mv = memoryview(buf)[buf_start : buf_start + total]
            f_type = mv[2]
            payload = mv[3 : 1 + L - 1]      # bez CRC (ostatni bajt)
            crc_rx  = mv[1 + L]              # ostatni bajt ramki

            # CRC po TYPE + PAYLOAD
            if crc8_atm(mv[2 : 1 + L]) != crc_rx:
                bad_crc += 1
                consume(1)  # przesuń o 1 i szukaj następnej ramki
                continue

            # Mamy poprawną ramkę
            if f_type == 0x16:  # RC Channels Packed
                # zwykle payload 22 bajty dla 16 kanałów
                raw = decode_channels_packed_11bit(payload, max_ch=16)
                if raw:
                    channels_us = [to_us(v) for v in raw] + [1500]*(16-len(raw))
                    last_rx_ms = time.ticks_ms()
                    failsafe = False

            elif f_type == 0x14:  # Link Stats
                ls = parse_linkstats(payload)
                if ls:
                    linkstats = ls

            consume(total)

        # Failsafe
        now = time.ticks_ms()
        if time.ticks_diff(now, last_rx_ms) > FAILSAFE_MS:
            failsafe = True

        # Rysowanie
        if time.ticks_diff(now, last_print) > PRINT_MS:
            out = []
            out.append("\033[H")
            out.append("=== CRSF MONITOR (Pico) ===\n")
            out.append(f"FS: {'YES' if failsafe else 'NO '} | UART: 420000 | Pins: TX=GP4 RX=GP5\n")
            if linkstats:
                out.append(
                    f"Link: RSSI {linkstats['rssi1']}/{linkstats['rssi2']} dBm  "
                    f"LQ {linkstats['lq']}%  SNR {linkstats['snr']} dB  "
                    f"RF {linkstats['rf']}  TXp {linkstats['txp']}\n"
                )
            # Debug (opcjonalnie, odkomentuj 1‑2 linie poniżej gdy chcesz)
            # out.append(f"bad_crc={bad_crc} bad_len={bad_len}\n")

            out.append("-"*42 + "\n")
            for i in range(0, 16, 2):
                c1, c2 = channels_us[i], channels_us[i+1]
                out.append(f"CH{i+1:02}: {c1:<4} | CH{i+2:02}: {c2:<4}\n")
            out.append("-"*42 + "\n")
            safe_write("".join(out))
            safe_flush()
            last_print = now

        # time.sleep_ms(1)  # opcjonalnie

except KeyboardInterrupt:
    pass
finally:
    safe_write("\033[?25h\n")
    safe_flush()
