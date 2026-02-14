import customtkinter as ctk

# Ustawienie wyglądu (opcjonalnie: "System", "Light", "Dark")
ctk.set_appearance_mode("System")
# Ustawienie domyślnego motywu kolorystycznego
ctk.set_default_color_theme("blue")

def switch_event():
    # Pobierz aktualny stan przełącznika (On/Off lub 1/0)
    state = switch_var.get()
    if state == "On":
        status_label.configure(text="Status: Włączony", text_color="green")
        print("Silnik WŁĄCZONY")
        # Tutaj dodasz kod do włączenia silnika na pinach GPIO
    else:
        status_label.configure(text="Status: Wyłączony", text_color="red")
        print("Silnik WYŁĄCZONY")
        # Tutaj dodasz kod do wyłączenia silnika na pinach GPIO

# Tworzenie głównego okna
root = ctk.CTk()
root.title("RC Boat Control")
root.geometry("300x250")

# Etykieta tytułowa
label = ctk.CTkLabel(root, text="Panel Sterowania Okrętem", font=("Helvetica", 16, "bold"))
label.pack(pady=20)

# Etykieta statusu
status_label = ctk.CTkLabel(root, text="Status: Wyłączony", text_color="red", font=("Helvetica", 12))
status_label.pack(pady=10)

# Zmienna, która przechowuje stan przełącznika ("On" lub "Off")
switch_var = ctk.StringVar(value="Off")

# Tworzenie nowoczesnego przełącznika (suwaczka)
engine_switch = ctk.CTkSwitch(
    master=root,
    text="WŁĄCZ / WYŁĄCZ",
    command=switch_event,
    variable=switch_var,
    onvalue="On",
    offvalue="Off",
    switch_width=40,        # Szerokosc suwaka
    switch_height=26,       # Wyższy suwak
    corner_radius=100,      # Maksymalne zaokrąglenie (jak na obrazku)
    fg_color="red",         # Kolor tła, gdy jest WYŁĄCZONY
    progress_color="green", # Kolor, gdy jest WŁĄCZONY
    button_color="white",   # Biały guziczek
    button_hover_color="lightgray",
    border_color="gray",    # Cienka ramka wokół całości
    border_width=4,
    font=("Arial", 14, "bold"),
    text_color="black",
    # button_length=20
)
engine_switch.pack(pady=20)

print("Uruchamiam interfejs graficzny...")
root.mainloop()
