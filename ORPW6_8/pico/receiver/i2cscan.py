import machine

# Inicjalizacja I2C na pinach GP0 (SDA) i GP1 (SCL)
i2c = machine.I2C(0, sda=machine.Pin(0), scl=machine.Pin(1), freq=400000)

print("Skanowanie magistrali I2C...")
devices = i2c.scan()

if devices:
    for device in devices:
        print(f"Znaleziono urządzenie pod adresem: {hex(device)}")
else:
    print("Nie znaleziono żadnych urządzeń I2C. Sprawdź okablowanie!")
