import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw, ImageFont

class SmoothToggleSwitch(tk.Canvas):
    def __init__(self, parent, width=60, height=30, command=None):
        # Automatyczne pobieranie koloru tła z CTK
        raw_bg = parent.cget("fg_color")
        if isinstance(raw_bg, (list, tuple)) or " " in str(raw_bg):
            bg_color = parent._apply_appearance_mode(raw_bg)
        elif raw_bg == "transparent":
            bg_color = parent._apply_appearance_mode(ctk.ThemeManager.theme["CTkFrame"]["fg_color"])
        else:
            bg_color = raw_bg

        super().__init__(parent, width=width, height=height, highlightthickness=0, bg=bg_color, cursor="hand2")
        self.width, self.height, self.command = width, height, command
        self.state = False
        
        # Generowanie obrazów
        self.render_images()
        self.display_img = self.create_image(0, 0, anchor="nw", image=self.img_off)
        self.bind("<Button-1>", self.toggle)

    def render_images(self):
        scale = 4
        target_size = int(self.height * scale * 0.28)
        
        # Próba znalezienia fontu
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
        tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]

        # Precyzyjne centrowanie w wolnym obszarze (tam gdzie nie ma kółka)
        if state:
            tx = (w - h) / 2 - tw / 2
        else:
            tx = h + (w - h) / 2 - tw / 2
            
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

class SystemRow(ctk.CTkFrame):
    def __init__(self, parent, name, has_slider=False, callback=None):
        super().__init__(parent, fg_color="transparent")
        self.name = name
        self.callback = callback

        self.grid_columnconfigure(1, weight=1)

        # 1. Nazwa systemu
        self.label = ctk.CTkLabel(self, text=name, font=("Arial", 14, "bold"), width=120, anchor="w")
        self.label.grid(row=0, column=0, padx=10, pady=10)

        # 2. Kontener suwaka (jeśli potrzebny)
        self.slider = None
        self.val_label = None
        if has_slider:
            slider_cont = ctk.CTkFrame(self, fg_color="transparent")
            slider_cont.grid(row=0, column=1, sticky="ew", padx=5)
            slider_cont.grid_columnconfigure(0, weight=1)

            self.slider = ctk.CTkSlider(slider_cont, from_=0, to=100, command=self._update_val_text)
            self.slider.grid(row=0, column=0, sticky="ew")
            self.slider.set(0)

            self.val_label = ctk.CTkLabel(slider_cont, text="0%", font=("Arial", 10), width=35)
            self.val_label.grid(row=0, column=1, padx=(5, 0))

        # 3. Przełącznik (Switch)
        self.switch = SmoothToggleSwitch(self, width=60, height=30, command=self._on_change)
        self.switch.grid(row=0, column=2, padx=10, pady=10)

    def _update_val_text(self, val):
        if self.val_label:
            self.val_label.configure(text=f"{int(val)}%")
        self._on_change()

    def _on_change(self, state=None):
        if self.callback:
            # Jeśli state nie został podany (zmiana suwaka), bierzemy aktualny ze switcha
            current_state = self.switch.state
            current_val = int(self.slider.get()) if self.slider else None
            self.callback(self.name, current_state, current_val)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("550x600")
        self.title("Military Control Panel 2026")

        # Lista: (Nazwa, Czy ma suwak)
        self.systemy_lista = [
            ("Pozycja obrotowa lufy 0-360°", True),
            ("Pozycja lufy 0-90°", True)
#            ("Torpedy", True),
#            ("Pole Siłowe", True),
#            ("Chłodzenie", True),
#            ("Autopilot", False),
#	     ("Reaktor",True)
        ]

        ctk.CTkLabel(self, text="KONSOLA ZARZĄDZANIA", font=("Arial", 22, "bold")).pack(pady=20)

        self.main_frame = ctk.CTkScrollableFrame(self, width=500, height=450)
        self.main_frame.pack(padx=20, pady=10, fill="both", expand=True)

        for name, has_slider in self.systemy_lista:
            row = SystemRow(self.main_frame, name, has_slider, self.log_event)
            row.pack(fill="x", pady=2)

    def log_event(self, name, state, value):
        status = "AKTYWNY" if state else "CZUWANIE"
        power = f" | Nastawa: {value}%" if value is not None else ""
        print(f"[{name}] Stan: {status}{power}")

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    app = App()
    app.mainloop()
