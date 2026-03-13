#!/usr/bin/env python3
"""
orpw4_tx.py  –  Military Control Panel UI (RPI5)
Wysyła stany GUI do PICO przez UART GPIO4/GPIO5 @ 115200
Protokół: 0xAA | 12x uint16 LE | XOR-CRC | 0xBB  (28 bajtów)

CH map (indeksy 0-11 odpowiadają CH5-CH16 w CRSF):
  idx 0-2  : packed bits przycisków (3 × 11 bitów = 33 bity)
  idx 3-6  : suwaki (Obrót, Elewacja, Lufa, Moc)
  idx 7-11 : rezerwa (wysyłamy 992)
"""

import customtkinter as ctk
import tkinter as tk
import serial
import struct
import time
from PIL import Image, ImageTk, ImageDraw, ImageFont

CRSF_MIN, CRSF_MAX, CRSF_CTR = 172, 1811, 992
UART_PORT = "/dev/ttyAMA2"  # GPIO4=TX / GPIO5=RX  (uart2 na RPI5)
UART_BAUD = 115200
SEND_HZ = 50  # wysyłamy do PICO 50×/s (PICO samo robi 100Hz CRSF)
FRAME_SOF = 0xAA
FRAME_EOF = 0xBB
NUM_GUI_CH = 12


# ─────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────


def map_crsf(val: float, lo: float, hi: float) -> int:
    """Liniowe mapowanie wartości fizycznej → zakres CRSF 172-1811."""
    r = max(0.0, min(1.0, (val - lo) / (hi - lo)))
    return int(CRSF_MIN + r * (CRSF_MAX - CRSF_MIN))


def build_uart_frame(channels: list[int]) -> bytes:
    """
    Buduje ramkę binarną dla PICO.
    channels: lista 12 wartości CRSF (0-2047)
    Format: SOF(1) + 12×uint16-LE(24) + XOR-CRC(1) + EOF(1) = 28 bajtów
    """
    payload = struct.pack("<12H", *[max(0, min(2047, v)) for v in channels])
    crc = 0
    for b in payload:
        crc ^= b
    return bytes([FRAME_SOF]) + payload + bytes([crc, FRAME_EOF])


# ─────────────────────────────────────────────────────────────
#  WIDGET: Gładki przełącznik ON/OFF
# ─────────────────────────────────────────────────────────────


