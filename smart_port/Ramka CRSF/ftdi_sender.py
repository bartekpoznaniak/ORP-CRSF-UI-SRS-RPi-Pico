import serial
import time

PORT = '/dev/ttyUSB0'  # Twój FTDI port (zmień na /dev/ttyACM0 jeśli inny)
BAUD = 420000          # Standard CRSF baud

def crc8_dvb_s2(data):
    """CRC8 dla CRSF (polynomial 0xD5)"""
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

def encode_rc_channels(channels):
    """Encode 16x11bit channels do 22 bajtów payload"""
    packed = bytearray(22)
    bit_index = 0
    for ch in channels:
        ch = max(172, min(1811, ch))  # Clamp do CRSF range
        for j in range(11):
            if ch & (1 << j):
                byte_idx = bit_index // 8
                bit_pos = bit_index % 8
                packed[byte_idx] |= (1 << bit_pos)
            bit_index += 1
    return packed

def build_crsf_frame(frame_type, payload):
    """Buduje kompletną ramkę CRSF: SYNC + LEN + TYPE + PAYLOAD + CRC"""
    frame = bytearray()
    frame.append(0xC8)  # SYNC byte (ELRS standard address)
    frame.append(len(payload) + 2)  # LEN = type + payload + crc
    frame.append(frame_type)
    frame.extend(payload)
    crc = crc8_dvb_s2(frame[2:])  # CRC od TYPE do końca payload
    frame.append(crc)
    return frame

try:
    ser = serial.Serial(PORT, BAUD, timeout=0.01)
    print(f"CRSF Frame Generator - wysyłam na {PORT} @ {BAUD} baud (3.3V check)")
    print("Złap FTDI TX pinem na logic analyzer! CTRL+C aby zatrzymać.\n")
    
    counter = 0
    
    while True:
        # 1. RC Channels frame (0x16) - symuluj drążki w środku + jeden ruchomy
        channels = [992] * 16  # Center (992 = ~1500us w 11bit)
        channels[0] = 172 + (counter % 1640)  # CH1 sweep od min do max
        channels[4] = 1811 if (counter // 100) % 2 == 0 else 172  # CH5 switch toggle
        
        rc_payload = encode_rc_channels(channels)
        rc_frame = build_crsf_frame(0x16, rc_payload)
        ser.write(rc_frame)
        print(f"[{counter:04d}] Wysłano RC_CHANNELS (0x16): {rc_frame.hex()} | CH1={channels[0]} CH5={channels[4]}")
        
        time.sleep(0.010)  # 10ms = 100Hz update rate
        
        # 2. Link Stats frame (0x14) - co 50ms
        if counter % 5 == 0:
            link_payload = bytearray([
                200,  # Uplink RSSI 1 (fake -56dBm)
                50,   # Uplink RSSI 2
                80,   # Uplink Link Quality (80%)
                120,  # Uplink SNR
                5,    # Active Antenna
                0,    # RF Mode (500Hz)
                200,  # Uplink TX Power (fake 25mW)
                150,  # Downlink RSSI
                90,   # Downlink Link Quality
                100   # Downlink SNR
            ])
            link_frame = build_crsf_frame(0x14, link_payload)
            ser.write(link_frame)
            print(f"  -> Wysłano LINK_STATS (0x14): {link_frame.hex()}")
        
        # 3. Battery frame (0x08) - co 100ms
        if counter % 10 == 0:
            voltage = 420  # 4.20V (unit: 0.01V = 420)
            current = 1550  # 15.50A (unit: 0.01A = 1550)
            capacity = 1200  # 1200mAh used
            remaining = 50  # 50% pozostało
            
            battery_payload = bytearray([
                (voltage >> 8) & 0xFF, voltage & 0xFF,
                (current >> 8) & 0xFF, current & 0xFF,
                (capacity >> 16) & 0xFF, (capacity >> 8) & 0xFF, capacity & 0xFF,
                remaining
            ])
            battery_frame = build_crsf_frame(0x08, battery_payload)
            ser.write(battery_frame)
            print(f"  -> Wysłano BATTERY (0x08): {battery_frame.hex()}")
        
        counter += 1
        
        # 4. Co sekundę wyślij burst do testu peak voltage
        if counter % 100 == 0:
            print("\n*** BURST TEST (10 ramek bez delay) ***")
            for _ in range(10):
                burst_channels = [992] * 16
                burst_payload = encode_rc_channels(burst_channels)
                burst_frame = build_crsf_frame(0x16, burst_payload)
                ser.write(burst_frame)
            print("*** Burst zakończony ***\n")

except KeyboardInterrupt:
    print("\nZatrzymano generator.")
finally:
    ser.close()
