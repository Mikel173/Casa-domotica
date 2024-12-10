from customtkinter import *
from PIL import Image

class LoginFrame(CTkFrame):
    def __init__(self, parent, db_manager):
        super().__init__(parent, fg_color="white")
        self.parent = parent
        self.db_manager = db_manager

        # Crear un frame contenedor para centrar todo el contenido
        container = CTkFrame(self, fg_color="white")
        container.place(relx=0.5, rely=0.5, anchor="center")  # Centrado en la ventana

        bg_img = CTkImage(dark_image=Image.open("bg1.jpg"), size=(500, 500))
        bg_lab = CTkLabel(container, image=bg_img, text="", fg_color="white")
        bg_lab.grid(row=0, column=0, padx=20)

        frame1 = CTkFrame(container, fg_color="#D9D9D9", bg_color="white", height=350, width=300, corner_radius=20)
        frame1.grid(row=0, column=1, padx=40)

        title = CTkLabel(frame1, text="Bienvenido \nInicia Sesion", text_color="black", font=("",35,"bold"))
        title.grid(row=0, column=0, sticky="nw", pady=30, padx=10)

        self.usrname_entry = CTkEntry(frame1, text_color="white", placeholder_text="Username or Email",
                                      fg_color="black", placeholder_text_color="white",
                                      font=("",16,"bold"), width=200, corner_radius=15, height=45)
        self.usrname_entry.grid(row=1, column=0, sticky="nwe", padx=30)

        self.passwd_entry = CTkEntry(frame1, text_color="white", placeholder_text="Password", fg_color="black",
                                     placeholder_text_color="white", font=("",16,"bold"), width=200,
                                     corner_radius=15, height=45, show="*")
        self.passwd_entry.grid(row=2, column=0, sticky="nwe", padx=30, pady=20)

        cr_acc = CTkLabel(frame1, text="Crear Cuenta", text_color="black", cursor="hand2", font=("",15))
        cr_acc.grid(row=3, column=0, sticky="w", pady=20, padx=40)
        cr_acc.bind("<Button-1>", lambda e: self.parent.show_register_frame())

        l_btn = CTkButton(frame1, text="Login", font=("",15,"bold"), height=40, width=60, fg_color="#0085FF",
                          cursor="hand2", corner_radius=15, command=self.login_action)
        l_btn.grid(row=3, column=0, sticky="ne", pady=20, padx=35)

    def login_action(self):
        user_or_email = self.usrname_entry.get().strip()
        password = self.passwd_entry.get().strip()

        if not user_or_email or not password:
            self.show_message("Campos Vacíos", "Por favor, ingrese usuario/correo y contraseña.")
            return

        success, _ = self.db_manager.verify_user_login_any(user_or_email, password)
        if success:
            self.show_message("Bienvenido", "¡Inicio de sesión exitoso!")
            self.parent.show_dashboard()
        else:
            self.show_message("Error de Autenticación", "Usuario/Correo o contraseña incorrectos.")

    def show_message(self, title, message):
        top = CTkToplevel(self)
        top.title(title)
        top.geometry("300x150")
        label = CTkLabel(top, text=message, font=("",14))
        label.pack(pady=20)
        btn = CTkButton(top, text="OK", command=top.destroy)
        btn.pack(pady=10)