class SmoothToggleSwitch(tk.Canvas):
    def __init__(self, parent, width=60, height=30, command=None):
        raw_bg = parent.cget("fg_color")
        if isinstance(raw_bg, (list, tuple)):
            bg_color = parent._apply_appearance_mode(raw_bg)
        elif str(raw_bg) == "transparent":
            bg_color = parent._apply_appearance_mode(
                ctk.ThemeManager.theme["CTkFrame"]["fg_color"]
            )
        else:
            bg_color = raw_bg
        super().__init__(
            parent,
            width=width,
            height=height,
            highlightthickness=0,
            bg=bg_color,
            cursor="hand2",
        )
        self.width, self.height, self.command = width, height, command
        self.state = False
        self._render()
        self._img_id = self.create_image(0, 0, anchor="nw", image=self._img_off)
        self.bind("<Button-1>", self.toggle)

    def _render(self):
        scale = 4
        sz = int(self.height * scale * 0.28)
        font = None
        for fn in ["arialbd.ttf", "DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf"]:
            try:
                font = ImageFont.truetype(fn, sz)
                break
            except Exception:
                pass
        if not font:
            font = ImageFont.load_default()
        self._img_on = self._make_img(True, font, scale)
        self._img_off = self._make_img(False, font, scale)

    def _make_img(self, state, font, scale):
        w, h = self.width * scale, self.height * scale
        color = "#2e7d32" if state else "#d32f2f"
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle([0, 0, w, h], radius=h // 2, fill=color)
        text = "ON" if state else "OFF"
        bb = draw.textbbox((0, 0), text, font=font)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        tx = (w - h) / 2 - tw / 2 if state else h + (w - h) / 2 - tw / 2
        ty = h / 2 - th / 2 - bb[1]
        draw.text((tx, ty), text, fill="white", font=font)
        m = 3 * scale
        d = h - 2 * m
        x0 = (w - h + m) if state else m
        draw.ellipse([x0, m, x0 + d, m + d], fill="white")
        return ImageTk.PhotoImage(
            img.resize((self.width, self.height), Image.Resampling.LANCZOS)
        )

    def toggle(self, _=None):
        self.state = not self.state
        self.itemconfig(
            self._img_id, image=self._img_on if self.state else self._img_off
        )
        if self.command:
            self.command(self.state)


# ─────────────────────────────────────────────────────────────
#  WIDGET: Wiersz systemu (nazwa + suwak + switch + przycisk)
# ─────────────────────────────────────────────────────────────


class SystemRow(ctk.CTkFrame):
    def __init__(
        self,
        parent,
        name,
        has_slider=False,
        has_button=False,
        has_switch=True,
        min_val=0,
        max_val=100,
        unit="%",
        callback=None,
    ):
        super().__init__(parent, fg_color="transparent")
        self.name, self.callback, self.unit = name, callback, unit
        self.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            self, text=name, font=("Arial", 20, "bold"), width=160, anchor="w"
        ).grid(row=0, column=0, padx=(10, 5), pady=10)

        self.slider = None
        if has_slider:
            cont = ctk.CTkFrame(self, fg_color="transparent")
            cont.grid(row=0, column=1, sticky="ew", padx=5)
            cont.grid_columnconfigure(0, weight=1)
            self.slider = ctk.CTkSlider(
                cont, from_=min_val, to=max_val, command=self._slider_moved
            )
            self.slider.grid(row=0, column=0, sticky="ew")
            self.slider.set(min_val)
            self._val_lbl = ctk.CTkLabel(
                cont, text=f"{min_val}{unit}", font=("Arial", 10), width=55
            )
            self._val_lbl.grid(row=0, column=1, padx=(5, 0))
        else:
            ctk.CTkFrame(self, fg_color="transparent").grid(row=0, column=1)

        self.switch = None
        if has_switch:
            self.switch = SmoothToggleSwitch(
                self, width=60, height=30, command=self._on_change
            )
            self.switch.grid(row=0, column=2, padx=10, pady=10)
        else:
            ctk.CTkFrame(self, width=60, fg_color="transparent").grid(
                row=0, column=2, padx=10
            )

        self.btn = None
        if has_button:
            self.btn = ctk.CTkButton(
                self,
                text="FIRE",
                command=self._on_impulse,
                fg_color="#b71c1c",
                hover_color="#f44336",
                font=("Arial", 12, "bold"),
                width=80,
                height=30,
            )
            self.btn.grid(row=0, column=3, padx=(5, 10), pady=10)
        else:
            ctk.CTkFrame(self, width=80, fg_color="transparent").grid(
                row=0, column=3, padx=(5, 10)
            )

    def _slider_moved(self, val):
        if hasattr(self, "_val_lbl"):
            self._val_lbl.configure(text=f"{int(val)}{self.unit}")
        self._on_change()

    def _on_impulse(self):
        if self.callback:
            self.callback(
                self.name, self.switch.state if self.switch else False, "IMPULSE"
            )

    def _on_change(self, _=None):
        if self.callback:
            sw = self.switch.state if self.switch else False
            val = int(self.slider.get()) if self.slider else None
            self.callback(self.name, sw, val)


# ─────────────────────────────────────────────────────────────
#  APLIKACJA GŁÓWNA
# ─────────────────────────────────────────────────────────────


