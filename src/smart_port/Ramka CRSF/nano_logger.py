import serial
import sys

PORT = '/dev/ttyUSB0'  # Zmień na swój port (np. /dev/ttyACM0 dla Nano)
BAUD = 420000          # 420k standardowo dla CRSF
THRESHOLD = 100

def decode_crsf(payload):
    """Decode 22-byte RC channels payload (16x11bit)"""
    channels = []
    current_byte = 0
    current_bit = 0
    for i in range(16):
        val = 0
        for j in range(11):
            if payload[current_byte] & (1 << current_bit):
                val |= (1 << j)
            current_bit += 1
            if current_bit == 8:
                current_byte += 1
                current_bit = 0
        channels.append(val)
    return channels

try:
    ser = serial.Serial(PORT, BAUD, timeout=0.01)
    ser.reset_input_buffer()
    
    print(f"Logger CRSF - łapie WSZYSTKIE ramki (0xC8/0xEE SYNC). Ruszaj drążkami!")
    
    buffer = bytearray()
    last_channels = [0] * 16

    while True:
        if ser.in_waiting > 0:
            buffer.extend(ser.read(ser.in_waiting))

        # Szukamy SYNC byte (0xC8 standard ELRS, 0xEE EdgeTX TX)
        while len(buffer) >= 4:  # Min frame: SYNC + LEN + TYPE + CRC
            # Sprawdź SYNC byte (0xC8 lub 0xEE)
            if buffer[0] not in [0xC8, 0xEE]:
                buffer.pop(0)
                continue
            
            # LEN = buffer[1] (payload+type+crc, bez SYNC i LEN)
            frame_len = buffer[1]
            full_frame_len = frame_len + 2  # +SYNC +LEN
            
            if len(buffer) < full_frame_len:
                break  # Czekamy na resztę ramki
            
            # Wyciągnij pełną ramkę
            frame = buffer[:full_frame_len]
            frame_type = frame[2]
            payload = frame[3:-1]  # Bez SYNC, LEN, TYPE, CRC
            crc = frame[-1]
            
            # Wydrukuj KAŻDĄ ramkę z typem (hex)
            print(f"FRAME: SYNC={hex(frame[0])} LEN={frame_len} TYPE={hex(frame_type)} PAYLOAD={payload.hex()} CRC={hex(crc)}")
            
            # Decode RC channels jeśli TYPE=0x16
            if frame_type == 0x16 and len(payload) == 22:
                current_channels = decode_crsf(payload)
                changed = any(abs(current_channels[i] - last_channels[i]) > THRESHOLD for i in range(16))
                
                if changed:
                    output = " | ".join([f"CH{i+1}:{val:<4}" for i, val in enumerate(current_channels)])
                    print(f"  -> RC CHANNELS: {output}")
                    last_channels = current_channels[:]
            
            # Inne typy ramek (telemetry)
            elif frame_type == 0x14:
                print(f"  -> LINK_STATS (telemetry)")
            elif frame_type == 0x08:
                print(f"  -> BATTERY (telemetry)")
            elif frame_type in [0x02, 0x1E, 0x21]:
                print(f"  -> GPS/ATTITUDE/FLIGHT_MODE")
            
            # Usuń przetworzoną ramkę
            del buffer[:full_frame_len]

except KeyboardInterrupt:
    print("\nZatrzymano logowanie.")
finally:
    ser.close()
