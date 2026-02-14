#!/usr/bin/env python3
"""
CRSF Monitor z AutoDeteKCJĄ Portu + ANTY-LOOPBACK Filter
dla RPi + FTDI USB → S.Port/ES24Pro (420k baud)
"""

import serial
import serial.tools.list_ports
import sys
import time

BAUD = 420000

def find_port():
    """Autodetekcja FTDI USB lub dowolny serial port"""
    print("🔍 Szukam portów USB/Serial...")
    
    # Lista wszystkich dostępnych portów
    ports = list(serial.tools.list_ports.comports())
    
    if not ports:
        print("❌ Brak portów USB/Serial!")
        sys.exit(1)
    
    print(f"\n📋 Znaleziono {len(ports)} port(ów):")
    for i, port in enumerate(ports, 1):
        desc = port.description or "Brak opisu"
        vid_pid = f"VID:PID={port.vid:04X}:{port.pid:04X}" if port.vid else "N/A"
        print(f"  {i}. {port.device} - {desc} ({vid_pid})")
    
    # Auto-wybór: pierwszy FTDI lub CH340
    for port in ports:
        if port.vid in [0x0403, 0x1a86]:  # FTDI lub CH340
            print(f"\n✅ Auto-wybrano: {port.device}")
            return port.device
    
    # Fallback: pierwszy dostępny
    print(f"\n⚠️  FTDI nie wykryty, używam: {ports[0].device}")
    return ports[0].device

def decode_channels(payload):
    channels = []
    bit_buf = 0
    bit_count = 0
    for byte in payload:
        bit_buf |= byte << bit_count
        bit_count += 8
        while bit_count >= 11:
            channels.append(bit_buf & 0x07FF)
            bit_buf >>= 11
            bit_count -= 11
    return channels

class CrsfMonitor:
    def __init__(self):
        self.port = find_port()
        try:
            self.ser = serial.Serial(self.port, BAUD, timeout=0.01)
        except serial.SerialException as e:
            print(f"❌ Nie można otworzyć {self.port}: {e}")
            sys.exit(1)
            
        self.buffer = bytearray()
        self.last_tx_time = 0
        self.tx_echo_pattern = None
        print(f"🚀 CRSF Monitor na {self.port} @ {BAUD:,} baud\n")
        
    def filter_echo(self, frame):
        """Filtruje echo ramek"""
        if (time.time() - self.last_tx_time < 0.005 and 
            self.tx_echo_pattern and frame == self.tx_echo_pattern):
            return True
        return False
        
    def update_display(self, channels, frame):
        sys.stdout.write("\033[H\033[J")  # Clear screen
        print("=== CRSF MONITOR (NO LOOPBACK) ===")
        print(f"PORT: {self.port} | BAUD: {BAUD:,}")
        print(f"RAW: {frame.hex().upper()[:80]}")
        print("-" * 50)
        
        # 16 kanałów w 4 kolumnach
        for row in range(0, 16, 4):
            line = ""
            for i in range(4):
                ch = channels[row+i] if row+i < len(channels) else 0
                line += f"CH{row+i+1:2}: {ch:4} | "
            print(line.rstrip(" | "))
        print("-" * 50)
        
    def run(self):
        sys.stdout.write("\033[?25l")  # Ukryj kursor
        sys.stdout.flush()
        
        try:
            while True:
                if self.ser.in_waiting:
                    self.buffer.extend(self.ser.read(self.ser.in_waiting))
                
                # Parsing ramek
                i = 0
                while i < len(self.buffer) - 4:
                    if self.buffer[i] in [0xC8, 0xEE, 0xEA]:
                        frame_len = self.buffer[i+1]
                        full_len = frame_len + 2
                        
                        if i + full_len <= len(self.buffer):
                            frame = bytes(self.buffer[i:i+full_len])
                            f_type = frame[2]
                            
                            if self.filter_echo(frame):
                                pass  # Echo - skip
                            elif f_type == 0x16:
                                channels = decode_channels(frame[3:-1])
                                self.update_display(channels, frame)
                            
                            # Usuń przetworzoną ramkę
                            self.buffer = self.buffer[i+full_len:]
                            i = 0
                            continue
                    i += 1
                
                # Anti-overflow
                if len(self.buffer) > 512:
                    self.buffer = self.buffer[-128:]
                
                time.sleep(0.001)  # 1ms delay
                
        except KeyboardInterrupt:
            print("\n\n🛑 Zatrzymano")
        finally:
            sys.stdout.write("\033[?25h")  # Pokaż kursor
            self.ser.close()

if __name__ == "__main__":
    monitor = CrsfMonitor()
    monitor.run()

