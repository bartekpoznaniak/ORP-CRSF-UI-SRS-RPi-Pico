import serial
import time

# KONFIGURACJA
# S.Port standardowo pracuje na 57600 bps
PORT = '/dev/ttyAMA0'
BAUD = 57600

def calculate_checksum(data):
    """Oblicza sumę kontrolną dla S.Port (0xFF - suma bajtów)"""
    total = sum(data)
    checksum = 0xFF - ((total & 0xFF) + (total >> 8))
    return checksum & 0xFF

def send_sport_poll(ser, physical_id):
    """
    Wysyła ramkę pollingu (pytania). 
    W S.Port ramka to: 0x7E (Start) oraz Physical ID.
    """
    # Fizyczne ID w S.Port są modyfikowane przed wysyłką (np. ID 1 to 0x17)
    # Dla testu wyślemy standardowy bajt startu i ID sensora (0x98 to popularny ID)
    frame = bytearray([0x7E, physical_id])
    
    print(f"--- Wysyłanie ramki S.Port (Hex): {frame.hex().upper()} ---")
    ser.write(frame)
    ser.flush() # Wymuszenie wypchnięcia danych z bufora

def run_test():
    try:
        # Inicjalizacja portu
        # timeout jest kluczowy, aby program nie zawisł przy braku odpowiedzi
        ser = serial.Serial(PORT, BAUD, timeout=0.5)
        print(f"Otwarto port {PORT} przy {BAUD} bps.")
        print("Hardware powinien teraz odwrócić sygnał i połączyć TX/RX.")
        print("Jeśli masz oscyloskop, szukaj paczek 0x7E na linii S.Port.\n")

        sensor_id = 0x98 # Przykładowy ID (Vario/Alt)
        
        while True:
            # 1. Wysyłanie
            send_sport_poll(ser, sensor_id)
            
            # 2. Nasłuch na odpowiedź
            # Jeśli Twój konwerter hardware'owy ma funkcję 'echo' (widzisz to co wysłałeś),
            # to ser.read() odbierze najpierw Twoje własne dane.
            response = ser.read(10) # Próba odczytu odpowiedzi
            
            if response:
                print(f"Odebrano (Hex): {response.hex().upper()}")
                if response[0] == 0x7E:
                    print("Status: Wykryto bajt START (0x7E) - Hardware działa!")
            else:
                print("Status: Brak odpowiedzi (Cisza na linii).")
            
            print("-" * 40)
            time.sleep(1) # Odstęp między testami

    except serial.SerialException as e:
        print(f"Błąd portu szeregowego: {e}")
    except KeyboardInterrupt:
        print("\nTest przerwany przez użytkownika.")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Port zamknięty.")

if __name__ == "__main__":
    run_test()
