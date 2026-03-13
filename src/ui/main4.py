import customtkinter as ctk
from PIL import Image
import os


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("500x500")
        self.title("Przełącznik obrazów")
        self.is_on = False  # <-- DODAJ TO w __init__

        # Ścieżka do folderu
        img_folder = "/home/bartek/Pictures"

        # 1. Wczytanie obu obrazów
        img_on_path = os.path.join(img_folder, "on1.png")
        img_off_path = os.path.join(img_folder, "off1.png")

        self.img_on = ctk.CTkImage(light_image=Image.open(
            img_on_path).convert("RGBA"), size=(60, 30))
        self.img_off = ctk.CTkImage(light_image=Image.open(
            img_off_path).convert("RGBA"), size=(60, 30))

        # 2. Zmienna stanu
        self.is_on = True

        # 3. Utworzenie przycisku

        self.btn = ctk.CTkButton(self,
                         image=self.img_on,
                         text="Twoj Tekst",
                         border_width=0,      # Odpowiednik highlightthickness
                         border_color="#FF0000", # Odpowiednik highlightcolor
                         fg_color="transparent"
                         )
        self.btn.pack(pady=20)

    def toggle_button(self):
        # 4. Logika zmiany obrazu
        if self.is_on:
            self.btn.configure(image=self.img_off)
            self.is_on = False
            print("Stan: OFF")
        else:
            self.btn.configure(image=self.img_on)
            self.is_on = True
            print("Stan: ON")


if __name__ == "__main__":
    app = App()
    app.mainloop()
