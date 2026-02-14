import customtkinter as ctk
from PIL import Image
import os

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("500x500")
        self.title("Przełącznik obrazów")

        img_folder = "/home/bartek/Pictures"

        img_on_path = os.path.join(img_folder, "on1.png")
        img_off_path = os.path.join(img_folder, "off1.png")
        self.img_on = ctk.CTkImage(light_image=Image.open(img_on_path).convert("RGBA"), size=(60, 30))
        self.img_off = ctk.CTkImage(light_image=Image.open(img_off_path).convert("RGBA"), size=(60, 30))

        self.is_on = True

        # 3. Utworzenie przycisku z niestandardową ramką fokusu

        self.btn = ctk.CTkButton(self,
                                 image=self.img_on,
                                 text="Twój Tekst",
                                 border_width=2,          # Zamiast highlightthickness
                                 border_color="#FF0000",  # Zamiast highlightcolor
                                 # Usuń całkowicie highlightbackground
                                 command=self.toggle_button)
        self.btn.pack(pady=20)
"""
        self.btn = ctk.CTkButton(self,
                                 image=self.img_on,
                                 text="",
                                 command=self.toggle_button,
                                 fg_color="transparent",  # Usuwa tło CustomTkinter
                                 hover_color=None,
                                 width=60,
                                 height=30,
                                 highlightthickness=2,    # <-- Ustawia grubość ramki (np. na 2 piksele)
                                 highlightcolor="#FF0000", # <-- Ustawia kolor ramki (np. na czerwony, możesz użyć hex lub nazwy)
                                 highlightbackground=self.cget('bg')) # <-- Kolor ramki, gdy przycisk NIE jest aktywny (ukrywa ją w stanie spoczynku)
"""
        

def toggle_button(self):
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
