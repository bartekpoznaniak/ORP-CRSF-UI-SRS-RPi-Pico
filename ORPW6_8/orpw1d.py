import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw, ImageFont


class SmoothToggleSwitch(tk.Canvas):
    def __init__(self, parent, width=60, height=30, command=None, text_label=""):
        # Pobieranie koloru tła (obsługa CustomTkinter)
        raw_bg = parent.cget("fg_color")
        if isinstance(raw_bg, (list, tuple)) or " " in str(raw_bg):
            bg_color = parent._apply_appearance_mode(raw_bg)
        elif raw_bg == "transparent":
            theme_color = ctk.ThemeManager.theme["CTkFrame"]["fg_color"]
            bg_color = parent._apply_appearance_mode(theme_color)
        else:
            bg_color = raw_bg

        super().__init__(parent, width=width, height=height, highlightthickness=0, bg=bg_color, cursor="hand2")
        self.width, self.height, self.command, self.text_label = width, height, command, text_label
        self.state = False
        
        # 1. Przygotowanie czcionki (raz dla obu stanów)
        self.font = self._load_best_font()
        
        # 2. Generowanie obrazów
        self.img_on = self._create_switch_image(True)
        self.img_off = self._create_switch_image(False)
        self.display_img = self.create_image(0, 0, anchor="nw", image=self.img_off)
        self.bind("<Button-1>", self.toggle)

    def _load_best_font(self):
        """Próbuje załadować czcionkę systemową, która reaguje na rozmiar."""
        scale = 4
        target_size = int(self.height * scale * 0.28) # Optymalna wielkość
        
        # Lista popularnych ścieżek do czcionek Bold
        font_names = [
            "arialbd.ttf",          # Windows
            "DejaVuSans-Bold.ttf",  # Linux
            "Verdana_Bold.ttf",     # Alternatywa
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", # Linux Path
            "Arial Bold.ttf"        # macOS
        ]
        
        for name in font_names:
            try:
                return ImageFont.truetype(name, target_size)
            except:
                continue
        return ImageFont.load_default() # Ostateczność (napisy mogą być małe)

    def _create_switch_image(self, state):
        scale = 4
        w, h = self.width * scale, self.height * scale
        bg_color = "#2e7d32" if state else "#d32f2f"
        
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Tło
        draw.rounded_rectangle([0, 0, w, h], radius=h//2, fill=bg_color)
        
        # Tekst
        text = "ON" if state else "OFF"
        
        # Pobieranie dokładnych wymiarów tekstu (bounding box)
        bbox = draw.textbbox((0, 0), text, font=self.font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]

        # Centrowanie w pionie i poziomie dla odpowiedniej połówki
        if state:
            # ON - lewa strona (środek obszaru od 0 do w-h)
            tx = (w - h) / 2 - tw / 2
        else:
            # OFF - prawa strona (środek obszaru od h do w)
            tx = h + (w - h) / 2 - tw / 2
            
        ty = (h / 2) - (th / 2) - bbox[1] # Korekta o offset góry fontu

        draw.text((tx, ty), text, fill="white", font=self.font)

        # Kółko (uchwyt)
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
    """Klasa reprezentująca pojedynczy wiersz: Label + Switch + opcjonalnie Slider"""
    def __init__(self, parent, name, has_slider=False, command=None):
        super().__init__(parent, fg_color="transparent")
        self.name = name
        self.command = command

        # Układ: Kolumna 0 (Nazwa), Kolumna 1 (Suwak), Kolumna 2 (Switch)
        self.grid_columnconfigure(1, weight=1)

        self.label = ctk.CTkLabel(self, text=name, font=("Arial", 14), width=120, anchor="w")
        self.label.grid(row=0, column=0, padx=(10, 20), pady=10)

        self.slider = None
        if has_slider:
            self.slider = ctk.CTkSlider(self, from_=0, to=100, width=150, state="disabled")
            self.slider.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
            self.slider.set(0)

        self.switch = SmoothToggleSwitch(self, width=60, height=30, command=self._on_toggle)
        self.switch.grid(row=0, column=2, padx=10, pady=10)

    def _on_toggle(self, state):
        if self.slider:
            self.slider.configure(state="normal" if state else "disabled")
        if self.command:
            val = self.slider.get() if self.slider else None
            self.command(self.name, state, val)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("500x600")
        self.title("System Bojowy 2026")

        # LISTA KONFIGURACYJNA: (Nazwa, Czy ma suwak)
        self.config_systemow = [
            ("Radar", False),
            ("Wyrzutnia", True),
            ("Torpedy", True),
            ("Osłony", True),
            ("Zasilanie", False)
        ]

        ctk.CTkLabel(self, text="KONSOLA OPERATORA", font=("Arial", 22, "bold")).pack(pady=20)

        self.main_frame = ctk.CTkScrollableFrame(self, width=450, height=400)
        self.main_frame.pack(padx=20, pady=10, fill="both", expand=True)

        self.refresh_ui()

    def refresh_ui(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        for name, has_slider in self.config_systemow:
            row = SystemRow(self.main_frame, name, has_slider, self.handle_update)
            row.pack(fill="x", pady=2)

    def handle_update(self, name, state, value):
        status = "WŁĄCZONY" if state else "WYŁĄCZONY"
        val_str = f" | Moc: {int(value)}%" if value is not None else ""
        print(f"Update: {name} -> {status}{val_str}")

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    app = App()
    app.mainloop()
