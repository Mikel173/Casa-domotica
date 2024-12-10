from customtkinter import CTkFrame, CTkLabel, CTkEntry, CTkOptionMenu, CTkButton
from tkinter import ttk
from helpers import CTkToplevel, show_message

class DispositivosTab:
    def __init__(self, parent, db_manager, tipos_dispositivos, dispositivo_info, graph_manager):
        self.parent = parent
        self.db_manager = db_manager
        self.tipos_dispositivos = tipos_dispositivos
        self.dispositivo_info = dispositivo_info
        self.graph_manager = graph_manager

    def build_tab(self, tab):
        dispositivos_frame = CTkFrame(tab, fg_color="white")
        dispositivos_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Frame de filtros
        filtros_frame = CTkFrame(dispositivos_frame, fg_color="#D9D9D9", corner_radius=10)
        filtros_frame.pack(fill="x", pady=10)

        self.filtro_id_input = CTkEntry(filtros_frame, placeholder_text="ID")
        self.filtro_nombre_input = CTkEntry(filtros_frame, placeholder_text="Nombre")
        self.filtro_tipo_input = CTkOptionMenu(filtros_frame, values=["Todos"] + self.tipos_dispositivos)
        self.filtro_ubicacion_input = CTkEntry(filtros_frame, placeholder_text="Ubicación")
        self.filtro_btn = CTkButton(filtros_frame, text="Filtrar", command=self.filtrar_dispositivos)

        self.filtro_id_input.grid(row=0, column=0, padx=10, pady=10)
        self.filtro_nombre_input.grid(row=0, column=1, padx=10, pady=10)
        self.filtro_tipo_input.grid(row=0, column=2, padx=10, pady=10)
        self.filtro_ubicacion_input.grid(row=0, column=3, padx=10, pady=10)
        self.filtro_btn.grid(row=0, column=4, padx=10, pady=10)

        # Split inferior
        bottom_frame = CTkFrame(dispositivos_frame, fg_color="white")
        bottom_frame.pack(fill="both", expand=True)

        # Dashboard grande, lista pequeña
        self.left_frame = CTkFrame(bottom_frame, fg_color="white", width=200)
        self.right_frame = CTkFrame(bottom_frame, fg_color="white")

        self.left_frame.pack(side="left", fill="both", expand=False, padx=5, pady=5)
        self.right_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # Tabla de dispositivos
        dispositivos_label = CTkLabel(self.left_frame, text="Listado de Dispositivos", text_color="black", font=("", 18, "bold"))
        dispositivos_label.pack(pady=10)

        self.dispositivos_tree = ttk.Treeview(self.left_frame, columns=("ID", "Nombre", "Tipo", "Ubicacion"), show="headings")
        self.dispositivos_tree.heading("ID", text="ID")
        self.dispositivos_tree.heading("Nombre", text="Nombre")
        self.dispositivos_tree.heading("Tipo", text="Tipo")
        self.dispositivos_tree.heading("Ubicacion", text="Ubicación")
        self.dispositivos_tree.bind("<<TreeviewSelect>>", lambda e: self.dispositivo_seleccionado())
        self.dispositivos_tree.pack(fill="both", expand=True, pady=10)

        self.actualizar_tabla_dispositivos()

        # Botones Dispositivos
        botones_frame = CTkFrame(self.left_frame, fg_color="white")
        botones_frame.pack(pady=10)

        self.agregar_btn = CTkButton(botones_frame, text="Agregar Dispositivo", command=self.agregar_dispositivo)
        self.modificar_btn = CTkButton(botones_frame, text="Modificar Dispositivo", command=self.modificar_dispositivo)
        self.eliminar_btn = CTkButton(botones_frame, text="Eliminar Dispositivo", command=self.eliminar_dispositivo)

        self.agregar_btn.grid(row=0, column=0, padx=5)
        self.modificar_btn.grid(row=0, column=1, padx=5)
        self.eliminar_btn.grid(row=0, column=2, padx=5)

        # Edición de Dispositivo
        self.edicion_frame = CTkFrame(self.left_frame, fg_color="#D9D9D9", corner_radius=10)
        self.edicion_frame.pack(pady=10, fill="x")
        self.edicion_frame.pack_forget()

        self.edicion_title = CTkLabel(self.edicion_frame, text="Agregar/Modificar Dispositivo", text_color="black", font=("", 16, "bold"))
        self.edicion_title.pack(pady=10)

        form_frame = CTkFrame(self.edicion_frame, fg_color="#D9D9D9")
        form_frame.pack(pady=10, padx=10, fill="x")

        CTkLabel(form_frame, text="Nombre:", text_color="black").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.nombre_input = CTkEntry(form_frame)
        self.nombre_input.grid(row=0, column=1, padx=5, pady=5)

        CTkLabel(form_frame, text="Tipo:", text_color="black").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.tipo_input = CTkOptionMenu(form_frame, values=self.tipos_dispositivos)
        self.tipo_input.grid(row=1, column=1, padx=5, pady=5)

        CTkLabel(form_frame, text="Ubicación:", text_color="black").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.ubicacion_input = CTkEntry(form_frame)
        self.ubicacion_input.grid(row=2, column=1, padx=5, pady=5)

        btns_edicion_frame = CTkFrame(self.edicion_frame, fg_color="#D9D9D9")
        btns_edicion_frame.pack(pady=10)

        self.guardar_btn = CTkButton(btns_edicion_frame, text="Guardar", command=self.guardar_dispositivo)
        self.cancelar_btn = CTkButton(btns_edicion_frame, text="Cancelar", command=self.cancelar_edicion)

        self.guardar_btn.grid(row=0, column=0, padx=10)
        self.cancelar_btn.grid(row=0, column=1, padx=10)

        # El resto del código está intacto y se mantiene en su totalidad.


    def actualizar_tabla_dispositivos(self, filtros=None):
        for i in self.dispositivos_tree.get_children():
            self.dispositivos_tree.delete(i)
        try:
            dispositivos = self.db_manager.obtener_dispositivos(filtros)
            for disp in dispositivos:
                self.dispositivos_tree.insert("", "end", values=(disp[0], disp[1], disp[2], disp[3] if disp[3] else "N/A"))
        except Exception as e:
            self.show_message("Error", f"No se pudo actualizar la tabla de dispositivos:\n{e}")

    def agregar_dispositivo(self):
        self.edicion_title.configure(text="Agregar Dispositivo")
        self.nombre_input.delete(0, "end")
        self.tipo_input.set(self.tipos_dispositivos[0])
        self.ubicacion_input.delete(0, "end")
        self.parent.dispositivo_mode = "add"
        self.parent.selected_dispositivo_id = None
        self.edicion_frame.pack(pady=10, fill="x")

    def modificar_dispositivo(self):
        selected = self.dispositivos_tree.selection()
        if not selected:
            self.show_message("Seleccionar Dispositivo", "Por favor, seleccione un dispositivo para modificar.")
            return

        item = self.dispositivos_tree.item(selected[0])
        vals = item["values"]
        id_dispositivo = vals[0]
        nombre = vals[1]
        tipo = vals[2]
        ubicacion = vals[3]

        self.edicion_title.configure(text="Modificar Dispositivo")
        self.nombre_input.delete(0, "end")
        self.nombre_input.insert(0, nombre)

        if tipo in self.tipos_dispositivos:
            self.tipo_input.set(tipo)
        else:
            self.tipo_input.set(self.tipos_dispositivos[0])

        self.ubicacion_input.delete(0, "end")
        if ubicacion != "N/A":
            self.ubicacion_input.insert(0, ubicacion)

        self.parent.dispositivo_mode = "modify"
        self.parent.selected_dispositivo_id = id_dispositivo
        self.edicion_frame.pack(pady=10, fill="x")

    def eliminar_dispositivo(self):
        selected = self.dispositivos_tree.selection()
        if not selected:
            self.show_message("Seleccionar Dispositivo", "Por favor, seleccione un dispositivo para eliminar.")
            return

        item = self.dispositivos_tree.item(selected[0])
        vals = item["values"]
        id_dispositivo = vals[0]
        nombre = vals[1]

        confirm = CTkToplevel(self.parent)
        confirm.title("Confirmar Eliminación")
        confirm.geometry("300x150")
        confirm.resizable(False, False)
        clabel = CTkLabel(confirm, text=f"¿Eliminar el dispositivo '{nombre}'?")
        clabel.pack(pady=20)

        def yes():
            try:
                if self.db_manager.eliminar_dispositivo(id_dispositivo):
                    self.actualizar_tabla_dispositivos()
                    if self.parent.selected_dispositivo_id == id_dispositivo:
                        self.parent.selected_dispositivo_id = None
                        self.graph_manager.reset_graph()
            except Exception as e:
                self.show_message("Error", f"No se pudo eliminar el dispositivo:\n{e}")
            confirm.destroy()

        def no():
            confirm.destroy()

        yes_btn = CTkButton(confirm, text="Sí", command=yes)
        yes_btn.pack(side="left", padx=30, pady=10)
        no_btn = CTkButton(confirm, text="No", command=no)
        no_btn.pack(side="right", padx=30, pady=10)

    def guardar_dispositivo(self):
        nombre = self.nombre_input.get().strip()
        tipo = self.tipo_input.get()
        ubicacion = self.ubicacion_input.get().strip()

        if not nombre or not tipo:
            self.show_message("Campos Vacíos", "Nombre y tipo son obligatorios.")
            return

        try:
            if self.parent.dispositivo_mode == "add":
                success = self.db_manager.agregar_dispositivo(nombre, tipo, ubicacion)
            elif self.parent.dispositivo_mode == "modify":
                success = self.db_manager.modificar_dispositivo(self.parent.selected_dispositivo_id, nombre, tipo, ubicacion)
            else:
                self.show_message("Modo Desconocido", "Modo de operación desconocido.")
                return

            if success:
                self.actualizar_tabla_dispositivos()
                self.edicion_frame.pack_forget()
                self.parent.dispositivo_mode = None
                self.parent.selected_dispositivo_id = None
        except Exception as e:
            self.show_message("Error", f"No se pudo guardar el dispositivo:\n{e}")

    def cancelar_edicion(self):
        self.edicion_frame.pack_forget()
        self.parent.dispositivo_mode = None
        self.parent.selected_dispositivo_id = None
        self.nombre_input.delete(0, "end")
        self.tipo_input.set(self.tipos_dispositivos[0])
        self.ubicacion_input.delete(0, "end")

    def filtrar_dispositivos(self):
        filtros = {
            'id_dispositivo': self.filtro_id_input.get().strip(),
            'nombre': self.filtro_nombre_input.get().strip(),
            'tipo': self.filtro_tipo_input.get() if self.filtro_tipo_input.get() != "Todos" else "",
            'ubicacion': self.filtro_ubicacion_input.get().strip()
        }
        if filtros['id_dispositivo']:
            if not filtros['id_dispositivo'].isdigit():
                self.show_message("ID Inválido", "El ID debe ser un número entero.")
                return
            filtros['id_dispositivo'] = int(filtros['id_dispositivo'])
        else:
            filtros['id_dispositivo'] = None
        self.actualizar_tabla_dispositivos(filtros)

    def dispositivo_seleccionado(self):
        selected = self.dispositivos_tree.selection()
        if selected:
            item = self.dispositivos_tree.item(selected[0])
            vals = item["values"]
            self.parent.selected_dispositivo_id = vals[0]
            self.parent.selected_dispositivo_tipo = vals[2]
            self.graph_manager.actualizar_labels_grafico(self.parent.selected_dispositivo_tipo)
        else:
            self.parent.selected_dispositivo_id = None
            self.parent.selected_dispositivo_tipo = None
            self.graph_manager.reset_graph()
