import serial
import argparse
from datetime import datetime

# Konfiguracja CLI
parser = argparse.ArgumentParser(description='CRSF Raw Logger - Senior Version')
parser.add_argument('-p', '--port', default='/dev/ttyUSB0', help='Port (default: /dev/ttyUSB0)')
parser.add_argument('-b', '--baud', type=int, default=420000, help='Baudrate (default: 420000)')
args = parser.parse_args()

def log_raw(frame):
    """Loguje ramkę z timestampem i typem w HEX"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    # frame[0] to Sync, frame[1] to Length, frame[2] to Type
    f_type = f"0x{frame[2]:02X}"
    hex_data = " ".join(f"{b:02X}" for b in frame)
    print(f"[{timestamp}] TYPE:{f_type} | LEN:{len(frame):02} | RAW: {hex_data}")

try:
    ser = serial.Serial(args.port, args.baud, timeout=0)
    buffer = bytearray()
    print(f"--- Nasłuchiwanie na {args.port} ({args.baud}) ---")

    while True:
        chunk = ser.read(1024)
        if chunk:
            buffer.extend(chunk)

        while len(buffer) >= 4:
            # Szukamy nagłówka (0xC8 lub 0xEE)
            if buffer[0] not in [0xC8, 0xEE]:
                buffer.pop(0)
                continue

            # frame_len w CRSF to długość: Typ + Payload + CRC
            frame_len = buffer[1]
            full_packet_len = frame_len + 2 

            if len(buffer) < full_packet_len:
                break # Czekamy na resztę danych

            # Mamy pełną ramkę
            frame = buffer[:full_packet_len]
            log_raw(frame)
            
            del buffer[:full_packet_len]

except KeyboardInterrupt:
    print("\nLogowanie przerwane przez użytkownika.")
finally:
    if 'ser' in locals(): ser.close()
