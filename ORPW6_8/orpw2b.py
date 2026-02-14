import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw, ImageFont

# --- KLASA 1: GŁADKI PRZEŁĄCZNIK (BEZ ZMIAN) ---
class SmoothToggleSwitch(tk.Canvas):
    def __init__(self, parent, width=60, height=30, command=None):
        raw_bg = parent.cget("fg_color")
        if isinstance(raw_bg, (list, tuple)) or " " in str(raw_bg):
            bg_color = parent._apply_appearance_mode(raw_bg)
        elif raw_bg == "transparent":
            # Poprawka pobierania koloru tła dla wersji 2026
            bg_color = parent._apply_appearance_mode(ctk.ThemeManager.theme["CTkFrame"]["fg_color"])
        else:
            bg_color = raw_bg

        super().__init__(parent, width=width, height=height, highlightthickness=0, bg=bg_color, cursor="hand2")
        self.width, self.height, self.command = width, height, command
        self.state = False
        self.render_images()
        self.display_img = self.create_image(0, 0, anchor="nw", image=self.img_off)
        self.bind("<Button-1>", self.toggle)

    def render_images(self):
        scale = 4
        target_size = int(self.height * scale * 0.28)
        font = None
        for f_name in ["arialbd.ttf", "DejaVuSans-Bold.ttf", "Arial_Bold.ttf", "LiberationSans-Bold.ttf"]:
            try:
                font = ImageFont.truetype(f_name, target_size)
                break
            except: continue
        if not font: font = ImageFont.load_default()
        self.img_on = self._create_switch_image(True, font, scale)
        self.img_off = self._create_switch_image(False, font, scale)

    def _create_switch_image(self, state, font, scale):
        w, h = self.width * scale, self.height * scale
        bg_color = "#2e7d32" if state else "#d32f2f"
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle([0, 0, w, h], radius=h//2, fill=bg_color)
        
        text = "ON" if state else "OFF"
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        
        tx = (w - h) / 2 - tw / 2 if state else h + (w - h) / 2 - tw / 2
        ty = (h / 2) - (th / 2) - bbox[1]
        
        draw.text((tx, ty), text, fill="white", font=font)
        margin = 3 * scale
        d = h - 2 * margin
        x_start = (w - h + margin) if state else margin
        draw.ellipse([x_start, margin, x_start + d, margin + d], fill="white")
        return ImageTk.PhotoImage(img.resize((self.width, self.height), Image.Resampling.LANCZOS))

    def toggle(self, event=None):
        self.state = not self.state
        self.itemconfig(self.display_img, image=self.img_on if self.state else self.img_off)
        if self.command: self.command(self.state)

# --- KLASA 2: PRZYCISK MONOSTABILNY ---
class MomentaryButton(ctk.CTkButton):
    def __init__(self, parent, text="START", command=None, **kwargs):
        super().__init__(parent, text=text, command=command, fg_color="#b71c1c",
                         hover_color="#f44336", font=("Arial", 12, "bold"), width=80, height=30, **kwargs)

# --- KLASA 3: WIERSZ SYSTEMU (POPRAWIONA) ---

class SystemRow(ctk.CTkFrame):
    def __init__(self, parent, name, has_slider=False, has_button=False, has_switch=True, callback=None):
        super().__init__(parent, fg_color="transparent")
        self.name = name
        self.callback = callback

        # Konfiguracja kolumn: Kolumna 1 (Slider) rozciąga się
        self.grid_columnconfigure(1, weight=1)

        # --- KOLUMNA 0: NAPIS ---
        self.label = ctk.CTkLabel(self, text=name, font=("Arial", 14, "bold"), width=130, anchor="w")
        self.label.grid(row=0, column=0, padx=(10, 5), pady=10)

        # --- KOLUMNA 1: SLIDER ---
        self.slider = None
        if has_slider:
            slider_cont = ctk.CTkFrame(self, fg_color="transparent")
            slider_cont.grid(row=0, column=1, sticky="ew", padx=5)
            slider_cont.grid_columnconfigure(0, weight=1)

            self.slider = ctk.CTkSlider(slider_cont, from_=0, to=100, command=self._update_val_text)
            self.slider.grid(row=0, column=0, sticky="ew")
            self.slider.set(0)

            self.val_label = ctk.CTkLabel(slider_cont, text="0%", font=("Arial", 10), width=40)
            self.val_label.grid(row=0, column=1, padx=(5, 0))
        else:
            # Puste miejsce, aby zachować strukturę siatki
            ctk.CTkFrame(self, fg_color="transparent", height=0).grid(row=0, column=1)

        # --- KOLUMNA 2: TOGGLE SWITCH ---
        self.switch = None
        if has_switch:
            self.switch = SmoothToggleSwitch(self, width=60, height=30, command=self._on_change)
            self.switch.grid(row=0, column=2, padx=10, pady=10)
        else:
            # Placeholder o szerokości switcha (60px)
            ctk.CTkFrame(self, width=60, height=30, fg_color="transparent").grid(row=0, column=2, padx=10)

        # --- KOLUMNA 3: PRZYCISK CHWILOWY ---
        self.btn = None
        if has_button:
            self.btn = MomentaryButton(self, text="START", command=self._on_button_push)
            self.btn.grid(row=0, column=3, padx=(5, 10), pady=10)
        else:
            # Placeholder o szerokości przycisku (80px)
            ctk.CTkFrame(self, width=80, height=30, fg_color="transparent").grid(row=0, column=3, padx=(5, 10))

    def _update_val_text(self, val):
        if hasattr(self, 'val_label'):
            self.val_label.configure(text=f"{int(val)}%")
        self._on_change()

    def _on_button_push(self):
        if self.callback:
            sw_state = self.switch.state if self.switch else "N/A"
            self.callback(self.name, sw_state, "IMPULS")

    def _on_change(self, state=None):
        if self.callback:
            sw_state = self.switch.state if self.switch else "N/A"
            current_val = int(self.slider.get()) if self.slider else None
            self.callback(self.name, sw_state, current_val)


# --- KLASA 4: APLIKACJA GŁÓWNA ---
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("700x700")
        self.title("Military Control Panel 2026")
					#   suwak   MBTN  Togle   
        self.systemy_lista = [
            ("Kierunkowy Kąt obrotowy",     True , False, True),
            ("Kąt Podniesienia - elewacja", True , False, True),
            ("Wystrzał",      		    False, True , False)
            #("Moc Reaktora",                True , True , True),
            #("System Chłodzenia",           True , True , False),
            #("Sygnał Bojowy",               True , False , False),
            #("Autodestrukcja",              False, False , False)
        ]

        ctk.CTkLabel(self, text="PANEL STEROWANIA DZIAŁEM 2026", font=("Arial", 22, "bold")).pack(pady=20)
        self.main_frame = ctk.CTkScrollableFrame(self, width=650, height=550)
        self.main_frame.pack(padx=20, pady=10, fill="both", expand=True)

        for name, has_slider, has_button, has_switch in self.systemy_lista:
            row = SystemRow(self.main_frame, name, has_slider, has_button, has_switch, self.log_event)
            row.pack(fill="x", pady=5)

    def log_event(self, name, state, value):
        status = f"Switch: {state}"
        if value == "IMPULS":
            print(f"[!] {name}: Wciśnięto przycisk! ({status})")
        else:
            power = f" | Moc: {value}%" if value is not None else ""
            print(f"[{name}] {status}{power}")

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    app = App()
    app.mainloop()
