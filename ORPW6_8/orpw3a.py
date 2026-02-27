import customtkinter as ctk
import tkinter as tk
import serial, struct
from PIL import Image, ImageTk, ImageDraw, ImageFont

CRSF_MIN, CRSF_MAX, CRSF_CTR = 172, 1811, 992


# --- KLASA 1: GŁADKI PRZEŁĄCZNIK (BEZ ZMIAN) ---
class SmoothToggleSwitch(tk.Canvas):
    def __init__(self, parent, width=60, height=30, command=None):
        raw_bg = parent.cget("fg_color")
        if isinstance(raw_bg, (list, tuple)) or " " in str(raw_bg):
            bg_color = parent._apply_appearance_mode(raw_bg)
        elif raw_bg == "transparent":
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
        self.render_images()
        self.display_img = self.create_image(0, 0, anchor="nw", image=self.img_off)
        self.bind("<Button-1>", self.toggle)

    def render_images(self):
        scale = 4
        target_size = int(self.height * scale * 0.28)
        font = None
        for f_name in [
            "arialbd.ttf",
            "DejaVuSans-Bold.ttf",
            "Arial_Bold.ttf",
            "LiberationSans-Bold.ttf",
        ]:
            try:
                font = ImageFont.truetype(f_name, target_size)
                break
            except:
                continue
        if not font:
            font = ImageFont.load_default()
        self.img_on = self._create_switch_image(True, font, scale)
        self.img_off = self._create_switch_image(False, font, scale)

    def _create_switch_image(self, state, font, scale):
        w, h = self.width * scale, self.height * scale
        bg_color = "#2e7d32" if state else "#d32f2f"
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle([0, 0, w, h], radius=h // 2, fill=bg_color)
        text = "ON" if state else "OFF"
        bbox = draw.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        tx = (w - h) / 2 - tw / 2 if state else h + (w - h) / 2 - tw / 2
        ty = (h / 2) - (th / 2) - bbox[1]
        draw.text((tx, ty), text, fill="white", font=font)
        margin = 3 * scale
        d = h - 2 * margin
        x_start = (w - h + margin) if state else margin
        draw.ellipse([x_start, margin, x_start + d, margin + d], fill="white")
        return ImageTk.PhotoImage(
            img.resize((self.width, self.height), Image.Resampling.LANCZOS)
        )

    def toggle(self, event=None):
        self.state = not self.state
        self.itemconfig(
            self.display_img, image=self.img_on if self.state else self.img_off
        )
        if self.command:
            self.command(self.state)


# --- KLASA 2: PRZYCISK MONOSTABILNY (BEZ ZMIAN) ---
class MomentaryButton(ctk.CTkButton):
    def __init__(self, parent, text="START", command=None, **kwargs):
        super().__init__(
            parent,
            text=text,
            command=command,
            fg_color="#b71c1c",
            hover_color="#f44336",
            font=("Arial", 12, "bold"),
            width=80,
            height=30,
            **kwargs,
        )


# --- KLASA 3: WIERSZ SYSTEMU (BEZ ZMIAN) ---
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
        self.name = name
        self.callback = callback
        self.unit = unit
        self.grid_columnconfigure(1, weight=1)

        self.label = ctk.CTkLabel(
            self, text=name, font=("Arial", 13, "bold"), width=160, anchor="w"
        )
        self.label.grid(row=0, column=0, padx=(10, 5), pady=10)

        self.slider = None
        if has_slider:
            slider_cont = ctk.CTkFrame(self, fg_color="transparent")
            slider_cont.grid(row=0, column=1, sticky="ew", padx=5)
            slider_cont.grid_columnconfigure(0, weight=1)
            self.slider = ctk.CTkSlider(
                slider_cont, from_=min_val, to=max_val, command=self._update_val_text
            )
            self.slider.grid(row=0, column=0, sticky="ew")
            self.slider.set(min_val)
            self.val_label = ctk.CTkLabel(
                slider_cont, text=f"{min_val}{self.unit}", font=("Arial", 10), width=50
            )
            self.val_label.grid(row=0, column=1, padx=(5, 0))
        else:
            ctk.CTkFrame(self, fg_color="transparent", height=0).grid(row=0, column=1)

        self.switch = None
        if has_switch:
            self.switch = SmoothToggleSwitch(
                self, width=60, height=30, command=self._on_change
            )
            self.switch.grid(row=0, column=2, padx=10, pady=10)
        else:
            ctk.CTkFrame(self, width=60, height=30, fg_color="transparent").grid(
                row=0, column=2, padx=10
            )

        self.btn = None
        if has_button:
            self.btn = MomentaryButton(self, text="START", command=self._on_button_push)
            self.btn.grid(row=0, column=3, padx=(5, 10), pady=10)
        else:
            ctk.CTkFrame(self, width=80, height=30, fg_color="transparent").grid(
                row=0, column=3, padx=(5, 10)
            )

    def _update_val_text(self, val):
        if hasattr(self, "val_label"):
            self.val_label.configure(text=f"{int(val)}{self.unit}")
        self._on_change()

    def _on_button_push(self):
        if self.callback:
            sw_state = self.switch.state if self.switch else "N/A"
            self.callback(self.name, sw_state, "IMPULS")

    def _on_change(self, state=None):
        if self.callback:
            sw_state = self.switch.state if self.switch else "N/A"
            current_val = int(self.slider.get()) if self.slider else None
            val_str = f"{current_val}{self.unit}" if current_val is not None else None
            self.callback(self.name, sw_state, val_str)


# --- KLASA 4: APLIKACJA GŁÓWNA ---
class App(ctk.CTk):  # ← 0 spacji

    def __init__(self):  # ← 4 spacje (metoda klasy)
        super().__init__()  # ← 8 spacji (ciało metody)

        # ── Połączenie z Pico ──────────────────────────────────
        try:  # ← 8 spacji
            self.pico = serial.Serial("/dev/ttyAMA0", 115200, timeout=0.01)
        except Exception as e:  # ← 8 spacji
            self.pico = None  # ← 12 spacji
            print(f"Pico offline: {e}")  # ← 12 spacji

        self._gui_ch = [CRSF_CTR] * 12  # ← 8 spacji
        self._buttons = 0  # ← 8 spacji

        self._slider_ch = {  # ← 8 spacji
            "Obrót Wieży": (0, -180, 180),
            "Elewacja Działa": (1, -20, 90),
            "Wysunięcie lufy": (2, 0, 500),
            "Moc Strzału": (3, 0, 100),
        }
        self._btn_bit = {  # ← 8 spacji
            "Procedura Ognia": 0,
        }

        # ── GUI setup ──────────────────────────────────────────
        self.geometry("800x600")
        self.title("Military Control Panel 2026")

        self.systemy_lista = [
            ("Obrót Wieży", True, False, True, -180, 180, "°"),
            ("Elewacja Działa", True, False, True, -20, 90, "°"),
            ("Wysunięcie lufy", True, False, True, 0, 500, "mm"),
            ("Moc Strzału", True, False, True, 0, 100, "%"),
            ("Procedura Ognia", False, True, False, 0, 0, ""),
        ]

        ctk.CTkLabel(
            self, text="PANEL STEROWANIA ARTYLERIĄ 2026", font=("Arial", 22, "bold")
        ).pack(pady=20)
        self.main_frame = ctk.CTkScrollableFrame(self, width=750, height=450)
        self.main_frame.pack(padx=20, pady=10, fill="both", expand=True)

        for name, sl, btn, sw, mi, ma, unit in self.systemy_lista:
            row = SystemRow(
                self.main_frame, name, sl, btn, sw, mi, ma, unit, self.log_event
            )
            row.pack(fill="x", pady=5)

    # ── Metody App (4 spacje = należą do klasy, nie do __init__!) ─

    def _map_crsf(self, val, lo, hi):  # ← 4 spacje
        r = max(0.0, min(1.0, (float(val) - lo) / (hi - lo)))
        return int(CRSF_MIN + r * (CRSF_MAX - CRSF_MIN))

    def _pack_buttons(self):  # ← 4 spacje
        self._gui_ch[0] = self._buttons & 0x7FF
        self._gui_ch[1] = (self._buttons >> 11) & 0x7FF
        self._gui_ch[2] = (self._buttons >> 22) & 0xFF

    def send_to_pico(self):  # ← 4 spacje
        if not self.pico:
            return
        data = struct.pack("<12H", *[max(0, min(2047, v)) for v in self._gui_ch])
        crc = 0
        for b in data:
            crc ^= b
        self.pico.write(bytes([0xAA]) + data + bytes([crc, 0xBB]))

    def _clear_bit(self, bit):  # ← 4 spacje
        self._buttons &= ~(1 << bit)
        self._pack_buttons()
        self.send_to_pico()

    def log_event(self, name, state, value):  # ← 4 spacje
        changed = False
        if name in self._slider_ch and value not in (None, "IMPULS"):
            idx, lo, hi = self._slider_ch[name]
            num = "".join(c for c in str(value) if c in "0123456789.-")
            if num:
                self._gui_ch[3 + idx] = self._map_crsf(float(num), lo, hi)
                changed = True
        if name in self._btn_bit and state != "N/A":
            bit = self._btn_bit[name]
            if state:
                self._buttons |= 1 << bit
            else:
                self._buttons &= ~(1 << bit)
            self._pack_buttons()
            changed = True
        if value == "IMPULS" and name in self._btn_bit:
            bit = self._btn_bit[name]
            self._buttons |= 1 << bit
            self._pack_buttons()
            self.send_to_pico()
            self.after(150, lambda b=bit: self._clear_bit(b))
            print(f"[!] {name}: IMPULS (bit {bit})")
            return
        if changed:
            self.send_to_pico()
        print(f"[{name}] SW:{state} | {value}")


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    app = App()
    app.mainloop()
