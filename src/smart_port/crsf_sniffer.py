 #!/usr/bin/env python3
import argparse, csv, time
import serial

SYNC_BYTES = (0xC8, 0xEE)  # warto akceptować oba; spotykane w praktyce [web:21][web:69]

def crc8_dvb_s2(data: bytes, poly=0xD5) -> int:
    crc = 0
    for b in data:
        crc ^= b
        for _ in range(8):
            crc = ((crc << 1) ^ poly) & 0xFF if (crc & 0x80) else (crc << 1) & 0xFF
    return crc

def now_us() -> int:
    return time.monotonic_ns() // 1000

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--port", required=True)
    ap.add_argument("-b", "--baud", type=int, default=420000)
    ap.add_argument("-o", "--out", default="crsf_log.csv")
    ap.add_argument("--timeout", type=float, default=0.1)
    args = ap.parse_args()

    ser = serial.Serial(args.port, args.baud, timeout=args.timeout)
    buf = bytearray()
    last_frame_us = None

    with open(args.out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "t_us", "gap_us", "sync", "len",
            "type", "is_extended", "ext_dest", "ext_src",
            "crc_rx", "crc_calc", "crc_ok", "hex"
        ])

        while True:
            chunk = ser.read(4096)
            if not chunk:
                continue
            buf.extend(chunk)

            # Parsowanie strumienia bajtów w stylu "sliding window"
            while True:
                # znajdź sync
                i = next((k for k, v in enumerate(buf) if v in SYNC_BYTES), None)
                if i is None:
                    buf.clear()
                    break
                if i > 0:
                    del buf[:i]
                if len(buf) < 2:
                    break

                sync = buf[0]
                ln = buf[1]  # LEN: type+payload+crc (PayloadLength+2) [web:21]
                total = ln + 2  # + sync+len

                # sanity
                if ln < 2 or ln > 62:  # CRSF max 64B total -> len max 62 [web:21]
                    del buf[0:1]
                    continue
                if len(buf) < total:
                    break

                frame = bytes(buf[:total])
                del buf[:total]

                t_us = now_us()
                gap_us = "" if last_frame_us is None else (t_us - last_frame_us)
                last_frame_us = t_us

                f_type = frame[2]
                payload = frame[3:-1]
                crc_rx = frame[-1]
                crc_calc = crc8_dvb_s2(frame[2:-1])  # type..payload [web:21]
                crc_ok = int(crc_rx == crc_calc)

                is_ext = int(f_type >= 0x28)  # extended packet format for >=0x28 [web:21]
                ext_dest = ""
                ext_src = ""
                if is_ext and len(payload) >= 2:
                    ext_dest = payload[0]
                    ext_src = payload[1]

                w.writerow([
                    t_us, gap_us,
                    f"0x{sync:02X}", f"0x{ln:02X}",
                    f"0x{f_type:02X}", is_ext,
                    (f"0x{ext_dest:02X}" if ext_dest != "" else ""),
                    (f"0x{ext_src:02X}" if ext_src != "" else ""),
                    f"0x{crc_rx:02X}", f"0x{crc_calc:02X}", crc_ok,
                    frame.hex(" ")
                ])
                f.flush()

if __name__ == "__main__":
    main()
