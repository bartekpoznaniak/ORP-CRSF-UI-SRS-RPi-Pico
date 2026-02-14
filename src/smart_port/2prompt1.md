# ORPW6_8 — RPi5 ↔ ExpressLRS (ES24ProTX ↔ Nano24RX) po CRSF (1‑wire, inverted) — dokument roboczy / handover

## 1) Cel projektu
- Zbudować komunikację **RPi 5 ↔ link RF ExpressLRS**, gdzie:
  - TX (nadajnik RF): HappyModel **ES24ProTX / ES24TX Pro (TCXO v1)**, w zatoce JR (jak w aparaturach typu FrSky).
  - RX (odbiornik RF): SpeedyBee **Nano 2.4G RX** (Nano24RX).
- Docelowe funkcje po stronie RPi:
  1) wysyłanie kanałów RC do ES24Pro (RPi przejmuje rolę „radia”/mastera),
  2) odbiór telemetrii i ramek zwrotnych (CRSF/ELRS ekosystem).

## 2) Ustalenia i założenia techniczne (warstwa fizyczna + pojęcia)
### 2.1 Topologia połączenia (zatoce JR)
- Użytkownik ma dostęp praktycznie tylko do **3 pinów**: VCC, GND, S.Port.
- Komunikacja **RPi ↔ ES24Pro** w zatoce JR odbywa się po **jednym przewodzie danych** (pin S.Port), czyli **single‑wire half‑duplex**: RX i TX na jednym kablu.

### 2.2 Polaryzacja i terminologia (ustalone, żeby nie mieszać)
- Ustalona i wymagana terminologia:
  - **Fizyczne LOW** = ~0 V na przewodzie.
  - **Fizyczne HIGH** = ~3.3–3.6 V na przewodzie.
  - Słowo „idle” w tej dyskusji znaczy: **idle = fizyczne LOW**.
- Linia jest **odwrócona (inverted)**: użytkownik obserwuje idle = fizyczne LOW (~0 V), a start/aktywność to przejście do fizycznego HIGH.

### 2.3 Parametry sygnału
- UART: **420000 bps** (typowe dla CRSF/ExpressLRS).
- Próbkowanie w analizie oscyloskopowej:
  - Rigol DS1202/DS1000, eksport CSV: `Sequence,Volt`,
  - `Increment = 5e-7 s` (0.5 µs/sample, 2 MSa/s),
  - czas bitu ~2.381 µs (~4.76 próbki/bit) — dekodowanie możliwe.

### 2.4 Poziomy napięć (pomiary użytkownika)
- FrSky nadaje „ładnie” do ~3.3 V (fizyczne HIGH).
- ES24Pro w fizycznym HIGH dochodzi typowo do ~3.5 V, maks obserwowany ~3.65 V.
- Wniosek praktyczny: przy logice 3.3 V warto ograniczyć prądy klamrowania na wejściu inwertera rezystorem szeregowym.

## 3) Sprzęt, podłączenie i aktualny tor pomiarowy (sniffer cyfrowy)
### 3.1 Założenie: najpierw podsłuch (RX‑only), bez nadawania z RPi
- Na etapie sniffingu RPi nie steruje linią, tylko **podsłuchuje** równolegle do pracującego układu FrSky ↔ ES24Pro.
- Krytyczne: **TXD FTDI niepodłączony** (żeby nie było kontencji na 1‑wire).

### 3.2 Tor sniffingu (RPi + FTDI + inwersja)
- RPi 5 + **FT232RL** (USB‑UART) + **74HC04** jako inwerter (zasilany z 3.3 V) + **rezystor szeregowy** (typowo 1k–4k7) przed wejściem 74HC04.
- Uzasadnienie rezystora: wejścia 74HC04 nie powinny stale dostawać napięć dużo powyżej VCC; typowe ograniczenie to okolice VCC+0.5 V, więc rezystor ogranicza prąd przez diody zabezpieczające, gdy fizyczne HIGH jest blisko/nieco powyżej 3.3 V. [web:126]
- FT232R jako wejście RX jest „lekkim” obciążeniem (m.in. wewnętrzne podciągnięcie wejść w trybie input rzędu ~200 kΩ do VCCIO), więc w praktyce nadaje się do równoległego podsłuchu. [web:156]

