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
# Skanujemy okolice Twojego baudrate
test_bauds = range(460000, 462000, 100)

header = bytes([0xEE, 0x18, 0x16])
payload = bytes([0xE0, 0x03, 0x1F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
crc = crsf_crc8(header[2:] + payload)
frame = header + payload + bytes([crc])

print("Rozpoczynam precyzyjne skanowanie baudrate...")

for b in test_bauds:
    print(f"Testuję: {b} bps", end='\r')
    try:
        with serial.Serial(port, b, timeout=0.05) as ser:
            # Wysyłamy 50 ramek na każdej prędkości
            for _ in range(50):
                ser.write(frame)
                time.sleep(0.01)
    except:
        continue

print("\nKoniec skanowania. Czy dioda ustabilizowała się na którymś etapie?")
