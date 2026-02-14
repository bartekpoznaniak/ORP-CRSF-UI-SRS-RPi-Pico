import os
import platform
import time

def get_rpi_info():
    # Pobieranie temperatury procesora (specyficzne dla Raspberry Pi)
    temp_raw = os.popen("vcgencmd measure_temp").readline()
    temp = temp_raw.replace("temp=", "").replace("'C\n", "")
    
    print(f"--- Raport z Raspberry Pi 5 ---")
    print(f"System: {platform.system()} {platform.release()}")
    print(f"Architektura: {platform.machine()}")
    print(f"Temperatura CPU: {temp}°C")
    print(f"-------------------------------")

if __name__ == "__main__":
    while True:
        get_rpi_info()
        print("Wciśnij Ctrl+C, aby zatrzymać...")
        time.sleep(2)
