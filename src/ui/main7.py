import tkinter as tk
from PIL import Image, ImageTk, ImageDraw, ImageFont

class SmoothToggleSwitch(tk.Canvas):
    def __init__(self, parent, width=80, height=34, command=None):
        # 1. Inicjalizacja Canvas (Podstawa przycisku)
        super().__init__(parent, width=width, height=height,
                         highlightthickness=0, bg=parent['bg'])

        self.width = width
        self.height = height
        self.command = command
        self.state = False

        # 2. Generowanie obrazów (Z Twoimi oryginalnymi ustawieniami)
        self.img_on = self._create_switch_image(True)
        self.img_off = self._create_switch_image(False)

        # 3. Wyświetlenie początkowego obrazu
        self.display_img = self.create_image(0, 0, anchor="nw", image=self.img_off)

        # 4. Obsługa kliknięcia
        self.bind("<Button-1>", self.toggle)

    def _create_switch_image(self, state):
        scale = 4
        w, h = self.width * scale, self.height * scale
        radius = h // 2
        bg_color = "#2e7d32" if state else "#d32f2f"

        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle([0, 0, w, h], radius=radius, fill=bg_color)

        # USTALONA DUŻA CZCIONKA (0.70)
        font_size = int(h * 0.20)

        try:
            font = ImageFont.truetype("arialbd.ttf", font_size)
        except:
            try:
                # Linux path
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
            except:
                font = ImageFont.load_default()

        text = "ON" if state else "OFF"
        text_x = w * 0.30 if state else w * 0.70
        draw.text((text_x, h/2), text, fill="white", font=font, anchor="mm")

        # Rysowanie białego kółka
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
            self.command(self.state)

# --- KLASA KONTENERA (ZAKONTENEROWANIE OPISU I PRZYCISKU) ---
class LabeledSwitch(tk.Frame):
    def __init__(self, parent, label_text, width=80, height=34):
        super().__init__(parent, bg=parent['bg'])

        # Tworzymy Twój oryginalny suwak wewnątrz ramki
        self.switch = SmoothToggleSwitch(self, width=width, height=height)
        self.switch.pack(side="left")

        # Dodajemy opis jako osobny widget obok (TOTALNIE ODSEPAROWANY)
        self.label = tk.Label(self, text=label_text, bg=parent['bg'],
                              font=("Arial", 11, "bold"))
        self.label.pack(side="left", padx=(10, 0))

        # Opcjonalnie: kliknięcie w napis też przełącza
        self.label.bind("<Button-1>", self.switch.toggle)

    @property
    def state(self):
        """Umożliwia łatwy dostęp do stanu: obiekt.state"""
        return self.switch.state

# --- GŁÓWNY PROGRAM ---
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Panel Sterowania 2026")
    root.geometry("450x500")
    root.configure(bg="#f0f0f0")

    # DPI Awareness dla Windows
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except: pass

    # Lista Twoich suwaków (zmienna do późniejszego wykorzystania)
    pulpit_sterowniczy = {}

    lista_funkcji = [
        "Radar Główny",
        "Oswietlenie kabiny1",
        "torpeda",
        "wyrzutnia pociskow",
        "zaslona dymna"
    ]

    # Tworzenie wielu suwaków jeden pod drugim
    for nazwa in lista_funkcji:
        # Używamy klasy LabeledSwitch, która "konteneruje" suwak i opis osobno
        row = LabeledSwitch(root, label_text=nazwa, width=45, height=28)
        row.pack(pady=10, padx=50, anchor="w")

        # Zapisujemy cały obiekt do słownika
        pulpit_sterowniczy[nazwa] = row

    # Przykładowa funkcja sprawdzająca stan zmiennych
    def sprawdz_ustawienia():
        print("\n--- RAPORT SYSTEMOWY ---")
        for nazwa, obiekt in pulpit_sterowniczy.items():
            # Odczytujemy stan bezpośrednio z obiektu
            status = "AKTYWNY" if obiekt.state else "NIEAKTYWNY"
            print(f"{nazwa}: {status}")

    tk.Button(root, text="Sprawdź stan wszystkich zmiennych", command=sprawdz_ustawienia).pack(pady=30)

    root.mainloop()
