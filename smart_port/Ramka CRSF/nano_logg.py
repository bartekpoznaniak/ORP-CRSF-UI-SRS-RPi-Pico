import serial
import sys
import argparse

# === ARGUMENTY CLI ===
parser = argparse.ArgumentParser(description='CRSF Logger - łap ramki z RX')
parser.add_argument('-c', '--channels', action='store_true', 
                    help='Tylko RC channels (0x16)')
parser.add_argument('-r', '--rest', action='store_true',
                    help='Tylko telemetry/reszta (bez 0x16)')
parser.add_argument('-p', '--port', type=str, default='/dev/ttyUSB0',
                    help='Port serial (default: /dev/ttyUSB0)')
parser.add_argument('-b', '--baud', type=int, default=420000,
                    help='Baudrate (default: 420000)')
parser.add_argument('-t', '--threshold', type=int, default=100,
                    help='Próg zmiany kanałów (default: 100)')

args = parser.parse_args()

PORT = args.port
BAUD = args.baud
THRESHOLD = args.threshold

# Logika filtrów
if args.channels and args.rest:
    print("BŁĄD: Nie możesz użyć -c i -r jednocześnie!")
    sys.exit(1)

FILTER_MODE = 'all'  # Default: wszystko
if args.channels:
    FILTER_MODE = 'channels_only'
elif args.rest:
    FILTER_MODE = 'no_channels'


def decode_crsf(payload):
    """Decode 16x11bit RC channels z 22-byte payload"""
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
    
    mode_text = {
        'all': 'WSZYSTKIE ramki',
        'channels_only': 'TYLKO RC channels (-c)',
        'no_channels': 'TYLKO telemetry/reszta (-r)'
    }
    print(f"CRSF Logger @ {PORT} {BAUD}bps | Tryb: {mode_text[FILTER_MODE]}")
    print("CTRL+C aby zatrzymać\n")
    
    buffer = bytearray()
    last_channels = [0] * 16

    while True:
        if ser.in_waiting > 0:
            buffer.extend(ser.read(ser.in_waiting))

        while len(buffer) >= 4:
            # SYNC byte check
            if buffer[0] not in [0xC8, 0xEE]:
                buffer.pop(0)
                continue
            
            frame_len = buffer[1]
            full_frame_len = frame_len + 2
            
            if len(buffer) < full_frame_len:
                break
            
            frame = buffer[:full_frame_len]
            frame_type = frame[2]
            payload = frame[3:-1]
            crc = frame[-1]
            
            # === FILTRY ===
            is_rc_frame = (frame_type == 0x16 and len(payload) == 22)
            
            # Skip based on filter mode
            if FILTER_MODE == 'channels_only' and not is_rc_frame:
                del buffer[:full_frame_len]
                continue
            
            if FILTER_MODE == 'no_channels' and is_rc_frame:
                del buffer[:full_frame_len]
                continue
            
            # === DECODE & PRINT ===
            
            # RC Channels (0x16)
            if is_rc_frame:
                current_channels = decode_crsf(payload)
                changed = any(abs(current_channels[i] - last_channels[i]) > THRESHOLD 
                             for i in range(16))
                
                if changed or FILTER_MODE == 'channels_only':
                    output = " | ".join([f"CH{i+1}:{val:<4}" 
                                        for i, val in enumerate(current_channels)])
                    print(f"RC_CHANNELS: {output}")
                    last_channels = current_channels[:]
            
            # Telemetry & inne (tylko w 'all' lub 'no_channels')
            else:
                frame_names = {
                    0x14: "LINK_STATS",
                    0x08: "BATTERY",
                    0x02: "GPS",
                    0x1E: "ATTITUDE",
                    0x21: "FLIGHT_MODE"
                }
                name = frame_names.get(frame_type, f"UNKNOWN_0x{frame_type:02X}")
                
                # W trybie 'all' pokaż hex, w 'no_channels' tylko label
                if FILTER_MODE == 'all':
                    print(f"FRAME: TYPE={name} PAYLOAD={payload.hex()} CRC=0x{crc:02X}")
                else:
                    print(f"{name}")
            
            del buffer[:full_frame_len]

except KeyboardInterrupt:
    print("\nZatrzymano logger.")
except serial.SerialException as e:
    print(f"BŁĄD serial: {e}")
    print(f"Sprawdź port: ls /dev/tty*")
finally:
    try:
        ser.close()
    except:
        pass
