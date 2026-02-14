import serial
import time

# KONFIGURACJA
PORT = '/dev/ttyUSB0'
BAUD = 57600  # Standard Smart.Port

def calculate_sport_checksum(data):
    """Oblicza sumę kontrolną FrSky: 0xFF - suma bajtów (z przeniesieniem)"""
    total = sum(data)
    # Dodaj przeniesienie (carry), jeśli suma > 0xFF
    while total > 0xFF:
        total = (total & 0xFF) + (total >> 8)
    return (0xFF - total) & 0xFF

def send_test_frame(ser, sensor_id=0x98):
    """
    Wysyła ramkę pollingu S.Port.
    Struktura: [START_BYTE, PHYSICAL_ID]
    Dla sensorów FrSky, ID fizyczne jest często mapowane:
    np. ID 0x1B to sensor 27.
    """
    start_byte = 0x7E
    # Przykładowa ramka: 0x7E + ID fizyczne
    frame = bytearray([start_byte, sensor_id])
    
    print(f"--> Wysyłanie na S.Port: {frame.hex().upper()}")
    ser.write(frame)
    ser.flush()

def run_hardware_test():
    print(f"=== Uruchamianie testu hardware na {PORT} ===")
    try:
        # Inicjalizacja z krótkim timeoutem, by nie blokować pętli
        ser = serial.Serial(PORT, BAUD, timeout=0.1)
        
        while True:
            # 1. Wyślij zapytanie (Poll)
            send_test_frame(ser)
            
            # 2. Czekaj chwilę na reakcję hardware'u
            # Jeśli Twój konwerter łączy TX i RX (Half-Duplex), 
            # powinieneś zobaczyć ECHO swoich własnych danych.
            time.sleep(0.05) 
            
            incoming = ser.read(ser.in_waiting or 1)
            
            if incoming:
                print(f"<-- Odebrano (Hex): {incoming.hex().upper()}")
                if incoming[0] == 0x7E:
                    print("Status: OK - Wykryto bajt startu S.Port.")
                else:
                    print("Status: Dane odebrane, ale format nieznany (sprawdź inwersję).")
            else:
                print("Status: Cisza (brak echo / brak odpowiedzi).")
                
            print("-" * 30)
            time.sleep(0.9) # Powtarzaj co sekundę

    except serial.SerialException as e:
        print(f"Błąd portu: {e}")
    except KeyboardInterrupt:
        print("\nTest przerwany.")
    finally:
        if 'ser' in locals():
            ser.close()

if __name__ == "__main__":
    run_hardware_test()
