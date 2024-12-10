from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
from customtkinter import CTkLabel, CTkFrame
from datetime import datetime
from helpers import show_message

class GraphManager:
    def __init__(self, parent, db_manager, dispositivo_info):
        self.parent = parent
        self.db_manager = db_manager
        self.dispositivo_info = dispositivo_info

    def build_graph_section(self, right_frame):
        dashboard_label = CTkLabel(right_frame, text="Dashboard en Tiempo Real", text_color="black", font=("", 18, "bold"))
        dashboard_label.pack(pady=10)

        self.figure = Figure(figsize=(8, 6))  # Gráfico más grande
        self.ax = self.figure.add_subplot(111)
        self.linea, = self.ax.plot([], [], '-', color='#e74c3c', lw=2, label='Sensor')
        self.ax.set_xlabel('Tiempo', color='#34495e', fontsize=12)
        self.ax.set_ylabel('Valor', color='#34495e', fontsize=12)
        self.ax.set_title('Datos en Tiempo Real', color='#34495e', fontsize=14)
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        self.ax.tick_params(axis='x', rotation=45)
        self.ax.legend()
        self.figure.tight_layout()

        self.canvas = FigureCanvasTkAgg(self.figure, master=right_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill="both", expand=True, padx=10, pady=10)

        values_frame = CTkFrame(right_frame, fg_color="white")
        values_frame.pack(pady=10)

        self.current_value_label = CTkLabel(values_frame, text="Valor Actual: N/A", text_color="black", fg_color="#ecf0f1", corner_radius=8)
        self.min_value_label = CTkLabel(values_frame, text="Valor Mínimo: N/A", text_color="black", fg_color="#ecf0f1", corner_radius=8)
        self.max_value_label = CTkLabel(values_frame, text="Valor Máximo: N/A", text_color="black", fg_color="#ecf0f1", corner_radius=8)

        self.current_value_label.grid(row=0, column=0, padx=5, pady=5)
        self.min_value_label.grid(row=0, column=1, padx=5, pady=5)
        self.max_value_label.grid(row=0, column=2, padx=5, pady=5)

    def reset_graph(self):
        self.ax.set_title('Datos en Tiempo Real', color='#34495e', fontsize=14)
        self.ax.set_ylabel('Valor', color='#34495e', fontsize=12)
        self.linea.set_data([], [])
        self.ax.relim()
        self.ax.autoscale_view()
        self.current_value_label.configure(text="Seleccione un dispositivo")
        self.min_value_label.configure(text="")
        self.max_value_label.configure(text="")
        self.canvas.draw()

    def actualizar_labels_grafico(self, tipo_dispositivo):
        info = self.dispositivo_info.get(tipo_dispositivo, {'unidad': '', 'titulo': f'Datos de {tipo_dispositivo.capitalize()} en Tiempo Real'})
        self.ax.set_ylabel(f'Valor ({info["unidad"]})', color='#34495e', fontsize=12)
        self.ax.set_title(info['titulo'], color='#34495e', fontsize=14)
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()

    def actualizar_grafico(self):
        if not self.parent.selected_dispositivo_id:
            self.reset_graph()
            self.parent.after(1000, self.actualizar_grafico)
            return

        tipo = (self.parent.selected_dispositivo_tipo or "").lower()
        try:
            datos = self.db_manager.obtener_datos_dispositivo(self.parent.selected_dispositivo_id, limit=50)
        except Exception as e:
            self.show_message("Error", f"No se pudieron obtener datos del dispositivo:\n{e}")
            self.parent.after(1000, self.actualizar_grafico)
            return

        if tipo == "sensor":
            self.actualizar_grafico_sensor(datos)
        else:
            self.actualizar_grafico_actuador(datos)

        self.parent.after(1000, self.actualizar_grafico)

    def actualizar_grafico_sensor(self, datos):
        if not datos:
            self.reset_graph()
            return

        tiempos = [d[0] for d in datos]
        valores = [float(d[1]) for d in datos]

        tiempos_num = mdates.date2num(tiempos)
        self.linea.set_data(tiempos_num, valores)

        # Limitar a los últimos 10 datos en el gráfico
        if len(tiempos_num) > 10:
            self.ax.set_xlim(tiempos_num[-10], tiempos_num[-1])

        self.ax.relim()
        self.ax.autoscale_view()

        valor_actual = valores[-1]
        valor_min = min(valores)
        valor_max = max(valores)

        unidad = self.dispositivo_info.get(self.parent.selected_dispositivo_tipo, {}).get('unidad', '')

        self.current_value_label.configure(text=f"Valor Actual: {valor_actual} {unidad}")
        self.min_value_label.configure(text=f"Valor Mínimo: {valor_min} {unidad}")
        self.max_value_label.configure(text=f"Valor Máximo: {valor_max} {unidad}")

        self.canvas.draw()

    def actualizar_grafico_actuador(self, datos):
        if not datos:
            self.reset_graph()
            return

        tiempos = [d[0] for d in datos]
        estados = [float(d[1]) for d in datos]

        tiempos_num = mdates.date2num(tiempos)
        self.linea.set_data(tiempos_num, estados)

        self.ax.relim()
        self.ax.autoscale_view()

        self.canvas.draw()

    def show_message(self, title, message):
        show_message(self.parent, title, message)
