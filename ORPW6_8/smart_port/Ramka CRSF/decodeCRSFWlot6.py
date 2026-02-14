import serial
import sys

PORT = '/dev/ttyUSB2'
BAUD = 420000
THRESHOLD = 100  # Próg zmiany (ok. 10% zakresu), aby uniknąć szumu

def decode_crsf(payload):
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
    
    print(f"Logowanie zmian (> {THRESHOLD} jednostek). Ruszaj switchami!")
    
    buffer = bytearray()
    last_channels = [0] * 16  # Tu przechowujemy poprzedni stan

    while True:
        if ser.in_waiting > 0:
            buffer.extend(ser.read(ser.in_waiting))

        while len(buffer) >= 26:
            if buffer[0] == 0xEE and buffer[2] == 0x16:
                payload = buffer[3:25]
                current_channels = decode_crsf(payload)
                
                # Sprawdzamy, czy którykolwiek kanał zmienił się znacząco
                changed = False
                for i in range(16):
                    if abs(current_channels[i] - last_channels[i]) > THRESHOLD:
                        changed = True
                        break
                
                if changed:
                    # Jeśli wykryto zmianę, drukujemy wszystkie kanały w nowej linii
                    output = " | ".join([f"CH{i+1}:{val:<4}" for i, val in enumerate(current_channels)])
                    print(f"ZMIANA: {output}")
                    last_channels = current_channels[:] # Aktualizujemy stan wzorcowy
                
                del buffer[:26]
            else:
                buffer.pop(0)

except KeyboardInterrupt:
    print("\nZatrzymano logowanie.")
finally:
    ser.close()
