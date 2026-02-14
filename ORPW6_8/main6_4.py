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
        
        size = (80, 40)
        self.img_on = ctk.CTkImage(light_image=Image.open(img_on_path).convert("RGBA"), size=size)
        self.img_off = ctk.CTkImage(light_image=Image.open(img_off_path).convert("RGBA"), size=size)

        self.bg_color = self.cget("fg_color") 
        self.button_states = {} 

        for i in range(4):
            btn = ctk.CTkButton(
                self,
                image=self.img_on,
                text=f"Przycisk {i+1}", 
                width=150,
                height=40,
                compound="right", 
                fg_color=self.bg_color,
                hover_color=self.bg_color,
                hover=False,
                border_width=0, # Upewniamy się, że to jest 0
            )
            
            btn.configure(command=lambda current_button=btn: self.toggle_button(current_button))

            # Ustawiamy pady na 0 i dodajemy anchor='center'
            btn.pack(pady=0, anchor='center') 
            
            self.button_states[btn] = True 

    def toggle_button(self, button_object):
        if self.button_states[button_object]:
            button_object.configure(image=self.img_off)
            self.button_states[button_object] = False
            print(f"Stan: OFF dla przycisku: {button_object.cget('text')}")
        else:
            button_object.configure(image=self.img_on)
            self.button_states[button_object] = True
            print(f"Stan: ON dla przycisku: {button_object.cget('text')}")

if __name__ == "__main__":
    app = App()
    app.mainloop()