class App(ctk.CTk):

    # Definicja systemów: (nazwa, suwak, przycisk, switch, min, max, jednostka)
    SYSTEMS = [
        ("Oświetlenie 1", False, False, True, 0, 1, ""),
        ("Oświetlenie 2", False, False, True, 0, 1, ""),
        ("Obrót Wieży", True, False, True, -180, 180, "°"),
        ("Elewacja Działa", True, False, True, -20, 90, "°"),
        ("Wysunięcie Lufy", True, False, True, 0, 500, "mm"),
        ("Moc Strzału", True, False, True, 0, 100, "%"),
        ("Procedura Ognia", False, True, False, 0, 0, ""),
    ]

    # Mapowanie nazw → indeks suwaka w _gui_ch[3..6]
    SLIDER_MAP = {
        "Obrót Wieży": (3, -180, 180),
        "Elewacja Działa": (4, -20, 90),
        "Wysunięcie Lufy": (5, 0, 500),
        "Moc Strzału": (6, 0, 100),
    }

    # Mapowanie nazw → numer bitu w _buttons (32-bit int)
    BIT_MAP = {
        "Oświetlenie 1": 0,
        "Oświetlenie 2": 1,
        "Procedura Ognia": 2,
    }

    def __init__(self):
        super().__init__()
        self.title("Military Control Panel 2026")
        self.geometry("820x640")

        # Stan wewnętrzny
        self._gui_ch = [CRSF_CTR] * NUM_GUI_CH  # CH5-CH16
        self._buttons = 0  # 32-bit maska przycisków

        # UART → PICO
        try:
            self._ser = serial.Serial(UART_PORT, UART_BAUD, timeout=0.01)
            print(f"[UART] Połączono z PICO @ {UART_PORT}")
        except Exception as e:
            self._ser = None
            print(f"[UART] PICO offline: {e}")

        # GUI
        ctk.CTkLabel(
            self, text="⚙ PANEL STEROWANIA – RC ELRS 2026", font=("Arial", 20, "bold")
        ).pack(pady=16)

        self._frame = ctk.CTkScrollableFrame(self, width=780, height=520)
        self._frame.pack(padx=16, pady=8, fill="both", expand=True)

        for name, sl, btn, sw, mi, ma, unit in self.SYSTEMS:
            SystemRow(
                self._frame, name, sl, btn, sw, mi, ma, unit, callback=self._on_event
            ).pack(fill="x", pady=4)

        # Cykliczne wysyłanie do PICO
        self._send_loop()

    # ── Logika zdarzeń ────────────────────────────────────────

    def _on_event(self, name: str, state: bool, value):
        """Callback z każdego wiersza GUI."""

        # Suwak → kanal CH8-CH11
        if name in self.SLIDER_MAP and value not in (None, "IMPULSE"):
            idx, lo, hi = self.SLIDER_MAP[name]
            self._gui_ch[idx] = map_crsf(float(value), lo, hi)

        # Przełącznik → bit w _buttons
        if name in self.BIT_MAP and isinstance(state, bool):
            bit = self.BIT_MAP[name]
            if state:
                self._buttons |= 1 << bit
            else:
                self._buttons &= ~(1 << bit)
            self._pack_bits()

        # Monostabilny impuls → ustaw bit, wyślij, skasuj po 150ms
        if value == "IMPULSE" and name in self.BIT_MAP:
            bit = self.BIT_MAP[name]
            self._buttons |= 1 << bit
            self._pack_bits()
            self._send_now()
            self.after(150, lambda b=bit: self._clear_bit(b))
            print(f"[IMPULSE] {name} bit={bit}")
            return

        print(f"[EVT] {name} | SW={state} | VAL={value}")

    def _pack_bits(self):
        self._gui_ch[0] = CRSF_MIN + (self._buttons & 0x07) * 200
        self._gui_ch[1] = CRSF_CTR
        self._gui_ch[2] = CRSF_CTR
        print(f"[BITS] buttons={self._buttons:#010b} → gui_ch[0]={self._gui_ch[0]}")

    def _clear_bit(self, bit: int):
        self._buttons &= ~(1 << bit)
        self._pack_bits()

    # ── Wysyłanie ─────────────────────────────────────────────
    # GLUPI KOMENTARDZ DO USUNIĘCIA
    def _send_now(self):
        if not self._ser:
            return
        frame = build_uart_frame(self._gui_ch)
        try:
            self._ser.write(frame)
        except serial.SerialException as e:
            print(f"[UART] Błąd zapisu: {e}")

    def _send_loop(self):
        """Cykliczne wysyłanie co 1000/SEND_HZ ms."""
        self._send_now()
        self.after(1000 // SEND_HZ, self._send_loop)


# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    app = App()
    app.mainloop()
