Cel projektu
Zbudować komunikację RPi 5 ↔ ExpressLRS RF link, gdzie:

TX: HappyModel ES24ProTX / ES24TX Pro (TCXO v1) w zatoce JR.

RX: SpeedyBee Nano 2.4G RX (Nano24RX).

RPi ma docelowo:

wysyłać kanały RC do ES24Pro (tak jak robi radio),

odbierać telemetrię/ramki zwrotne (CRSF/ELRS ecosystem).

Kluczowe ustalenia warstwy fizycznej
Komunikacja RPi ↔ ES24Pro w zatoce JR odbywa się po jednym przewodzie danych (pin S.Port) + VCC + GND.

To jest single‑wire half‑duplex (RX/TX na jednym kablu) i sygnał jest odwrócony:

Użytkownik definiuje: idle = fizyczne LOW (~0 V).

Fizyczne HIGH (~3.3–3.6 V) odpowiada stanom „aktywnym” po inwersji (start/bit0 itd.).

Baudrate: 420000 bps.

Poziomy: FrSky ~3.3 V, ES24Pro ma fizyczne HIGH ~3.5 V (max ok. 3.65 V). Żeby bezpiecznie wprowadzić do 74HC04 zasilanego 3.3 V, dodany jest rezystor szeregowy 1k–4k7 przed wejściem inwertera (ograniczenie prądu klamrowania).

Sprzęt do sniffingu
RPi5 + FT232RL (USB-UART) + 74HC04 @3.3 V (inwersja) + rezystor szeregowy.

Na etapie sniffingu: TXD FTDI niepodłączony (podsłuch RX-only) żeby uniknąć kontencji na 1‑wire.

FTDI jako wejście nie obciąża mocno linii (praktycznie „wysokoomowo”), więc podsłuch równoległy z działającym FrSky↔ES24Pro jest OK.

Co już działa (ważny milestone)
Uruchomiono prosty skrypt Python (pySerial) na RPi do odbioru bajtów z /dev/ttyUSB0 przy 420000 8N1.

W logu widać powtarzające się ramki zaczynające się od:

EE 18 16 ... (26 bajtów całej ramki).

Zrobiono weryfikację CRC8 (poly 0xD5) na kilku wyciętych ramkach:

CRC wychodzi poprawne dla ramek 0x16.

Wniosek: tor elektryczny + inwersja + baudrate + sampling działają; RPi poprawnie odbiera strumień „FrSky → ES24Pro”.

Nierozwiązane / problem do dalszej analizy
W danych z oscyloskopu/dekodera pojawiały się odpowiedzi wyglądające jak zaczynające się od EA ..., ale było podejrzenie, że to środek ramki (np. bajty dest/src w extended) albo ucięcie początku (brak SYNC).

W sniffingu RPi w krótkim wycinku dominują ramki 0x16 (RC channels); odpowiedzi/telemetria mogą być rzadsze i nie wpadły w pierwszy krótki print.

Trzeba zrobić solidny logger ramek (dłuższy czas) i znaleźć wszystkie typy ramek (np. 0x32/extended itd.), z CRC i timestampami.

Terminologia (ważne, żeby nie mylić)
Zespół ustalił, że używa się tylko:

Fizyczne LOW/HIGH = poziom napięcia na przewodzie.

Słowo „idle” = fizyczne LOW (użytkownik tak rozumie).

Jeśli mowa o „bitach UART po inwersji”, trzeba to pisać jawnie, żeby nie mieszać pojęć.

Kolejny krok (plan)
Zrobić porządny sniffer, który:

wykrywa ramki po SYNC (0xEE i także 0xC8 jeśli się pojawia),

tnie po LEN,

sprawdza CRC8 poly 0xD5,

zapisuje do CSV: timestamp + SYNC + LEN + TYPE + CRC_OK + pełny hex.

Nagrać 3 sesje:

cold start (od włączenia),

stan ustalony 30–60 s,

praca drążkami/przełącznikami + ewentualne wymuszenie zmian RF.

Dopiero potem przejść do etapu „RPi jako master”:

odpiąć FrSky od linii i zacząć nadawać z RPi ramki 0x16 cyklicznie,

ale to wymaga rozwiązania nadawania na 1‑wire (kontrola kiedy FTDI nadaje i kiedy „puszcza” linię, aby ES24Pro mógł odpowiedzieć).

Status emocjonalno-procesowy
Użytkownik jest bardzo techniczny, ale oczekuje krótkich, jednoznacznych instrukcji i nie toleruje mieszania pojęć.

Priorytet: unikać „chaosu z internetu”, opierać się na danych z pomiarów i CRC.