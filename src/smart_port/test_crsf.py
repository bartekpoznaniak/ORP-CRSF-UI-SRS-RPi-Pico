#!/usr/bin/env python3
import serial
import time
import struct

# Konfiguracja FTDI
ser = serial.Serial('/dev/ttyUSB0', 420000, timeout=0.1)

# ===== STAŁE CRSF =====
CRSF_SYNC_BYTE = 0xC8
CRSF_ADDRESS_FLIGHT_CONTROLLER = 0xC8  # Receiver wysyła do FC
CRSF_FRAMETYPE_RC_CHANNELS_PACKED = 0x16

CRSF_CHANNEL_VALUE_MIN = 172   # ~988us
CRSF_CHANNEL_VALUE_MID = 992   # ~1500us
CRSF_CHANNEL_VALUE_MAX = 1811  # ~2012us

def crc8_dvb_s2(data):
    """CRC-8 dla CRSF (DVB-S2 polynomial)"""
    crc = 0
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x80:
                crc = (crc << 1) ^ 0xD5
            else:
                crc = crc << 1
            crc &= 0xFF
    return crc

def pack_channels_11bit(channels):
    """
    Pakuje 16 kanałów (11-bit każdy) do 22 bajtów
    channels: lista 16 wartości (172-1811)
    """
    if len(channels) != 16:
        raise ValueError("Wymagane 16 kanałów!")
    
    # Ograniczenie wartości
    channels = [max(CRSF_CHANNEL_VALUE_MIN, min(CRSF_CHANNEL_VALUE_MAX, ch)) 
                for ch in channels]
    
    packed = bytearray(22)
    bit_offset = 0
    
    for ch in channels:
        # Zapisz 11 bitów kanału
        byte_offset = bit_offset // 8
        bit_in_byte = bit_offset % 8
        
        # Pierwsza część (może być split przez granicę bajtu)
        packed[byte_offset] |= ((ch << bit_in_byte) & 0xFF)
        
        # Jeśli przekracza granicę bajtu
        if bit_in_byte + 11 > 8:
            packed[byte_offset + 1] |= ((ch >> (8 - bit_in_byte)) & 0xFF)
        
        # Jeśli przekracza drugą granicę
        if bit_in_byte + 11 > 16:
            packed[byte_offset + 2] |= ((ch >> (16 - bit_in_byte)) & 0xFF)
        
        bit_offset += 11
    
    return packed

def build_rc_packet(channels):
    """
    Buduje pełną ramkę CRSF RC Channels
    """
    # Pakuj kanały
    payload = pack_channels_11bit(channels)
    
    # Buduj ramkę
    frame = bytearray()
    frame.append(CRSF_SYNC_BYTE)                      # 0xC8
    frame.append(CRSF_ADDRESS_FLIGHT_CONTROLLER)      # 0xC8
    frame.append(24)                                  # Length: 1(type) + 22(payload) + 1(crc)
    frame.append(CRSF_FRAMETYPE_RC_CHANNELS_PACKED)   # 0x16
    frame.extend(payload)                             # 22 bytes
    
    # CRC od address do końca payload (nie licząc sync byte!)
    crc = crc8_dvb_s2(frame[1:])
    frame.append(crc)
    
    return frame

def test_simple_ping():
    """Test prostego pingu do modułu"""
    # Ping: Sync + Address + Length + Type + Dest + Src + CRC
    packet = bytearray([
        0xC8,  # Sync
        0xEE,  # Dest: CRSF Transmitter
        0x04,  # Length (4 bytes: type + 2 addrs + crc)
        0x28,  # Type: DEVICE_PING
        0xEE,  # Destination address
        0xEA,  # Source address (radio)
    ])
    crc = crc8_dvb_s2(packet[1:])
    packet.append(crc)
    
    print(f"Wysyłam PING: {' '.join([f'{b:02X}' for b in packet])}")
    ser.write(packet)
    ser.flush()
    
    time.sleep(0.1)
    
    if ser.in_waiting > 0:
        response = ser.read(ser.in_waiting)
        print(f"ODPOWIEDŹ: {' '.join([f'{b:02X}' for b in response])}")
        return True
    else:
        print("Brak odpowiedzi na PING")
        return False

def send_rc_channels():
    """Wysyła kanały RC"""
    # Testowe kanały - środek na wszystkich
    channels = [CRSF_CHANNEL_VALUE_MID] * 16
    channels[2] = CRSF_CHANNEL_VALUE_MIN  # Throttle na zero
    
    packet = build_rc_packet(channels)
    
    print(f"Wysyłam RC: {' '.join([f'{b:02X}' for b in packet])}")
    print(f"Długość: {len(packet)} bajtów")
    
    ser.write(packet)
    ser.flush()

def main():
    print("=== Test komunikacji CRSF z ES24Pro ===")
    print(f"Port: {ser.port}")
    print(f"Baudrate: {ser.baudrate}")
    print()
    
    try:
        # Test 1: Ping
        print("Test 1: Wysyłam PING...")
        if test_simple_ping():
            print("✅ Moduł odpowiedział!")
        else:
            print("⚠️ Brak odpowiedzi, ale to normalne dla TX module")
        
        print()
        
        # Test 2: Kanały RC
        print("Test 2: Wysyłam RC Channels...")
        for i in range(5):
            send_rc_channels()
            time.sleep(0.02)  # 50Hz
            print(f"  Wysłano pakiet {i+1}/5")
        
        print()
        print("✅ Test zakończony!")
        print()
        print("WAŻNE:")
        print("- ES24Pro TX może NIE odpowiadać na UART (to normalne)")
        print("- Moduł powinien WYSYŁAĆ `RF gdy dostaje RC packets")
        print("- Sprawdź LED na module - czy mruga?")
        print("- Podłącz receiver i sprawdź czy dostaje sygnał")
        
    except KeyboardInterrupt:
        print("\nPrzerwano przez użytkownika")
    finally:
        ser.close()

if __name__ == '__main__':
    main()