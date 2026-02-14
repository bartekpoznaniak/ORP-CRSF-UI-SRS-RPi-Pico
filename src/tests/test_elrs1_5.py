import serial

# Ustawiamy Twoją podejrzewaną prędkość
port = "/dev/ttyAMA0"
baud = 460800

try:
    ser = serial.Serial(port, baud, timeout=2)
    print(f"Nasłuchuję na {port} ({baud} bps)...")
    
    # Próbujemy odczytać 50 bajtów
    data = ser.read(50)
    
    if data:
        print(f"Odebrano dane (Hex): {data.hex().upper()}")
        # Szukamy bajtu synchronizacji CRSF: 0xC8, 0xEE lub 0xEA
        if any(b in data for b in [0xc8, 0xee, 0xea]):
            print("Zidentyfikowano ramki protokołu CRSF/ELRS!")
        else:
            print("Odebrano dane, ale nie przypominają protokołu CRSF. Może inny baudrate?")
    else:
        print("Brak danych. Moduł nic nie wysyła.")
        
    ser.close()
except Exception as e:
    print(f"Błąd: {e}")
