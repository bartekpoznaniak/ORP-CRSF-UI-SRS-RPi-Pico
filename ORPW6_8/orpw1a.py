import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw, ImageFont

class SmoothToggleSwitch(tk.Canvas):
    def __init__(self, parent, width=80, height=34, command=None, text_label=""):
        raw_bg = parent.cget("fg_color")
        if isinstance(raw_bg, (list, tuple)) or " " in str(raw_bg):
            bg_color = parent._apply_appearance_mode(raw_bg)
        elif raw_bg == "transparent":
            theme_color = ctk.ThemeManager.theme["CTkFrame"]["fg_color"]
            bg_color = parent._apply_appearance_mode(theme_color)
        else:
            bg_color = raw_bg

        super().__init__(parent, width=width, height=height,
                         highlightthickness=0, bg=bg_color, cursor="hand2")

        self.width = width
        self.height = height
        self.command = command
        self.text_label = text_label
        self.state = False

        self.img_on = self._create_switch_image(True)
        self.img_off = self._create_switch_image(False)
        self.display_img = self.create_image(0, 0, anchor="nw", image=self.img_off)
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
            font = ImageFont.truetype("arialbd.ttf", font_size)
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
        self.geometry("400x700")
        self.title("System Bojowy")

        # 1. TWOJA LISTA ELEMENTÓW
        self.systemy = ["Radar 2", "Wyrzutnia rakiet", "Torpedy", "Tarcza", "Silniki"]

        self.label_title = ctk.CTkLabel(self, text="Panel Sterowania", font=("Arial", 20, "bold"))
        self.label_title.pack(pady=20)

        # Kontener na przełączniki
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(pady=10, padx=20, fill="x")

        # 2. GENEROWANIE PRZEŁĄCZNIKÓW Z LISTY
        self.refresh_switches()

        # Suwak
        self.zmienna_suwaka = 0
        self.label_wartosc = ctk.CTkLabel(self, text="Moc systemów: 0")
        self.label_wartosc.pack(pady=(30, 5))
        self.suwak = ctk.CTkSlider(self, from_=0, to=100, command=self.update_slider)
        self.suwak.pack(pady=10, padx=40, fill="x")
        self.suwak.set(0)

        # PRZYKŁAD DODAWANIA/USUWANIA PRZEZ KOD (DODATKOWE PRZYCISKI)
        self.btn_add = ctk.CTkButton(self, text="Dodaj System", command=lambda: self.add_system("Nowy Moduł"))
        self.btn_add.pack(pady=5)
        
        self.btn_del = ctk.CTkButton(self, text="Usuń Ostatni", command=self.remove_last_system, fg_color="gray30")
        self.btn_del.pack(pady=5)

    def refresh_switches(self):
        """Czyści i rysuje listę przełączników na nowo"""
        for widget in self.button_frame.winfo_children():
            widget.destroy()

        for i, name in enumerate(self.systemy):
            lbl = ctk.CTkLabel(self.button_frame, text=name, font=("Arial", 14))
            lbl.grid(row=i, column=0, pady=10, padx=20, sticky="w")

            sw = SmoothToggleSwitch(
                self.button_frame,
                width=60,
                height=34,
                text_label=name,
                command=self.handle_toggle
            )
            sw.grid(row=i, column=1, pady=10, padx=20, sticky="e")
        
        self.button_frame.grid_columnconfigure(0, weight=1)

    def add_system(self, name):
        """Dodaje system do listy i odświeża interfejs"""
        self.systemy.append(name)
        self.refresh_switches()

    def remove_last_system(self):
        """Usuwa ostatni system i odświeża interfejs"""
        if self.systemy:
            self.systemy.pop()
            self.refresh_switches()

    def handle_toggle(self, state, name):
        stan_tekst = "ON" if state else "OFF"
        print(f"System: {name} -> {stan_tekst}")

    def update_slider(self, value):
        self.zmienna_suwaka = int(value)
        self.label_wartosc.configure(text=f"Moc systemów: {self.zmienna_suwaka}")

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    app = App()
    app.mainloop()
