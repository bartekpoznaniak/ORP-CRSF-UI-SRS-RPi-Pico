import serial
import time

# Konfiguracja portu - dla RPi 5 to zazwyczaj /dev/ttyAMA0
# Jeśli używasz innego UART, zmień nazwę portu
PORT = '/dev/ttyAMA0'
BAUD = 420000  # Standard dla ELRS/CRSF

def test_elrs_connection():
    try:
        print(f"--- Inicjalizacja połączenia na {PORT} ({BAUD} baud) ---")
        ser = serial.Serial(PORT, BAUD, timeout=1)
        
        print("Czekam na dane z ES24TX Pro... (upewnij się, że [ ] UART inverted jest wyłączone)")
        
        start_time = time.time()
        byte_count = 0
        
        while time.time() - start_time < 10:  # Testuj przez 10 sekund
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting)
                byte_count += len(data)
                # Wyświetl hex pierwszych 10 bajtów dla weryfikacji
                print(f"Odebrano {len(data)} bajtów. Hex: {data[:10].hex().upper()}")
            
            time.sleep(0.1)

        if byte_count > 0:
            print(f"\n--- SUKCES! Odebrano łącznie {byte_count} bajtów. ---")
            print("Komunikacja fizyczna RPi <-> TX działa poprawnie.")
        else:
            print("\n--- BŁĄD: Nie odebrano żadnych danych. ---")
            print("Sprawdź: 1. Połączenie kablowe (TX do RX, RX do TX). 2. DIP-switches. 3. Czy UART jest włączony w raspi-config.")

        ser.close()

    except Exception as e:
        print(f"Błąd portu: {e}")

if __name__ == "__main__":
    test_elrs_connection()
