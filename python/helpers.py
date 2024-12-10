# helpers.py
from customtkinter import CTkToplevel, CTkLabel, CTkButton

def show_message(parent, title, message):
    top = CTkToplevel(parent)
    top.title(title)
    top.geometry("300x150")
    top.resizable(False, False)
    top.attributes("-topmost", True)  # Mantiene la ventana de mensaje por encima

    label = CTkLabel(top, text=message, font=("", 14))
    label.pack(pady=20)

    btn = CTkButton(top, text="OK", command=top.destroy)
    btn.pack(pady=10)
