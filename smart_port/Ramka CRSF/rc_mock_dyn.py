#!/usr/bin/env python3
"""
CRSF RC Mockowanie - Dynamic Edition
Generuje płynne ruchy drążków (sinus, piła, prostokąt)
Idealne do testowania odbiorników/FC bez aparatury
"""

import serial
import time
import argparse
import math

def crc8_dvb_s2(data):
    """CRC8 DVB-S2 (poly 0xD5) dla CRSF"""
    crc = 0
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc << 1) ^ 0xD5 if crc & 0x80 else crc << 1
    return crc & 0xFF

def pack_channels(channels):
    """Pack 16 kanałów (0-2047) do 22 bajtów CRSF payload"""
    if len(channels) != 16:
        raise ValueError("Potrzeba 16 kanałów")
    
    payload = bytearray(22)
    current_byte = 0
    current_bit = 0
    
    for ch_val in channels:
        val = max(0, min(2047, int(ch_val)))  # Clamp do zakresu
        
        for j in range(11):
            if val & (1 << j):
                payload[current_byte] |= (1 << current_bit)
            current_bit += 1
            if current_bit == 8:
                current_byte += 1
                current_bit = 0
    
    return bytes(payload)

def build_crsf_frame(channels):
    """Buduje pełną ramkę CRSF RC_CHANNELS_PACKED"""
    address = 0xEE
    frame_type = 0x16
    
    payload = pack_channels(channels)
    crc_data = bytes([frame_type]) + payload
    crc = crc8_dvb_s2(crc_data)
    
    frame = bytes([address, 0x18, frame_type]) + payload + bytes([crc])
    return frame

class ChannelAnimator:
    """Generuje dynamiczne wartości dla kanałów"""
    
    def __init__(self, wave_type='sine', period=3.0, min_val=172, max_val=1811, offset=992):
        """
        wave_type: 'sine', 'triangle', 'square', 'sawtooth'
        period: czas pełnego cyklu w sekundach
        min_val, max_val: zakres CRSF (0-2047)
        offset: wartość środkowa (default 992 = center)
        """
        self.wave_type = wave_type
        self.period = period
        self.min_val = min_val
        self.max_val = max_val
        self.offset = offset
        self.amplitude = (max_val - min_val) / 2
        self.start_time = time.time()
    
    def get_value(self):
        """Zwraca aktualną wartość na podstawie czasu"""
        elapsed = time.time() - self.start_time
        phase = (elapsed % self.period) / self.period  # 0.0 - 1.0
        
        if self.wave_type == 'sine':
            # Sinus: -1 do +1
            wave = math.sin(phase * 2 * math.pi)
        
        elif self.wave_type == 'triangle':
            # Trójkąt: liniowy ruch tam-i-z-powrotem
            if phase < 0.5:
                wave = (phase * 4) - 1  # 0→0.5 => -1→+1
            else:
                wave = 3 - (phase * 4)  # 0.5→1 => +1→-1
        
        elif self.wave_type == 'square':
            # Prostokąt: skok min-max
            wave = 1 if phase < 0.5 else -1
        
        elif self.wave_type == 'sawtooth':
            # Piła: liniowy wzrost, skok w dół
            wave = (phase * 2) - 1  # 0→1 => -1→+1
        
        else:
            wave = 0
        
        # Skaluj do zakresu CRSF
        value = self.offset + (wave * self.amplitude)
        return max(self.min_val, min(self.max_val, int(value)))

