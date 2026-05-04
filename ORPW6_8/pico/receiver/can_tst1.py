from machine import SPI, Pin
from mcp2515 import MCP2515, CAN_500KBPS, MCP_8MHz
import time
spi = SPI(0, baudrate=1_000_000, polarity=0, phase=0, sck=Pin(18), mosi=Pin(19), miso=Pin(16))
cs = Pin(17, Pin.OUT)
cs.value(1)
can = MCP2515(spi, cs)
can.begin(CAN_500KBPS, MCP_8MHz)
can.sendMsgBuf(0x100, 0, 8, bytearray([0xF1,0x12,0xE0,0,0,0,0,0]))
print('Wyslano!')
