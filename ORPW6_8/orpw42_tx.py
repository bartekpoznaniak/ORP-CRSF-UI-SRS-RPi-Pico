#!/usr/bin/env python3
"""
orpw4_tx.py – Military Control Panel UI (RPI5) v2.0
UART GPIO4/GPIO5 @ 115200: 0xAA | 12×uint16 LE | XOR-CRC | 0xBB (27 bajtów)

Mapowanie gui_ch[0..11] → CH5-CH16:
  gui_ch[0]  CH5  : ARM (CRSF_MIN=off / CRSF_MAX=on)
  gui_ch[1]  CH6  : Switch bitmask sw[0..9]   (raw 0-1023)
  gui_ch[2]  CH7  : Switch bitmask sw[10..19] (raw 0-1023)
  gui_ch[3]  CH8  : Switch bitmask sw[20..29] (raw 0-1023)
  gui_ch[4]  CH9  : Obrót Wieży    (CRSF 172-1811)
  gui_ch[5]  CH10 : Elewacja Działa(CRSF 172-1811)
  gui_ch[6]  CH11 : Wysunięcie Lufy(CRSF 172-1811)
  gui_ch[7]  CH12 : Moc Strzału    (CRSF 172-1811)
  gui_ch[8]  CH13 : Fire bitmask   (raw 0-1023)
  gui_ch[9]  CH14 : Rezerwa
  gui_ch[10] CH15 : Rezerwa
  gui_ch[11] CH16 : Rezerwa
"""

import customtkinter as ctk
import tkinter as tk
import serial
import struct
from PIL import Image, ImageTk, ImageDraw, ImageFont

CRSF_MIN, CRSF_MAX, CRSF_CTR = 172, 1811, 992
UART_PORT = "/dev/ttyAMA2"
UART_BAUD = 115200
SEND_HZ = 50
FRAME_SOF = 0xAA
FRAME_EOF = 0xBB
NUM_GUI_CH = 12

# ── Helpers ──────────────────────────────────────────────────


def map_crsf(val: float, lo: float, hi: float) -> int:
    r = max(0.0, min(1.0, (val - lo) / (hi - lo)))
    return int(CRSF_MIN + r * (CRSF_MAX - CRSF_MIN))


def build_uart_frame(channels: list[int]) -> bytes:
    payload = struct.pack("<12H", *[max(0, min(2047, v)) for v in channels])
    crc = 0
    for b in payload:
        crc ^= b
    return bytes([FRAME_SOF]) + payload + bytes([crc, FRAME_EOF])


# ── Widget: Smooth Toggle Switch ─────────────────────────────


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


