import customtkinter as ctk
from PIL import Image
import os

class App(ctk.CTk):
    def __init__(self): # <--- TO JEST METODA INIT
        super().__init__()
        self.geometry("500x700") # Zwiększyłem wysokość, żeby suwak się zmieścił
        self.title("Przełącznik obrazów")
        # ... (tutaj masz definicje ścieżek do obrazków) ...
        script_dir = os.path.dirname(os.path.abspath(__file__))
        img_on_path = os.path.join(script_dir, "on1.png")
        img_off_path = os.path.join(script_dir, "off1.png")
        size = (80, 40)
        self.img_on = ctk.CTkImage(light_image=Image.open(img_on_path).convert("RGBA"), size=size)
        self.img_off = ctk.CTkImage(light_image=Image.open(img_off_path).convert("RGBA"), size=size)
        self.bg_color = self.cget("fg_color") 
        self.button_states = {} 
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=20)
        
        for i in range(5):
            btn = ctk.CTkButton(
                button_frame,
                image=self.img_on,
                text=f"sekcja {i+1}", 
                width=150,
                height=40,
                compound="right", 
                fg_color=self.bg_color,
                hover_color=self.bg_color,
                hover=False,
                border_width=0,
            )
            btn.configure(command=lambda current_button=btn: self.toggle_button(current_button))
            btn.grid(row=i, column=0, pady=0, padx=0, ipady=0, sticky="nsew") 
            self.button_states[btn] = True 

        # --- TUTAJ DODAŁEM SUWAK (nadal wewnątrz __init__) ---
        self.zmienna_suwaka = 0
        
        self.label_wartosc = ctk.CTkLabel(self, text="Wartość: 0")
        self.label_wartosc.pack(pady=(10, 0))

        self.suwak = ctk.CTkSlider(self, from_=0, to=100, command=self.update_slider)
        self.suwak.pack(pady=10)
        self.suwak.set(0) # ustawia suwak na 0 na starcie
        # ----------------------------------------------------

    # NOWA METODA (poza __init__, ale wewnątrz klasy App)
    def update_slider(self, value):
        self.zmienna_suwaka = value
        self.label_wartosc.configure(text=f"Wartość: {int(value)}")
        print(f"Suwak ustawiony na: {value}")

    def toggle_button(self, button_object):
        # ... (Twoja dotychczasowa funkcja toggle) ...
        if self.button_states[button_object]:
            button_object.configure(image=self.img_off)
            self.button_states[button_object] = False
        else:
            button_object.configure(image=self.img_on)
            self.button_states[button_object] = True

if __name__ == "__main__":
    app = App()
    app.mainloop()
