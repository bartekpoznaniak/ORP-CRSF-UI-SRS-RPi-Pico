import serial
import time

PORT = '/dev/ttyUSB1'
BAUD = 57600

def loopback_test():
    print(f"--- TEST LOOPBACK NA {PORT} ---")
    try:
        ser = serial.Serial(PORT, BAUD, timeout=1)
        test_data = b'\x7E\x98\x00\x11\x22' # Przykładowa ramka S.Port
        
        print(f"Wysyłam: {test_data.hex().upper()}")
        ser.write(test_data)
        
        time.sleep(0.1)
        odpowiedz = ser.read(len(test_data))
        
        if odpowiedz == test_data:
            print("SUKCES: Odebrano dokładnie to samo! Port USB i sterowniki są OK.")
        elif len(odpowiedz) > 0:
            print(f"BŁĄD: Odebrano inne dane: {odpowiedz.hex().upper()}")
            print("Prawdopodobna przyczyna: Zły baudrate lub zakłócenia.")
        else:
            print("BŁĄD: Nic nie odebrano. Sprawdź zworkę między TX i RX.")
            
        ser.close()
    except Exception as e:
        print(f"Nie można otworzyć portu: {e}")

if __name__ == "__main__":
    loopback_test()
