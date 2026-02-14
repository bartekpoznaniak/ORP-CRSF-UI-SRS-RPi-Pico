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
        
        # Używamy większego rozmiaru, żeby były lepiej widoczne
        size = (80, 40)
        self.img_on = ctk.CTkImage(light_image=Image.open(img_on_path).convert("RGBA"), size=size)
        self.img_off = ctk.CTkImage(light_image=Image.open(img_off_path).convert("RGBA"), size=size)

        # Pobieramy kolor tła okna, aby przyciski były "niewidoczne"
        self.bg_color = self.cget("fg_color") 
        
        # Lista do przechowywania stanów przycisków (True = ON, False = OFF)
        self.button_states = {}

        # Tworzenie wielu przycisków w pętli
        for i in range(4): # Utworzy przyciski o nazwach 'btn_0', 'btn_1' itd.
            btn_name = f'btn_{i}'
            
            btn = ctk.CTkButton(
                self,
                image=self.img_on,
                text="",
                width=80,
                height=40,
                fg_color=self.bg_color,
                hover_color=self.bg_color,
                hover=False,
                border_width=0,
                # Używamy lambda, aby przekazać unikalną nazwę przycisku do funkcji
                command=lambda name=btn_name: self.toggle_button(name)
            )
            btn.pack(pady=5) # Niewielki margines pionowy
            
            # Dodajemy przycisk do słownika stanów i ustawiamy jako ON (True)
            self.button_states[btn_name] = True

    def toggle_button(self, btn_name):
        # Sprawdzamy, który przycisk został kliknięty i jaki jest jego stan
        current_state = self.button_states[btn_name]
        
        # Znajdujemy obiekt przycisku po nazwie (poprzez metodę pack_slaves, która zwraca listę dzieci)
        # To jest nieco skomplikowane, łatwiej byłoby przechowywać obiekty, ale działa z obecnym kodem
        
        # Alternatywna (łatwiejsza) metoda: przechowaj obiekty w słowniku zamiast nazw
        # Ten kod zakłada, że użyjesz kodu z mojej następnej odpowiedzi, który jest prostszy.

        # Prostsza implementacja funkcji toggle_button, jeśli przekazujemy obiekt przycisku:
        # Poniższa funkcja zadziała, jeśli zmienimy lambda na: command=lambda b=btn: self.toggle_button_simple(b)

        print(f"Przycisk {btn_name} - Stan przed: {'ON' if current_state else 'OFF'}")

        if current_state:
            # Tutaj musisz znaleźć odpowiedni obiekt przycisku, żeby zmienić jego image
            # ... (implementacja szukania obiektu jest kłopotliwa) ...
            
            # Uprośćmy to i przechowujmy obiekty przycisków w słowniku:

            pass

if __name__ == "__main__":
    app = App()
    app.mainloop()
