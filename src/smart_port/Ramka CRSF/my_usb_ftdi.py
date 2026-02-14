import serial.tools.list_ports

def znajdz_moje_ftdi(target_serial="A9AP82Z0"):
    ports = serial.tools.list_ports.comports()
    for port in ports:
        # Sprawdzamy numer seryjny urządzenia
        if port.serial_number == target_serial:
            print(f"Znaleziono urządzenie na porcie: {port.device}")
            return port.device
    
    print("Nie znaleziono urządzenia o podanym numerze seryjnym.")
    return None

# Użycie w kodzie:
moj_port = znajdz_moje_ftdi()

if moj_port:
    # Tutaj otwierasz połączenie używając wykrytej ścieżki
    ser = serial.Serial(moj_port, 115200)
    print(f"Połączono z {moj_port}")
