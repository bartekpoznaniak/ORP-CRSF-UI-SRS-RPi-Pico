import serial
import time

port = "/dev/ttyAMA0"
baud = 460800  # Twoja podejrzewana prędkość

try:
    ser = serial.Serial(port, baud, timeout=1)
    # Standardowa ramka CRSF Ping: [Sync, Len, Type, Payload, CRC]
    ping_frame = bytes([0xC8, 0x04, 0x28, 0x00, 0xCF])
    
    print(f"Wysyłam ramkę Ping do ES24TX na {baud} bps...")
    ser.write(ping_frame)
    
    time.sleep(0.5)
    response = ser.read(ser.in_waiting or 100)
    
    if response:
        print(f"MODUŁ ODPOWIEDZIAŁ: {response.hex().upper()}")
    else:
        print("Cisza. Moduł nie zareagował na Ping.")
    
    ser.close()
except Exception as e:
    print(f"Błąd: {e}")
