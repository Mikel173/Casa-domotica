from customtkinter import *
from PIL import Image

class RegisterFrame(CTkFrame):
    def __init__(self, parent, db_manager):
        super().__init__(parent, fg_color="white")
        self.parent = parent
        self.db_manager = db_manager

        # Crear un contenedor y centrarlo en el frame principal
        container = CTkFrame(self, fg_color="white")
        container.place(relx=0.5, rely=0.5, anchor="center")

        bg_img = CTkImage(dark_image=Image.open("bg1.jpg"), size=(500, 500))
        bg_lab = CTkLabel(container, image=bg_img, text="", fg_color="white")
        bg_lab.grid(row=0, column=0)

        frame1 = CTkFrame(container, fg_color="#D9D9D9", bg_color="white", height=400, width=300, corner_radius=20)
        frame1.grid(row=0, column=1, padx=40)

        title = CTkLabel(frame1, text="Crear Nueva Cuenta", text_color="black", font=("",25,"bold"))
        title.grid(row=0, column=0, sticky="nw", pady=30, padx=10)

        self.name_entry = CTkEntry(frame1, text_color="white", placeholder_text="Nombre",
                                   fg_color="black", placeholder_text_color="white",
                                   font=("",16,"bold"), width=200, corner_radius=15, height=45)
        self.name_entry.grid(row=1, column=0, sticky="nwe", padx=30, pady=(10,0))

        self.email_entry = CTkEntry(frame1, text_color="white", placeholder_text="Correo", fg_color="black",
                                    placeholder_text_color="white", font=("",16,"bold"), width=200,
                                    corner_radius=15, height=45)
        self.email_entry.grid(row=2, column=0, sticky="nwe", padx=30, pady=(20,0))

        self.passwd_entry = CTkEntry(frame1, text_color="white", placeholder_text="Contraseña", fg_color="black",
                                     placeholder_text_color="white", font=("",16,"bold"), width=200,
                                     corner_radius=15, height=45, show="*")
        self.passwd_entry.grid(row=3, column=0, sticky="nwe", padx=30, pady=(20,0))

        # Botones
        btn_frame = CTkFrame(frame1, fg_color="#D9D9D9")
        btn_frame.grid(row=4, column=0, pady=30)

        reg_btn = CTkButton(btn_frame, text="Registrar", font=("",15,"bold"), height=40, width=60, fg_color="#0085FF",
                            cursor="hand2", corner_radius=15, command=self.register_action)
        reg_btn.grid(row=0, column=0, padx=20)

        back_btn = CTkLabel(btn_frame, text="Volver a Iniciar Sesión", text_color="black", cursor="hand2", font=("",15))
        back_btn.grid(row=0, column=1, padx=20)
        back_btn.bind("<Button-1>", lambda e: self.parent.show_login_frame())

    def register_action(self):
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.passwd_entry.get().strip()

        if not name or not email or not password:
            self.show_message("Campos Vacíos", "Por favor, complete todos los campos.")
            return

        try:
            self.db_manager.agregar_usuario(name, email, password)
            self.show_message("Registro Exitoso", "El usuario ha sido registrado con éxito.")
            # Limpia campos
            self.name_entry.delete(0,"end")
            self.email_entry.delete(0,"end")
            self.passwd_entry.delete(0,"end")
            # Regresa al login
            self.parent.show_login_frame()
        except Exception as e:
            self.show_message("Error", f"No se pudo registrar el usuario:\n{e}")

    def show_message(self, title, message):
        top = CTkToplevel(self)
        top.title(title)
        top.geometry("300x150")
        label = CTkLabel(top, text=message, font=("",14))
        label.pack(pady=20)
        btn = CTkButton(top, text="OK", command=top.destroy)
        btn.pack(pady=10)