# ── Widget: System Row ───────────────────────────────────────


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
            self, text=name, font=("Arial", 13, "bold"), width=160, anchor="w"
        ).grid(row=0, column=0, padx=(10, 5), pady=4)

        self.slider = None
        if has_slider:
            cont = ctk.CTkFrame(self, fg_color="transparent")
            cont.grid(row=0, column=1, sticky="ew", padx=5, pady=4)
            cont.grid_columnconfigure(0, weight=1)
            self.slider = ctk.CTkSlider(
                cont, from_=min_val, to=max_val, command=self._slider_moved
            )
            self.slider.grid(row=0, column=0, sticky="ew")
            self.slider.set(min_val)
            self._val_lbl = ctk.CTkLabel(
                cont, text=f"{min_val}{unit}", font=("Arial", 10), width=50
            )
            self._val_lbl.grid(row=0, column=1, padx=(5, 0))
        else:
            ctk.CTkFrame(self, fg_color="transparent", height=0).grid(row=0, column=1)

        self.switch = None
        if has_switch:
            self.switch = SmoothToggleSwitch(
                self, width=60, height=30, command=self._on_change
            )
            self.switch.grid(row=0, column=2, padx=10, pady=4)
        else:
            ctk.CTkFrame(self, width=60, height=30, fg_color="transparent").grid(
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
            self.btn.grid(row=0, column=3, padx=(5, 10), pady=4)
        else:
            ctk.CTkFrame(self, width=80, height=30, fg_color="transparent").grid(
                row=0, column=3, padx=(5, 10)
            )

    def _slider_moved(self, val):
        if hasattr(self, "_val_lbl"):
            self._val_lbl.configure(text=f"{int(val)}{self.unit}")
        self._on_change()

    def _on_impulse(self):
        if self.callback:
            self.callback(self.name, False, "IMPULSE")

    def _on_change(self, _=None):
        if self.callback:
            sw = self.switch.state if self.switch else False
            val = int(self.slider.get()) if self.slider else None
            self.callback(self.name, sw, val)


# ── Main App ─────────────────────────────────────────────────


class App(ctk.CTk):

    SYSTEMS = [
        # (name,            slider, button, switch, min,  max,  unit)
        ("ARM", False, False, True, 0, 1, ""),
        ("Oświetlenie 1", False, False, True, 0, 1, ""),
        ("Oświetlenie 2", False, False, True, 0, 1, ""),
        ("Obrót Wieży", True, False, True, -180, 180, "°"),
        ("Elewacja Działa", True, False, True, -20, 90, "°"),
        ("Wysunięcie Lufy", True, False, True, 0, 500, "mm"),
        ("Moc Strzału", True, False, True, 0, 100, "%"),
        ("Procedura Ognia", False, True, False, 0, 0, ""),
    ]

    # ARM → gui_ch[0] = CH5, osobna logika
    ARM_IDX = 0

    # Switch → (gui_ch_idx, bit)
    # gui_ch[1]=CH6 bity 0-9, gui_ch[2]=CH7 bity 10-19, gui_ch[3]=CH8 bity 20-29
    SWITCH_MAP = {
        "Oświetlenie 1": (1, 1),
        "Oświetlenie 2": (1, 2),
        "Obrót Wieży": (1, 3),
        "Elewacja Działa": (1, 4),
        "Wysunięcie Lufy": (1, 5),
        "Moc Strzału": (1, 6),
        # "Oświetlenie 1": (1, 0),
        # "Oświetlenie 2": (1, 1),
        # "Obrót Wieży": (1, 2),
        # "Elewacja Działa": (1, 3),
        # "Wysunięcie Lufy": (1, 4),
        # "Moc Strzału": (1, 5),
        # Kolejne switche: (1, 6)..(1, 9), potem (2, 0)..(2, 9), itd.
    }

    # Slider → (gui_ch_idx, lo, hi)
    SLIDER_MAP = {
        "Obrót Wieży": (4, -180, 180),
        "Elewacja Działa": (5, -20, 90),
        "Wysunięcie Lufy": (6, 0, 500),
        "Moc Strzału": (7, 0, 100),
    }

    # Impulse → (gui_ch_idx, bit)
    FIRE_MAP = {
        # "Procedura Ognia": (8, 0),
        "Procedura Ognia": (8, 1),
    }

    def __init__(self):
        super().__init__()
        self.title("Military Control Panel 2026")
        self.geometry("820x560")

        self._gui_ch = [CRSF_CTR] * NUM_GUI_CH
        self._gui_ch[self.ARM_IDX] = CRSF_MIN  # ARM domyślnie OFF
        # self._gui_ch[1] = 0  # CH6 switch bitmask
        # self._gui_ch[2] = 0  # CH7 switch bitmask
        # self._gui_ch[3] = 0  # CH8 switch bitmask
        # self._gui_ch[8] = 0  # CH13 fire bitmask

        self._gui_ch[1] = 1  # CH6 switch bitmask
        self._gui_ch[2] = 1  # CH7 switch bitmask
        self._gui_ch[3] = 1  # CH8 switch bitmask
        self._gui_ch[8] = 1  # CH13 fire bitmask

        try:
            self._ser = serial.Serial(UART_PORT, UART_BAUD, timeout=0.01)
            print(f"[UART] Połączono z PICO @ {UART_PORT}")
        except Exception as e:
            self._ser = None
            print(f"[UART] PICO offline: {e}")

        ctk.CTkLabel(
            self, text="⚙ PANEL STEROWANIA – RC ELRS 2026", font=("Arial", 16, "bold")
        ).pack(pady=8)

        self._frame = ctk.CTkScrollableFrame(self, width=780, height=460)
        self._frame.pack(padx=16, pady=4, fill="both", expand=True)

        for name, sl, btn, sw, mi, ma, unit in self.SYSTEMS:
            SystemRow(
                self._frame, name, sl, btn, sw, mi, ma, unit, callback=self._on_event
            ).pack(fill="x", pady=2)

        self._send_loop()

    def _on_event(self, name: str, state: bool, value):
        # ARM — osobny kanał, prosta wartość
        if name == "ARM":
            self._gui_ch[self.ARM_IDX] = CRSF_MAX if state else CRSF_MIN
            return

        # Switch bitmask
        if name in self.SWITCH_MAP:
            ch_idx, bit = self.SWITCH_MAP[name]

            if state:
                self._gui_ch[ch_idx] |= 1 << bit
            else:
                self._gui_ch[ch_idx] &= ~(1 << bit)

        # Slider → CRSF range
        if name in self.SLIDER_MAP and value not in (None, "IMPULSE"):
            ch_idx, lo, hi = self.SLIDER_MAP[name]
            self._gui_ch[ch_idx] = map_crsf(float(value), lo, hi)

        # Fire impulse — chwilowy bit
        if value == "IMPULSE" and name in self.FIRE_MAP:
            ch_idx, bit = self.FIRE_MAP[name]
            self._gui_ch[ch_idx] |= 1 << bit
            self._send_now()
            self.after(150, lambda ci=ch_idx, b=bit: self._clear_fire(ci, b))
            return

    def _clear_fire(self, ch_idx: int, bit: int):
        self._gui_ch[ch_idx] &= ~(1 << bit)

    def _send_now(self):
        if not self._ser:
            return
        try:
            self._ser.write(build_uart_frame(self._gui_ch))
            frame = build_uart_frame(self._gui_ch)  # ←--- Najpierw to
            # print(
            #    f"[TX] CH6={self._gui_ch[1]:4d} frame={frame[1:7].hex().upper()} CRC={frame[25]:02X}"
            # )
        except serial.SerialException as e:
            print(f"[UART] Błąd zapisu: {e}")

    def _send_loop(self):
        self._send_now()
        self.after(1000 // SEND_HZ, self._send_loop)


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    app = App()
    app.mainloop()
