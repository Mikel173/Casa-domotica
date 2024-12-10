# usuarios_tab.py
from customtkinter import CTkFrame, CTkLabel, CTkEntry, CTkButton
from tkinter import ttk
from helpers import show_message

class UsuariosTab:
    def __init__(self, parent, db_manager):
        self.parent = parent
        self.db_manager = db_manager

    def build_tab(self, tab):
        usuarios_frame = CTkFrame(tab, fg_color="white")
        usuarios_frame.pack(fill="both", expand=True, padx=10, pady=10)

        usuarios_label = CTkLabel(usuarios_frame, text="Listado de Usuarios", text_color="black", font=("", 18, "bold"))
        usuarios_label.pack(pady=10)

        self.usuarios_tree = ttk.Treeview(usuarios_frame, columns=("ID", "Nombre", "Correo"), show="headings")
        self.usuarios_tree.heading("ID", text="ID")
        self.usuarios_tree.heading("Nombre", text="Nombre")
        self.usuarios_tree.heading("Correo", text="Correo")
        self.usuarios_tree.pack(fill="both", expand=True, pady=10)
        self.usuarios_tree.bind("<<TreeviewSelect>>", lambda e: self.usuario_seleccionado())

        self.actualizar_tabla_usuarios()

        # Botones Usuarios
        botones_usuarios_frame = CTkFrame(usuarios_frame, fg_color="white")
        botones_usuarios_frame.pack(pady=10)

        self.agregar_usuario_btn = CTkButton(botones_usuarios_frame, text="Agregar Usuario", command=self.agregar_usuario)
        self.modificar_usuario_btn = CTkButton(botones_usuarios_frame, text="Modificar Usuario", command=self.modificar_usuario)
        self.eliminar_usuario_btn = CTkButton(botones_usuarios_frame, text="Eliminar Usuario", command=self.eliminar_usuario)

        self.agregar_usuario_btn.grid(row=0, column=0, padx=5)
        self.modificar_usuario_btn.grid(row=0, column=1, padx=5)
        self.eliminar_usuario_btn.grid(row=0, column=2, padx=5)

        # Edición Usuario
        self.edicion_usuario_frame = CTkFrame(usuarios_frame, fg_color="#D9D9D9", corner_radius=10)
        self.edicion_usuario_frame.pack(pady=10, fill="x")
        self.edicion_usuario_frame.pack_forget()

        self.edicion_usuario_title = CTkLabel(self.edicion_usuario_frame, text="Agregar/Modificar Usuario", text_color="black", font=("", 16, "bold"))
        self.edicion_usuario_title.pack(pady=10)

        form_usuario_frame = CTkFrame(self.edicion_usuario_frame, fg_color="#D9D9D9")
        form_usuario_frame.pack(pady=10, padx=10, fill="x")

        CTkLabel(form_usuario_frame, text="Nombre:", text_color="black").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.usuario_nombre_input = CTkEntry(form_usuario_frame)
        self.usuario_nombre_input.grid(row=0, column=1, padx=5, pady=5)

        CTkLabel(form_usuario_frame, text="Correo:", text_color="black").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.usuario_correo_input = CTkEntry(form_usuario_frame)
        self.usuario_correo_input.grid(row=1, column=1, padx=5, pady=5)

        CTkLabel(form_usuario_frame, text="Contraseña:", text_color="black").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.usuario_password_input = CTkEntry(form_usuario_frame, show="*")
        self.usuario_password_input.grid(row=2, column=1, padx=5, pady=5)

        btns_edicion_usuario_frame = CTkFrame(self.edicion_usuario_frame, fg_color="#D9D9D9")
        btns_edicion_usuario_frame.pack(pady=10)

        self.guardar_usuario_btn = CTkButton(btns_edicion_usuario_frame, text="Guardar", command=self.guardar_usuario)
        self.cancelar_usuario_btn = CTkButton(btns_edicion_usuario_frame, text="Cancelar", command=self.cancelar_edicion_usuario)

        self.guardar_usuario_btn.grid(row=0, column=0, padx=10)
        self.cancelar_usuario_btn.grid(row=0, column=1, padx=10)

    def actualizar_tabla_usuarios(self):
        for i in self.usuarios_tree.get_children():
            self.usuarios_tree.delete(i)
        try:
            usuarios = self.db_manager.obtener_usuarios()
            for usr in usuarios:
                self.usuarios_tree.insert("", "end", values=(usr[0], usr[1], usr[2]))
        except Exception as e:
            self.show_message("Error", f"No se pudo actualizar la tabla de usuarios:\n{e}")

    def agregar_usuario(self):
        self.edicion_usuario_title.configure(text="Agregar Usuario")
        self.usuario_nombre_input.delete(0, "end")
        self.usuario_correo_input.delete(0, "end")
        self.usuario_password_input.delete(0, "end")
        self.parent.usuario_mode = "add"
        self.parent.selected_usuario_id = None
        self.edicion_usuario_frame.pack(pady=10, fill="x")

    def modificar_usuario(self):
        selected = self.usuarios_tree.selection()
        if not selected:
            self.show_message("Seleccionar Usuario", "Por favor, seleccione un usuario para modificar.")
            return

        item = self.usuarios_tree.item(selected[0])
        vals = item["values"]
        id_usuario = vals[0]
        nombre = vals[1]
        correo = vals[2]

        self.edicion_usuario_title.configure(text="Modificar Usuario")
        self.usuario_nombre_input.delete(0, "end")
        self.usuario_nombre_input.insert(0, nombre)
        self.usuario_correo_input.delete(0, "end")
        self.usuario_correo_input.insert(0, correo)
        self.usuario_password_input.delete(0, "end")
        self.usuario_password_input.placeholder_text = "Dejar en blanco para no cambiar"
        self.parent.usuario_mode = "modify"
        self.parent.selected_usuario_id = id_usuario
        self.edicion_usuario_frame.pack(pady=10, fill="x")

    def eliminar_usuario(self):
        selected = self.usuarios_tree.selection()
        if not selected:
            self.show_message("Seleccionar Usuario", "Por favor, seleccione un usuario para eliminar.")
            return

        item = self.usuarios_tree.item(selected[0])
        vals = item["values"]
        id_usuario = vals[0]
        nombre = vals[1]

        confirm = CTkToplevel(self.parent)
        confirm.title("Confirmar Eliminación")
        confirm.geometry("300x150")
        confirm.resizable(False, False)
        clabel = CTkLabel(confirm, text=f"¿Eliminar el usuario '{nombre}'?")
        clabel.pack(pady=20)

        def yes():
            try:
                if self.db_manager.eliminar_usuario(id_usuario):
                    self.actualizar_tabla_usuarios()
            except Exception as e:
                self.show_message("Error", f"No se pudo eliminar el usuario:\n{e}")
            confirm.destroy()

        def no():
            confirm.destroy()

        yes_btn = CTkButton(confirm, text="Sí", command=yes)
        yes_btn.pack(side="left", padx=30, pady=10)
        no_btn = CTkButton(confirm, text="No", command=no)
        no_btn.pack(side="right", padx=30, pady=10)

    def guardar_usuario(self):
        nombre = self.usuario_nombre_input.get().strip()
        correo = self.usuario_correo_input.get().strip()
        password = self.usuario_password_input.get().strip()

        if not nombre or not correo:
            self.show_message("Campos Vacíos", "Nombre y correo son obligatorios.")
            return

        try:
            if self.parent.usuario_mode == "add":
                if not password:
                    self.show_message("Contraseña Vacía", "La contraseña es obligatoria para agregar un usuario.")
                    return
                success = self.db_manager.agregar_usuario(nombre, correo, password)
            elif self.parent.usuario_mode == "modify":
                if password:
                    success = self.db_manager.modificar_usuario(self.parent.selected_usuario_id, nombre, correo, password)
                else:
                    success = self.db_manager.modificar_usuario(self.parent.selected_usuario_id, nombre, correo)
            else:
                self.show_message("Modo Desconocido", "Modo de operación desconocido.")
                return

            if success:
                self.actualizar_tabla_usuarios()
                self.edicion_usuario_frame.pack_forget()
                self.parent.usuario_mode = None
                self.parent.selected_usuario_id = None
                self.usuario_nombre_input.delete(0, "end")
                self.usuario_correo_input.delete(0, "end")
                self.usuario_password_input.delete(0, "end")
                self.usuario_password_input.placeholder_text = ""
        except Exception as e:
            self.show_message("Error", f"No se pudo guardar el usuario:\n{e}")

    def cancelar_edicion_usuario(self):
        self.edicion_usuario_frame.pack_forget()
        self.parent.usuario_mode = None
        self.parent.selected_usuario_id = None
        self.usuario_nombre_input.delete(0, "end")
        self.usuario_correo_input.delete(0, "end")
        self.usuario_password_input.delete(0, "end")
        self.usuario_password_input.placeholder_text = ""

    def usuario_seleccionado(self):
        # Opcional
        pass

    def show_message(self, title, message):
        show_message(self.parent, title, message)
