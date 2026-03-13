

Cel: Graficzna aplikacja na Raspberry Pi 5 sterująca makietą okrętu ORP: joysticki i przełączniki → pakowanie do ramek radiowych CRSF → gimbaly na Pico + wyświetlanie telemetry z modelu.

Moduły do reużycia (z read.me):

Logowanie/parsowanie ramek CRSF (z weryfikacją CRC8): 1.py, newLogger.py.
Emulacja nadajnika TX (kanały bez fizycznej aparatury): ftdisender.py, rcmockdyn.py.
Konfiguracja modułu ES24Pro: confLogger.py.


Wymagania funkcjonalne:

REQ-1: Odczyt danych z gimbali (kanały 1-4), wyświetlaj suwaki w grafice, odświeżanie 50 Hz.

REQ-2: Kodowanie 40 przełączników jako bity w ramkach CRSF 0x16 (pakowanie/dekodowanie na Pico).

REQ-3: Sekwencje automatyki (5-10 szt.): przycisk w UI triggeruje np. "Działo nr1: obrót 180° w prawo (CW – zgodnie z zegarem) + wystrzał" (kanały 10-12 na 1s); operator obserwuje kamerę O4Pro na goglach.

REQ-4: Graficzny interfejs odbiornika (UI z wirtualnymi joystickami i przyciskami).

REQ-5: Wyświetlanie telemetry z modelu (np. prędkość, pozycja) na ekranie.

REQ-6  Gimbal Hall "Hala Fuj" (chińskie joysticki)

| Kolor   | Pin Pico | Funkcja          |
|---------|----------|--------------    |
| Czarny  | 3V3      | +3.3V [web:24]   |
| Czerwony| GND      | Masa [web:24]    |
| Żółty   | GP26/ADC | Sygnał X [web:26]|

Wymagania jakościowe:

Opóźnienie od joysticka do efektora <10 ms.
Obsługa błędów: automatyczna retransmisja przy błędzie CRC8.
Zużycie CPU Raspberry Pi 5 <50%, kompatybilne z ekranem 7".

Testy:
REQ-2: Symuluj 40 bitów, sprawdź CRC na snifferze RF.
REQ-3: Uruchom sekwencję, zweryfikuj logi z Pico.
