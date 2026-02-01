#!/usr/bin/env python3
"""
CRSF Raw Logger - Enhanced Edition (Anti False-Sync)
Ignoruje false-sync artifacts z payloadu
"""

import serial
import argparse
from datetime import datetime

# Adresy CRSF zgodne ze specyfikacją
CRSF_ADDRESSES = [0xC0, 0xC2, 0xC8, 0xCA, 0xCC, 0xEA, 0xEC, 0xEE]

# Słownik typów ramek dla czytelności
FRAME_TYPES = {
    0x02: "GPS",
    0x07: "VARIO",
    0x08: "BATTERY_SENSOR",
    0x14: "LINK_STATISTICS",
    0x16: "RC_CHANNELS_PACKED",
    0x1D: "ATTITUDE",
    0x1E: "FLIGHT_MODE",
    0x28: "DEVICE_PING",
    0x29: "DEVICE_INFO",
    0x2B: "PARAMETER_SETTINGS_ENTRY",
    0x2C: "PARAMETER_READ",
    0x2D: "PARAMETER_WRITE",
    0x32: "COMMAND",
    0x3A: "ELRS_STATUS",
}

# Statystyki globalne
stats = {
    'crc_ok': 0,
    'total_frames': 0,
    'frame_types': {},
    'false_sync_dropped': 0
}

def crc8_dvb_s2(data):
    """
    CRC8 DVB-S2 (polynomial 0xD5) używany w CRSF
    data: bajty od Type do końca Payload (bez CRC byte)
    """
    crc = 0
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc << 1) ^ 0xD5 if crc & 0x80 else crc << 1
    return crc & 0xFF

def log_raw(frame):
    """Loguje poprawną ramkę z timestampem i typem"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    
    # Wyciągnij adres, długość, typ
    address = frame[0]
    length = frame[1]
    frame_type = frame[2]
    
    # Przyjazna nazwa typu
    type_name = FRAME_TYPES.get(frame_type, f"UNKNOWN_0x{frame_type:02X}")
    
    # HEX dump
    hex_data = " ".join(f"{b:02X}" for b in frame)
    
    # Aktualizuj statystyki typów
    stats['frame_types'][type_name] = stats['frame_types'].get(type_name, 0) + 1
    
    print(f"[{timestamp}] ADDR:0x{address:02X} TYPE:{type_name:25} LEN:{len(frame):02} | {hex_data}")

def print_statistics():
    """Wypisuje statystyki sesji"""
    print("\n" + "="*80)
    print("STATYSTYKI SESJI")
    print("="*80)
    print(f"Poprawne ramki (CRC OK):  {stats['crc_ok']}")
    print(f"False-sync odrzucone:     {stats['false_sync_dropped']}")
    print(f"Całkowita liczba ramek:   {stats['total_frames']}")
    print("\nRozkład typów ramek:")
    for frame_type, count in sorted(stats['frame_types'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {frame_type:25} : {count:5}")
    print("="*80)

def main():
    # Konfiguracja CLI
    parser = argparse.ArgumentParser(
        description='CRSF Raw Logger z ochroną przed false-sync',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Przykłady użycia:
  %(prog)s                              # Domyślnie /dev/ttyUSB0 @ 420000
  %(prog)s -p /dev/ttyAMA0 -b 400000    # Custom port i baudrate
  %(prog)s -p COM3 -b 416666            # Windows
        """
    )
    parser.add_argument('-p', '--port', default='/dev/ttyUSB0', 
                        help='Port szeregowy (default: /dev/ttyUSB0)')
    parser.add_argument('-b', '--baud', type=int, default=420000, 
                        help='Baudrate (default: 420000)')
    args = parser.parse_args()

    try:
        # Timeout 10ms zapobiega busy-wait
        ser = serial.Serial(args.port, args.baud, timeout=0.01)
        buffer = bytearray()
        
        print("="*80)
        print(f"CRSF Raw Logger - nasłuchiwanie na {args.port} @ {args.baud} baud")
        print("Anti false-sync: włączona (loguje tylko ramki z CRC OK)")
        print("Naciśnij Ctrl+C aby zakończyć")
        print("="*80)

        while True:
            chunk = ser.read(1024)
            if chunk:
                buffer.extend(chunk)

            while len(buffer) >= 4:
                # Szukamy poprawnego adresu CRSF
                if buffer[0] not in CRSF_ADDRESSES:
                    buffer.pop(0)
                    continue

                frame_len = buffer[1]
                
                # Walidacja długości (CRSF max ~64, min 2)
                if frame_len < 2 or frame_len > 64:
                    buffer.pop(0)
                    continue
                
                # Pełna długość pakietu: address + length + frame_len
                full_packet_len = frame_len + 2

                if len(buffer) < full_packet_len:
                    break  # Czekamy na resztę danych

                # Mamy pełną ramkę - sprawdź CRC
                frame = bytes(buffer[:full_packet_len])
                
                # Weryfikacja CRC8
                # CRC liczone od Type (frame[2]) do końca Payload (frame[-2])
                # frame[-1] to sam CRC
                calculated_crc = crc8_dvb_s2(frame[2:-1])
                crc_valid = (calculated_crc == frame[-1])
                
                if crc_valid:
                    # To jest prawdziwa ramka - loguj
                    stats['crc_ok'] += 1
                    stats['total_frames'] += 1
                    log_raw(frame)
                    del buffer[:full_packet_len]
                else:
                    # CRC fail = to jest false-sync (payload collision)
                    # Posuń tylko o 1 bajt i szukaj dalej
                    stats['false_sync_dropped'] += 1
                    buffer.pop(0)

    except KeyboardInterrupt:
        print("\n\nLogowanie przerwane przez użytkownika.")
    except serial.SerialException as e:
        print(f"\n\n✗ Błąd portu szeregowego: {e}")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
        print_statistics()

if __name__ == "__main__":
    main()
