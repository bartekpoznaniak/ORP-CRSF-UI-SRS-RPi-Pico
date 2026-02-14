import customtkinter as ctk
from PIL import Image
import os

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("500x500")
        self.title("Przełącznik obrazów")

        # Ścieżka do folderu - upewnij się, że pliki tam są
        img_folder = "/home/bartek/Pictures"
        
        # Ładowanie obrazów
        img_on_path = os.path.join(img_folder, "on1.png")
        img_off_path = os.path.join(img_folder, "off1.png")
        
        self.img_on = ctk.CTkImage(light_image=Image.open(img_on_path).convert("RGBA"), size=(60, 30))
        self.img_off = ctk.CTkImage(light_image=Image.open(img_off_path).convert("RGBA"), size=(60, 30))

        self.is_on = True
        bg_color = self.cget("fg_color") 
        # Utworzenie przycisku
        self.btn = ctk.CTkButton(
            self,
            image=self.img_on,
            text="",                # Brak tekstu dla przełącznika
            width=30,
            height=15,
            fg_color=bg_color,
            hover_color=bg_color,      # Brak zmiany koloru po najechaniu
            hover=False,
            border_width=0,         # Usuwamy ramkę CustomTkinter
            command=self.toggle_button
        )
        self.btn.pack(pady=20)

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
