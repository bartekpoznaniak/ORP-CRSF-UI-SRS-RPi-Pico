import customtkinter as ctk
from PIL import Image
import os

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("500x500")
        self.title("Podgląd obrazu")

	# moj pil_image = Image.open("on.png").convert("RGBA") # Wymuś tryb przezroczystości
	# moj my_image = ctk.CTkImage(light_image=pil_image, size=(300, 300))
        
	

	# 1. Ścieżka do pliku (użyj ścieżki bezwzględnej dla bezpieczeństwa)
        img_path = os.path.join("/home/bartek/Pictures", "on1.png")

        # 2. Otwarcie obrazu za pomocą Pillow
        pil_image = Image.open(img_path).convert("RGBA")

        # 3. Utworzenie obiektu CTkImage
        # Możesz podać dwie wersje (light i dark) lub jedną dla obu
        my_image = ctk.CTkImage(light_image=pil_image,
                                dark_image=pil_image,
                                size=(60, 30)) # Tutaj ustawiasz wymiary wyświetlania

        # 4. Umieszczenie obrazu w Label (etykiecie)
        self.label = ctk.CTkLabel(self, image=my_image, text="") 
        self.label.pack(pady=20)

if __name__ == "__main__":
    app = App()
    app.mainloop()
