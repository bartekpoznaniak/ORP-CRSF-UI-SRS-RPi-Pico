import serial
import time

# Na RPi 5 głównym portem na pinach GPIO jest zazwyczaj /dev/ttyAMA0
try:
    ser = serial.Serial('/dev/ttyAMA0', 115200, timeout=1)
    test_string = b'TEST_UART'
    
    ser.write(test_string)
    time.sleep(0.1)
    odpowiedz = ser.read(len(test_string))
    
    if odpowiedz == test_string:
        print("SUKCES: Test pętli zaliczony!")
    else:
        print(f"BLAD: Wyslano {test_string}, ale odebrano: {odpowiedz}")
        
    ser.close()
except Exception as e:
    print(f"Nie udalo sie otworzyc portu: {e}")
