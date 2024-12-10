from customtkinter import CTkFrame, CTkTabview
from dispositivos_tab import DispositivosTab
from usuarios_tab import UsuariosTab
from analysis_frame import AnalysisFrame
from graph_manager import GraphManager
from helpers import show_message

class MainWindow(CTkFrame):
    def __init__(self, parent, db_manager):
        super().__init__(parent, fg_color="white")
        self.parent = parent
        self.db_manager = db_manager

        # Inicialización de variables necesarias
        self.selected_dispositivo_id = None
        self.selected_dispositivo_tipo = None

        # Información de dispositivos
        self.tipos_dispositivos = [
            'temperatura', 'humedad', 'luz', 'presión', 'gas', 'sonido',
            'movimiento', 'nivel', 'voltaje', 'corriente', 'potencia', 'pH'
        ]

        self.dispositivo_info = {
            'temperatura': {'unidad': '°C', 'titulo': 'Temperatura en Tiempo Real'},
            'humedad': {'unidad': '%', 'titulo': 'Humedad en Tiempo Real'}
        }

        self.pack(fill="both", expand=True)

        # Crear Tabview
        self.tabs = CTkTabview(self, width=1800, height=900)
        self.tabs.pack(fill="both", expand=True)

        # Crear instancias de las pestañas
        self.graph_manager = GraphManager(self, self.db_manager, self.dispositivo_info)
        self.dispositivos_tab_class = DispositivosTab(
            self, self.db_manager, self.tipos_dispositivos, self.dispositivo_info, self.graph_manager
        )
        self.usuarios_tab_class = UsuariosTab(self, self.db_manager)

        # Añadir pestañas
        self.dispositivos_tab = self.tabs.add("Dispositivos")
        self.usuarios_tab = self.tabs.add("Usuarios")
        self.analisis_tab = self.tabs.add("Análisis")

        # Construir pestañas
        self.dispositivos_tab_class.build_tab(self.dispositivos_tab)
        self.usuarios_tab_class.build_tab(self.usuarios_tab)

        # Vincular AnalysisFrame correctamente a la pestaña "Análisis"
        self.analysis_frame_class = AnalysisFrame(self.analisis_tab, self.db_manager)
        self.analysis_frame_class.pack(fill="both", expand=True)

        # Vincular el gráfico en la pestaña de dispositivos
        self.graph_manager.build_graph_section(self.dispositivos_tab_class.right_frame)

        # Iniciar actualización del gráfico
        self.after(1000, self.graph_manager.actualizar_grafico)

    def show_message(self, title, message):
        show_message(self, title, message)
