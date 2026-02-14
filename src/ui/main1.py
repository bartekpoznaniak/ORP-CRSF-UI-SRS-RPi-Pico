import tkinter as tk

# Zmienna globalna do przechowywania stanu silnika (ON/OFF)
engine_state = False

def toggle_engine():
    global engine_state
    engine_state = not engine_state
    if engine_state:
        status_label.config(text="Status: Włączony", fg="green")
        print("Silnik WŁĄCZONY")
        # Tutaj dodasz kod do włączenia silnika na pinach GPIO
    else:
        status_label.config(text="Status: Wyłączony", fg="red")
        print("Silnik WYŁĄCZONY")
        # Tutaj dodasz kod do wyłączenia silnika na pinach GPIO

root = tk.Tk()
root.title("RC Boat Control")
root.geometry("300x250")

# Etykieta tytułowa
label = tk.Label(root, text="Panel Sterowania Okrętem", pady=20, font=("Helvetica", 14, "bold"))
label.pack()

# Etykieta statusu (zmienia kolor)
status_label = tk.Label(root, text="Status: Wyłączony", fg="red", pady=10)
status_label.pack()

# Przycisk, który wygląda jak przełącznik (używamy reliefu i włączamy/wyłączamy stan)
toggle_button = tk.Button(
    root,
    text="WŁĄCZ / WYŁĄCZ",
    command=toggle_engine,
    height=2,
    width=20,
    bg="lightgray",
    activebackground="gray",
    bd=3, # Border, żeby wyglądał mniej płasko
    relief="raised" # Podniesiony wygląd
)
toggle_button.pack(pady=20)

print("Uruchamiam interfejs graficzny...")
root.mainloop()