def main():
    parser = argparse.ArgumentParser(
        description='CRSF RC Mockowanie - Dynamiczne wartości',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Przykłady:
  # Sinus na CH1 (aileron), 3 sek pełny cykl
  %(prog)s --ch1 sine --period 3
  
  # Szybki ruch trójkątny na CH1, CH2 statyczny center
  %(prog)s --ch1 triangle --period 1.5
  
  # Kilka kanałów naraz
  %(prog)s --ch1 sine --ch2 triangle --ch3 sawtooth --period 2
  
  # Wolny sinus z custom zakresem
  %(prog)s --ch1 sine --period 5 --min 500 --max 1500
        """
    )
    parser.add_argument('-p', '--port', default='/dev/ttyUSB2',
                        help='Port szeregowy (default: /dev/ttyUSB2)')
    parser.add_argument('-b', '--baud', type=int, default=420000,
                        help='Baudrate (default: 420000)')
    parser.add_argument('-r', '--rate', type=int, default=100,
                        help='Częstotliwość wysyłania Hz (default: 100)')
    
    parser.add_argument('--period', type=float, default=3.0,
                        help='Czas pełnego cyklu w sekundach (default: 3.0)')
    parser.add_argument('--min', type=int, default=172, dest='min_val',
                        help='Minimalna wartość CRSF (default: 172 = ~1000µs)')
    parser.add_argument('--max', type=int, default=1811, dest='max_val',
                        help='Maksymalna wartość CRSF (default: 1811 = ~2000µs)')
    
    # Typ animacji dla każdego kanału (lub 'static')
    wave_choices = ['static', 'sine', 'triangle', 'square', 'sawtooth']
    for i in range(1, 17):
        parser.add_argument(f'--ch{i}', choices=wave_choices, default='static',
                            help=f'CH{i} typ animacji (default: static=992)')
    
    args = parser.parse_args()
    
    # Stwórz animatory dla każdego kanału
    animators = []
    for i in range(1, 17):
        wave_type = getattr(args, f'ch{i}')
        if wave_type == 'static':
            animators.append(None)  # Będzie 992 (center)
        else:
            animator = ChannelAnimator(
                wave_type=wave_type,
                period=args.period,
                min_val=args.min_val,
                max_val=args.max_val,
                offset=992
            )
            animators.append(animator)
    
    # Sprawdź czy jest jakakolwiek animacja
    if all(a is None for a in animators):
        print("⚠️  Nie wybrano żadnej animacji. Użyj np. --ch1 sine")
        print("    Uruchom z --help aby zobaczyć przykłady.")
        return
    
    print("="*80)
    print("CRSF RC Mockowanie - DYNAMIC MODE 🌊")
    print("="*80)
    print(f"Port:        {args.port}")
    print(f"Baudrate:    {args.baud}")
    print(f"Częstotliwość: {args.rate} Hz")
    print(f"Okres cyklu: {args.period} sek")
    print(f"Zakres:      {args.min_val}-{args.max_val} ({988 + args.min_val/1.639:.0f}-{988 + args.max_val/1.639:.0f} µs)")
    print(f"\nAnimacje kanałów:")
    for i, anim in enumerate(animators, 1):
        if anim:
            print(f"  CH{i:2}: {anim.wave_type:10} (dynamiczny)")
        else:
            print(f"  CH{i:2}: static      (992 = center)")
    print("="*80)
    print("Wysyłanie ramek... (Ctrl+C aby zatrzymać)")
    print("Obserwuj RF sniffer - zobaczysz płynny ruch! 🎬")
    print()
    
    try:
        ser = serial.Serial(args.port, args.baud, timeout=None)
        
        interval = 1.0 / args.rate
        frame_count = 0
        last_print = time.time()
        
        while True:
            # Generuj wartości dla każdego kanału
            channels = []
            for anim in animators:
                if anim:
                    channels.append(anim.get_value())
                else:
                    channels.append(992)  # Static center
            
            # Wyślij ramkę
            frame = build_crsf_frame(channels)
            ser.write(frame)
            frame_count += 1
            
            # Co 1 sekundę wypisz aktualny stan
            now = time.time()
            if now - last_print >= 1.0:
                # Pokaż tylko animowane kanały
                status = []
                for i, (anim, val) in enumerate(zip(animators, channels), 1):
                    if anim:
                        us = 988 + (val / 1.639)
                        status.append(f"CH{i}:{val:4}({us:4.0f}µs)")
                
                print(f"[{frame_count:6}] {' | '.join(status)}")
                last_print = now
            
            time.sleep(interval)
    
    except KeyboardInterrupt:
        print("\n\nZatrzymano wysyłanie.")
        print(f"Wysłano łącznie: {frame_count} ramek")
    except serial.SerialException as e:
        print(f"\n✗ Błąd portu: {e}")
    finally:
        if 'ser' in locals():
            ser.close()

if __name__ == "__main__":
    main()
