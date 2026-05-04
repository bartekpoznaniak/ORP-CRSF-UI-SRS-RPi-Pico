from machine import SPI, Pin
import time

# MCP2515 rejestry
RESET       = 0xC0
READ        = 0x03
WRITE       = 0x02
RTS_TXB0    = 0x81
CANSTAT     = 0x0E
CANCTRL     = 0x0F
CNF1        = 0x2A
CNF2        = 0x29
CNF3        = 0x28
TXB0CTRL    = 0x30
TXB0SIDH    = 0x31
TXB0SIDL    = 0x32
TXB0DLC     = 0x35
TXB0D0      = 0x36
CANINTE     = 0x2B

CAN_500KBPS = 500
MCP_8MHz    = 8
MCP_16MHz   = 16

class MCP2515:
    def __init__(self, spi, cs):
        self.spi = spi
        self.cs  = cs

    def _cs(self, v): self.cs.value(v)

    def _write_reg(self, addr, val):
        self._cs(0)
        self.spi.write(bytes([WRITE, addr, val]))
        self._cs(1)

    def _read_reg(self, addr):
        self._cs(0)
        self.spi.write(bytes([READ, addr]))
        r = self.spi.read(1)
        self._cs(1)
        return r[0]

    def begin(self, speed, clock):
        # Reset
        self._cs(0)
        self.spi.write(bytes([RESET]))
        self._cs(1)
        time.sleep_ms(10)

        # Tryb konfiguracji
        self._write_reg(CANCTRL, 0x80)
        time.sleep_ms(5)

        # Timing dla 500kbps @ 8MHz
        # CNF1=0x00, CNF2=0x90, CNF3=0x02
        if clock == MCP_8MHz and speed == CAN_500KBPS:
            self._write_reg(CNF1, 0x00)
            self._write_reg(CNF2, 0x90)
            self._write_reg(CNF3, 0x02)
        elif clock == MCP_16MHz and speed == CAN_500KBPS:
            self._write_reg(CNF1, 0x00)
            self._write_reg(CNF2, 0xA0)
            self._write_reg(CNF3, 0x02)

        # Wyłącz przerwania
        self._write_reg(CANINTE, 0x00)

        # Tryb normalny
        self._write_reg(CANCTRL, 0x00)
        time.sleep_ms(10)

        s = self._read_reg(CANSTAT)
        return (s & 0xE0) == 0x00  # True = OK

    def sendMsgBuf(self, can_id, ext, length, data):
        # Załaduj bufor TX0
        self._write_reg(TXB0SIDH, (can_id >> 3) & 0xFF)
        self._write_reg(TXB0SIDL, (can_id & 0x07) << 5)
        self._write_reg(TXB0DLC,  length & 0x0F)
        for i in range(length):
            self._write_reg(TXB0D0 + i, data[i])
        # Wyślij
        self._cs(0)
        self.spi.write(bytes([RTS_TXB0]))
        self._cs(1)
