

Cel: Aplikacja graficzna na Raspberry Pi 5 sterująca makietą ORP – joysticki/przełączniki → radio CRSF → gimbaly Pico + telemetry.

Moduły z read.me (do reużycia):
Logowanie/parsowanie: 1.py, newLogger.py (ramki CRSF z CRC8).
Emulacja TX: ftdisender.py, rcmockdyn.py (kanały bez aparatury).
Konfiguracja: confLogger.py (parametry ES24Pro).
Wymagania (z plan.dzialania.md):

Odczyt danych z gimbali (kanaly 1-4, wyświetlaj suwaki).

Opracowanie protokołu przełączników inaczej niż w klasycznym CRSF a ma to działać tak że:
1 bit = jeden przełącznik (bo będzie ich ok 40) czyli apkikacja RPI będzie kodowałała przełaczniki do bitów 0x16 a potem aplikacja dekodująca będzie to rozkładała na poszczególne bity i działanie podsystemów okrętu.

Bedą jeszcze wysyłane komendy uruchamiające sekwencje w skrócie opertatoe płunie statkiem obserwue na kamerze 04pro na goglach dokąd płynie i przyciskiem włącza jedną z zaprogarmowanych sekwencji która będzi Uruchamiać radaey działo nr 1 obrót o 180st CW i wystrzał działo 2 obrót o 110st ccw i wysrzał światła na pokaładzie 2 włącz uruchom syręnę pokładową, wystrzel tropedę nr4  itp idt . takiecch sekwencji będzie kilka akle trzbeaa jakoś rozwiązać sposób ich kodowania.
Chodzi o to że operatoe ma tylko 2 ręce i 10 palców i musi być jakaś autmatyzajcja inaczej jeden człowiek tego nie ogranie. 


​

Tryb graficzny odbiornika (UI z joystickami).
​Telemetria z modelu (wyświetl na ekranie).
​