#!/usr/bin/env python3
"""
CRSF RC Mockowanie - Emuluje aparaturę FrSky
Wysyła ramki RC_CHANNELS_PACKED do modułu ELRS
TX-ONLY mode (nie wymaga bufora half-duplex na start)
"""

import serial
import time
import argparse

def crc8_dvb_s2(data):
    """CRC8 DVB-S2 (poly 0xD5) dla CRSF"""
    crc = 0
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc << 1) ^ 0xD5 if crc & 0x80 else crc << 1
    return crc & 0xFF

def pack_channels(channels):
    """
    Pack 16 kanałów (0-2047) do 22 bajtów CRSF payload
    """
    if len(channels) != 16:
        raise ValueError("Potrzeba 16 kanałów")
    
    payload = bytearray(22)
    current_byte = 0
    current_bit = 0
    
    for ch_val in channels:
        if not (0 <= ch_val <= 2047):
            raise ValueError(f"Kanał {ch_val} poza zakresem 0-2047")
        
        for j in range(11):
            if ch_val & (1 << j):
                payload[current_byte] |= (1 << current_bit)
            current_bit += 1
            if current_bit == 8:
                current_byte += 1
                current_bit = 0
    
    return bytes(payload)

def build_crsf_frame(channels):
    """
    Buduje pełną ramkę CRSF RC_CHANNELS_PACKED
    channels: lista 16 int (0-2047)
    Returns: bytes gotowe do wysłania
    """
    # Address: 0xEE (TX module)
    # Length: 0x18 (24 = type + 22 payload + crc)
    # Type: 0x16 (RC_CHANNELS_PACKED)
    address = 0xEE
    frame_type = 0x16
    
    payload = pack_channels(channels)
    
    # CRC od type do końca payload
    crc_data = bytes([frame_type]) + payload
    crc = crc8_dvb_s2(crc_data)
    
    # Złóż ramkę
    frame = bytes([address, 0x18, frame_type]) + payload + bytes([crc])
    
    return frame

def main():
    parser = argparse.ArgumentParser(
        description='CRSF RC Mockowanie - emuluje aparaturę',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Przykłady:
  %(prog)s                           # Wszystkie kanały center (992)
  %(prog)s --ch1 172                 # CH1 full left, reszta center
  %(prog)s --ch1 1811 --ch3 172      # CH1 full right, CH3 zero throttle
        """
    )
    parser.add_argument('-p', '--port', default='/dev/ttyUSB2',
                        help='Port szeregowy (default: /dev/ttyUSB2)')
    parser.add_argument('-b', '--baud', type=int, default=420000,
                        help='Baudrate (default: 420000)')
    parser.add_argument('-r', '--rate', type=int, default=100,
                        help='Częstotliwość wysyłania Hz (default: 100)')
    
    # Argumenty dla poszczególnych kanałów
    for i in range(1, 17):
        parser.add_argument(f'--ch{i}', type=int, default=992,
                            help=f'Wartość CH{i} (0-2047, default: 992=center)')
    
    args = parser.parse_args()
    
    # Zbierz wartości kanałów
    channels = [getattr(args, f'ch{i}') for i in range(1, 17)]
    
    # Walidacja
    for i, val in enumerate(channels, 1):
        if not (0 <= val <= 2047):
            print(f"✗ Błąd: CH{i}={val} poza zakresem 0-2047")
            return
    
    print("="*80)
    print("CRSF RC Mockowanie - Emulator aparatury")
    print("="*80)
    print(f"Port:        {args.port}")
    print(f"Baudrate:    {args.baud}")
    print(f"Częstotliwość: {args.rate} Hz ({1000/args.rate:.1f} ms)")
    print(f"\nWartości kanałów (CRSF 0-2047):")
    for i, val in enumerate(channels, 1):
        us = 988 + (val / 1.639)
        print(f"  CH{i:2}: {val:4}  (~{us:4.0f} µs)")
    print("="*80)
    print("Wysyłanie ramek... (Ctrl+C aby zatrzymać)")
    print()
    
    try:
        # TX-only: nie czytamy odpowiedzi
        ser = serial.Serial(args.port, args.baud, timeout=None)
        
        frame = build_crsf_frame(channels)
        interval = 1.0 / args.rate
        frame_count = 0
        
        start_time = time.time()
        
        while True:
            ser.write(frame)
            frame_count += 1
            
            # Co sekundę wypisz status
            if frame_count % args.rate == 0:
                elapsed = time.time() - start_time
                actual_rate = frame_count / elapsed
                print(f"[{frame_count:6}] Wysłano {frame_count} ramek | "
                      f"Faktyczna częstotliwość: {actual_rate:.1f} Hz")
            
            time.sleep(interval)
    
    except KeyboardInterrupt:
        print("\n\nZatrzymano wysyłanie.")
        elapsed = time.time() - start_time
        print(f"Wysłano łącznie: {frame_count} ramek w {elapsed:.1f}s")
        print(f"Średnia częstotliwość: {frame_count/elapsed:.1f} Hz")
    except serial.SerialException as e:
        print(f"\n✗ Błąd portu: {e}")
    finally:
        if 'ser' in locals():
            ser.close()

if __name__ == "__main__":
    main()