### 3.3 Skrypt RX‑only (python)
- Wdrożony prosty nasłuch na RPi po `/dev/ttyUSB0`, `420000 8N1`.
- Uwaga systemowa: pySerial był brakujący w venv — rozwiązane przez instalację `pyserial` wewnątrz virtualenv (systemowy `python3-serial` nie był widoczny z venv).

## 4) Co już mamy (twarde wyniki z RPi)
### 4.1 Wynik uruchomienia RX‑only
- Skrypt nasłuchu na RPi zwrócił np. `RX bytes: 15036` w 5 sekund oraz powtarzalne sekwencje bajtów:
  - `ee 18 16 e0 c3 5e 2b ...`
- Te ramki są **cykliczne** i wyglądają jak standardowy strumień RC.

### 4.2 Interpretacja wstępna: CRSF „RC_CHANNELS_PACKED”
- Widoczne ramki zaczynają się od `0xEE`, mają `LEN=0x18` i `TYPE=0x16`, czyli odpowiadają formatowi CRSF (SYNC/LEN/TYPE/PAYLOAD/CRC). [web:30]
- `TYPE=0x16` odpowiada ramkom kanałów RC (`RC_CHANNELS_PACKED`) znanym z ekosystemu CRSF. [web:93]

### 4.3 CRC i wiarygodność dekodowania
- Wykonano obliczenie CRC8 (poly 0xD5, jak w CRSF) dla wyciętych ramek i w krótkim wycinku wszystkie wycięte ramki `0x16` miały CRC poprawne. [web:58]
- Wniosek: tor „fizyczny → inwersja → FTDI → RPi → pySerial” działa i daje bajty zgodne z CRSF (na tyle, że CRC się zgadza). [web:30][web:58]

## 5) Nierozwiązane kwestie i plan dalszych kroków
### 5.1 Nierozwiązane / do wyjaśnienia
- W logach z oscyloskopu użytkownik obserwował fragmenty sugerujące odpowiedzi zaczynające się od `EA ...`, ale pojawiła się hipoteza, że to może być:
  - start „w środku” ramki (np. dest/src w extended),
  - ucięcie początku ramki przez dekoder/fragment logu,
  - albo rzadkie ramki zwrotne, które nie trafiły do krótkiego wydruku (pierwsze 300 bajtów).
- Wniosek organizacyjny: zanim przejdziemy do nadawania z RPi, trzeba mieć pełny obraz ramek na linii (w tym ramek innych niż `0x16`). raczej to tylko podejżenie ale warto zweryfikować.

### 5.2 Dlaczego najpierw solidny sniffer (a nie od razu „RPi steruje ES24Pro”)
- Docelowo RPi ma zastąpić FrSky jako master na 1‑wire, ale bez pełnej listy ramek/timingów łatwo debugować jednocześnie:
  - elektrykę 1‑wire,
  - inwersję,
  - framing (SYNC/LEN),
  - CRC,
  - zachowanie modułu ES24Pro (kiedy i na co odpowiada).
- Dlatego proponowany etap pośredni: **logger ramek CRSF do CSV** (timestamp + SYNC + LEN + TYPE + CRC_OK + hex) i dopiero potem emulator mastera.

### 5.3 Plan sniffingu (nagrania)
Zrobić trzy sesje logów:
1) **Cold start**: od włączenia radia/modułu do stabilnej pracy.
2) **Stan ustalony**: 30–60 s bez ruszania kanałami.
3) **Wymuszenie zmian**: 30–60 s z ruchem gimbali/przełączników (opcjonalnie zmiana warunków RF), żeby sprowokować inne ramki (telemetria/komendy).

### 5.4 Następny etap (po sniffingu): „RPi jako master”
- Po pełnym sniffingu i analizie:
  - odpinamy FrSky od S.Port,
  - RPi zaczyna generować ramki `0x16` w cyklu (jak FrSky),
  - równolegle RPi odbiera ramki zwrotne (telemetria/command/extended).
- Krytyczne zagadnienie do rozwiązania przed TX:
  - poprawne „puszczanie” linii w half‑duplex (żeby ES24Pro mógł nadać między ramkami).
