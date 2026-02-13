import serial
import sys

# Konfiguracja
PORT = '/dev/ttyUSB2' # sprawdzić jak alktualnie nazywa się port USB_FTDI tym: 'ls -l /dev/serial/by-id/'

BAUD = 420000

def decode_channels(payload):
    channels = []
    bit_buf = 0
    bit_count = 0
    for byte in payload:
        bit_buf |= byte << bit_count
        bit_count += 8
        while bit_count >= 11:
            channels.append(bit_buf & 0x07FF)
            bit_buf >>= 11
            bit_count -= 11
    return channels

try:
    ser = serial.Serial(PORT, BAUD, timeout=0)
    buffer = bytearray()
    
    # Ukrywamy kursor dla lepszego efektu
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

    while True:
        if ser.in_waiting > 0:
            buffer.extend(ser.read(ser.in_waiting))

        while len(buffer) >= 4:
            if buffer[0] not in [0xC8, 0xEE]:
                buffer.pop(0)
                continue

            frame_len = buffer[1]
            full_len = frame_len + 2

            if len(buffer) < full_len:
                break

            frame = buffer[:full_len]
            f_type = frame[2]
            
            if f_type == 0x16:
                channels = decode_channels(frame[3:-1])
                
                # ANSI: Powrót na górę ekranu (0,0)
                output = "\033[H" 
                output += "=== CRSF MONITOR (STACJONARNY) ===\n"
                output += f"RAW TYPE: 0x{f_type:02X} | LEN: {full_len}\n"
                output += "-" * 40 + "\n"
                
                # Wyświetlamy 16 kanałów w dwóch kolumnach
                for i in range(0, 16, 2):
                    c1, c2 = channels[i], channels[i+1]
                    output += f"CH{i+1:02}: {c1:<5} | CH{i+2:02}: {c2:<5}\n"
                
                output += "-" * 40 + "\n"
                output += f"RAW HEX: {frame.hex().upper()[:60]}...\n"
                
                sys.stdout.write(output)
                sys.stdout.flush()

            del buffer[:full_len]

except KeyboardInterrupt:
    # Przywracamy kursor
    sys.stdout.write("\033[?25h\n")
    print("Zatrzymano.")
finally:
    ser.close()
