import serial
import time

def crsf_crc8(data):
    crc = 0
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x80:
                crc = (crc << 1) ^ 0xD5
            else:
                crc <<= 1
            crc &= 0xFF
    return crc

port = "/dev/ttyAMA0"
baud = 460800 

# Nagłówek: Sync (0xEE), Długość (0x18), Typ (0x16 - RC Channels)
header = bytes([0xEE, 0x18, 0x16])
# 22 bajty danych kanałów (środek: 0x03E0)
payload = bytes([0xE0, 0x03, 0x1F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
# Obliczamy CRC z Typu i Payloadu
crc = crsf_crc8(header[2:] + payload)
frame = header + payload + bytes([crc])

try:
    with serial.Serial(port, baud, timeout=1) as ser:
        print(f"Nadaję poprawną ramkę CRSF na {baud} bps...")
        while True:
            ser.write(frame)
            time.sleep(0.01) # 100Hz
except Exception as e:
    print(f"Błąd: {e}")
