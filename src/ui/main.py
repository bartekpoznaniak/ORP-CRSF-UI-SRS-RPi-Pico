import tkinter as tk

def on_click():
    print("Przycisk został naciśnięty! Sterowanie działa.")

root = tk.Tk()
root.title("RC Boat Control")
root.geometry("300x200")

label = tk.Label(root, text="Panel Sterowania Okrętem", pady=20)
label.pack()

button = tk.Button(root, text="Testuj Silnik", command=on_click)
button.pack()

print("Uruchamiam interfejs graficzny...")
root.mainloop()
