import serial
import time

# Używamy sudo przy uruchamianiu, aby mieć pełną kontrolę nad portem
# ser = serial.Serial('/dev/ttyUSB0', 420000, timeout=0.1)
# ser = serial.Serial('/dev/ttyAMA0', 420000, timeout=0.1)
ser = serial.Serial('/dev/ttyUSB0', 420000, timeout=0.1)


# ser = serial.Serial('/dev/ttyAMA0', 420000, timeout=0.1)
# Ramka CRSF: Sync(EE) Len(04) Type(28 - Ping) Payload(EE EA) CRC(1C)
channels_frame = b'\xee\x04\x28\xee\xea\x1c'


# ser = serial.Serial('/dev/ttyAMA0', 115200, timeout=0.1)
# Ramka kanałów CRSF
# channels_frame = b'\xee\x18\x16\x00\x04\x20\x00\x01\x08\x40\x00\x02\x10\x80\x00\x04\x20\x00\x01\x08\x40\x00\x02\x10\x80\x0a'
# channels_frame = b'\xee\x04\x2f\x02\x01\x1a'
print("Wysyłam dane przez USB... (Naciśnij Ctrl+C aby przerwać)")

try:
    while True:
        ser.reset_output_buffer() # Czyścimy stare dane
        ser.write(channels_frame)
        ser.flush() # Wymuszamy natychmiastowe wysłanie przez mostek USB
        
        time.sleep(0.02) # Standardowe 50Hz
        
        if ser.in_waiting > 0:
            data = ser.read(ser.in_waiting)
            print(f"TELEMETRIA: {data.hex()}")
except KeyboardInterrupt:
    ser.close()

