import customtkinter as ctk

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("500x500")
        self.title("Dynamiczny Przełącznik Warstwowy")

        self.is_on = True

        # 1. Główny kontener (tło przełącznika)
        self.switch_frame = ctk.CTkFrame(self, width=120, height=60, corner_radius=30, fg_color="green")
        self.switch_frame.pack(pady=50)
        # Używamy place() wewnątrz frame, aby precyzyjnie pozycjonować elementy
        self.switch_frame.pack_propagate(False) # Zapobiega zmianie rozmiaru frame przez jego zawartość

        # 2. Etykieta z tekstem (statyczna pozycja)
        self.text_label = ctk.CTkLabel(self.switch_frame, text="ON", font=("Arial", 20, "bold"), text_color="white")
        # Pozycjonujemy tekst: x=85 (na prawo), y=0.5 (środek pionowo)
        self.text_label.place(relx=0.85, rely=0.5, anchor=ctk.CENTER) 

        # 3. Ruchome kółko (przycisk)
        self.handle_button = ctk.CTkButton(self.switch_frame, text="", width=50, height=50, corner_radius=25, 
                                           fg_color="white", hover_color="lightgray", border_width=0,
                                           command=self.toggle_switch)
        # Pozycjonujemy kółko: początkowo po lewej (x=5)
        self.handle_button.place(x=5, rely=0.5, anchor=ctk.CENTER)
        
        self.handle_position_on = 5
        self.handle_position_off = 115

    def toggle_switch(self):
        if self.is_on:
            # Przesuń kółko na prawo, zmień kolor tła i tekst
            self.handle_button.place(x=self.handle_position_off)
            self.switch_frame.configure(fg_color="gray")
            self.text_label.configure(text="OFF", text_color="black")
            print("Stan: OFF")
            self.is_on = False
        else:
            # Przesuń kółko na lewo, zmień kolor tła i tekst
            self.handle_button.place(x=self.handle_position_on)
            self.switch_frame.configure(fg_color="green")
            self.text_label.configure(text="ON", text_color="white")
            print("Stan: ON")
            self.is_on = True

if __name__ == "__main__":
    app = App()
    app.mainloop()
