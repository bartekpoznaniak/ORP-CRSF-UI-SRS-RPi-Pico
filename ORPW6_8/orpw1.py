import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw, ImageFont

class SmoothToggleSwitch(tk.Canvas):
    def __init__(self, parent, width=80, height=34, command=None, text_label=""):
        # 1. Rozwiązanie problemu kolorów "gray86 gray17" i "transparent"
        raw_bg = parent.cget("fg_color")
        
        # Jeśli kolor jest parą dla trybu jasnego/ciemnego, wybierz jeden właściwy
        if isinstance(raw_bg, (list, tuple)) or " " in str(raw_bg):
            bg_color = parent._apply_appearance_mode(raw_bg)
        elif raw_bg == "transparent":
            # Jeśli transparent, pobierz standardowy kolor tła z motywu CTK
            theme_color = ctk.ThemeManager.theme["CTkFrame"]["fg_color"]
            bg_color = parent._apply_appearance_mode(theme_color)
        else:
            bg_color = raw_bg

        # 2. Inicjalizacja Canvas
        super().__init__(parent, width=width, height=height,
                         highlightthickness=0, bg=bg_color, cursor="hand2")

        self.width = width
        self.height = height
        self.command = command
        self.text_label = text_label
        self.state = False

        # 3. Generowanie obrazów wektorowych
        self.img_on = self._create_switch_image(True)
        self.img_off = self._create_switch_image(False)

        # 4. Wyświetlenie początkowego stanu
        self.display_img = self.create_image(0, 0, anchor="nw", image=self.img_off)

        # 5. Obsługa kliknięcia
        self.bind("<Button-1>", self.toggle)

    def _create_switch_image(self, state):
        scale = 4
        w, h = self.width * scale, self.height * scale
        radius = h // 2
        bg_color = "#2e7d32" if state else "#d32f2f"

        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle([0, 0, w, h], radius=radius, fill=bg_color)

        font_size = int(h * 0.20)
        try:
            # Próba załadowania czcionki pogrubionej
            font = ImageFont.truetype("arialbd.ttf", font_size)
        except:
            try:
                # Ścieżka dla systemów Linux
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
            except:
                font = ImageFont.load_default()

        text = "ON" if state else "OFF"
        text_x = w * 0.30 if state else w * 0.70
        draw.text((text_x, h/2), text, fill="white", font=font, anchor="mm")

        margin = 3 * scale
        d = h - 2 * margin
        x_start = (w - h + margin) if state else margin
        draw.ellipse([x_start, margin, x_start + d, margin + d], fill="white")

        img = img.resize((self.width, self.height), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(img)

    def toggle(self, event=None):
        self.state = not self.state
        self.itemconfig(self.display_img, image=self.img_on if self.state else self.img_off)
        if self.command:
            self.command(self.state, self.text_label)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("400x650")
        self.title("Zintegrowany Przełącznik")

        # Nagłówek
        self.label_title = ctk.CTkLabel(self, text="Panel Sterowania", font=("Arial", 20, "bold"))
        self.label_title.pack(pady=20)

        # Kontener na przyciski (z Twojego Kodu 1)
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=10, padx=20, fill="x")

        # Pętla generująca sekcje (z Twojego Kodu 1)
        for i in range(5):
            section_name = f"sekcja {i+1}"
            
            # Etykieta sekcji
            lbl = ctk.CTkLabel(button_frame, text=section_name, font=("Arial", 14))
            lbl.grid(row=i, column=0, pady=10, padx=20, sticky="w")

            # Twój rysowany przełącznik (z Twojego Kodu 2)
            sw = SmoothToggleSwitch(
                button_frame, 
                width=60, 
                height=34, 
                text_label=section_name,
                command=self.handle_toggle
            )
            sw.grid(row=i, column=1, pady=10, padx=20, sticky="e")
            
            # Konfiguracja rozciągania kolumn
            button_frame.grid_columnconfigure(0, weight=1)

        # --- SEKCJA SUWAKA (z Twojego Kodu 1) ---
        self.zmienna_suwaka = 0

        self.label_wartosc = ctk.CTkLabel(self, text="Wartość suwaka: 0")
        self.label_wartosc.pack(pady=(30, 5))

        self.suwak = ctk.CTkSlider(self, from_=0, to=100, command=self.update_slider)
        self.suwak.pack(pady=10, padx=40, fill="x")
        self.suwak.set(0)

    def handle_toggle(self, state, name):
        """Metoda raportująca stan przełączników"""
        stan_tekst = "ON" if state else "OFF"
        print(f"Stan: {stan_tekst} dla przycisku: {name}")

    def update_slider(self, value):
        """Metoda raportująca stan suwaka"""
        self.zmienna_suwaka = int(value)
        self.label_wartosc.configure(text=f"Wartość suwaka: {self.zmienna_suwaka}")
        print(f"Suwak ustawiony na: {self.zmienna_suwaka}")

if __name__ == "__main__":
    # Ustawienie motywu (możesz zmienić na "light")
    ctk.set_appearance_mode("dark") 
    app = App()
    app.mainloop()
