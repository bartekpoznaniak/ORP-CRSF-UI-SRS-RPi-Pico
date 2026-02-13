#!/usr/bin/env python3
"""
CRSF Config Inspector - ELRS/CRSF Parameter Specialist
Filtruje RC_CHANNELS i LINK_STATISTICS, skupia się na konfiguracji.
"""

import serial
import argparse
from datetime import datetime

# Adresy i Typy
CRSF_ADDRESSES = [0xC8, 0xEA, 0xEE] # TX Module, Handset, Serial Bridge
INTERESTING_TYPES = {
    0x29: "DEVICE_INFO",
    0x2B: "PARAM_ENTRY (Discovery)",
    0x2C: "PARAM_READ",
    0x2D: "PARAM_WRITE",
    0x32: "COMMAND",
    0x3A: "ELRS_STATUS"
}

def crc8_dvb_s2(data):
    crc = 0
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc << 1) ^ 0xD5 if crc & 0x80 else crc << 1
    return crc & 0xFF

def parse_param_frame(frame):
    """Dekoduje ramkę zapisu/odczytu parametrów"""
    f_type = frame[2]
    if f_type == 0x2D: # PARAMETER_WRITE
        # Struktura: [Addr] [Len] [2D] [Dest] [Orig] [Index] [Value] [CRC]
        p_id = frame[5]
        val = frame[6]
        return f"---> ZAPIS: Parametr ID {p_id:3} | Nowa Wartość: {val:3}"
    elif f_type == 0x2B: # PARAMETER_SETTINGS_ENTRY
        return f"<--- INFO: Definicja parametru (Discovery)"
    return ""

def main():
    parser = argparse.ArgumentParser(description='CRSF Config Inspector')
    parser.add_argument('-p', '--port', default='/dev/ttyUSB0', help='Port (np. COM3 lub /dev/ttyUSB0)')
    parser.add_argument('-b', '--baud', type=int, default=420000, help='Baudrate (standard ELRS to 420000)')
    args = parser.parse_args()

    try:
        ser = serial.Serial(args.port, args.baud, timeout=0.05)
        buffer = bytearray()
        
        print(f"[*] Rozpoczęto nasłuchiwanie na {args.port}...")
        print("[*] Filtrowanie aktywne: Loguję tylko ramki konfiguracyjne.\n")

        while True:
            if ser.in_waiting > 0:
                buffer.extend(ser.read(ser.in_waiting))

            while len(buffer) >= 4:
                if buffer[0] not in [0xEE, 0xEA, 0xC8, 0xC0]: # Rozszerzona lista sync
                    buffer.pop(0)
                    continue

                frame_len = buffer[1]
                if frame_len < 2 or frame_len > 64:
                    buffer.pop(0)
                    continue
                
                full_packet_len = frame_len + 2
                if len(buffer) < full_packet_len:
                    break

                frame = bytes(buffer[:full_packet_len])
                calculated_crc = crc8_dvb_s2(frame[2:-1])
                
                if calculated_crc == frame[-1]:
                    f_type = frame[2]
                    if f_type in INTERESTING_TYPES:
                        ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                        t_name = INTERESTING_TYPES[f_type]
                        hex_dump = " ".join(f"{b:02X}" for b in frame)
                        
                        print(f"[{ts}] {t_name:20} | {hex_dump}")
                        
                        details = parse_param_frame(frame)
                        if details:
                            print(f"      {details}")
                    
                    del buffer[:full_packet_len]
                else:
                    buffer.pop(0)

    except KeyboardInterrupt:
        print("\nPrzerwano.")
    finally:
        if 'ser' in locals(): ser.close()

if __name__ == "__main__":
    main()
