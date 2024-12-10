from customtkinter import CTkFrame, CTkLabel, CTkComboBox, CTkButton
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import pandas as pd
import customtkinter as ctk
from tkcalendar import DateEntry
from datetime import datetime


class AnalysisFrame(CTkFrame):
    def __init__(self, parent, db_manager):
        super().__init__(parent, fg_color="white")
        self.parent = parent
        self.db_manager = db_manager

        # Crear widgets de filtros
        self.create_filters()

        # Crear sección de gráficos y análisis
        self.create_charts_and_analysis()

    def create_filters(self):
        filter_frame = CTkFrame(self, fg_color="#D9D9D9", corner_radius=10)
        filter_frame.pack(fill="x", padx=10, pady=10)

        # Selector de fecha inicial
        lbl_start = CTkLabel(filter_frame, text="Fecha Inicial:", text_color="black", font=("Arial", 12, "bold"))
        lbl_start.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.start_date = DateEntry(filter_frame, date_pattern="yyyy-MM-dd", width=12)
        self.start_date.grid(row=0, column=1, padx=5, pady=5)

        # Selector de hora inicial
        lbl_start_hour = CTkLabel(filter_frame, text="Hora Inicial (Opcional):", text_color="black", font=("Arial", 12, "bold"))
        lbl_start_hour.grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.start_hour = CTkComboBox(filter_frame, values=[f"{h:02}:{m:02}" for h in range(24) for m in [0, 30]])
        self.start_hour.grid(row=0, column=3, padx=5, pady=5)

        # Selector de fecha final
        lbl_end = CTkLabel(filter_frame, text="Fecha Final:", text_color="black", font=("Arial", 12, "bold"))
        lbl_end.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.end_date = DateEntry(filter_frame, date_pattern="yyyy-MM-dd", width=12)
        self.end_date.grid(row=1, column=1, padx=5, pady=5)

        # Selector de hora final
        lbl_end_hour = CTkLabel(filter_frame, text="Hora Final (Opcional):", text_color="black", font=("Arial", 12, "bold"))
        lbl_end_hour.grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.end_hour = CTkComboBox(filter_frame, values=[f"{h:02}:{m:02}" for h in range(24) for m in [0, 30]])
        self.end_hour.grid(row=1, column=3, padx=5, pady=5)

        # Selector de dispositivo
        lbl_device = CTkLabel(filter_frame, text="Dispositivo:", text_color="black", font=("Arial", 12, "bold"))
        lbl_device.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.device_var = ctk.StringVar()
        self.device_dropdown = CTkComboBox(filter_frame, variable=self.device_var, values=self.get_devices())
        self.device_dropdown.grid(row=2, column=1, padx=5, pady=5)

        # Botón para aplicar filtros
        apply_btn = CTkButton(filter_frame, text="Aplicar Filtros", command=self.update_charts_and_analysis, font=("Arial", 12, "bold"))
        apply_btn.grid(row=2, column=3, padx=5, pady=5)

    def get_devices(self):
        query = "SELECT nombre FROM dispositivos"
        try:
            devices = self.db_manager.execute_query(query)
            return [device[0] for device in devices]
        except Exception as e:
            self.show_message("Error", f"No se pudo obtener la lista de dispositivos:\n{e}")
            return []

    def create_charts_and_analysis(self):
    # Marco principal para gráficos y análisis
        main_frame = CTkFrame(self, fg_color="white")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Marco para gráficos (izquierda)
        self.chart_frame = CTkFrame(main_frame, fg_color="white")
        self.chart_frame.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=10)

        # Crear figura de matplotlib
        self.fig, self.ax = plt.subplots(figsize=(10, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Marco para análisis con scroll (derecha)
        analysis_container = CTkFrame(main_frame, fg_color="#f0f0f0", corner_radius=10)
        analysis_container.pack(side="right", fill="y", padx=10, pady=10)

        # Canvas para scroll
        self.analysis_canvas = ctk.CTkCanvas(analysis_container, bg="#f0f0f0", highlightthickness=0)
        self.analysis_canvas.pack(side="left", fill="both", expand=True)

        # Scrollbar
        scrollbar = ctk.CTkScrollbar(analysis_container, command=self.analysis_canvas.yview)
        scrollbar.pack(side="right", fill="y")

        self.analysis_canvas.configure(yscrollcommand=scrollbar.set)

        # Frame interno para el contenido de análisis
        self.analysis_frame = CTkFrame(self.analysis_canvas, fg_color="#f0f0f0", corner_radius=10)
        self.analysis_canvas.create_window((0, 0), window=self.analysis_frame, anchor="nw")

        # Vincular eventos de tamaño al canvas
        self.analysis_frame.bind("<Configure>", lambda e: self.analysis_canvas.configure(scrollregion=self.analysis_canvas.bbox("all")))


    def update_charts_and_analysis(self):
        start_date = self.start_date.get()
        end_date = self.end_date.get()
        start_hour = self.start_hour.get() or "00:00"
        end_hour = self.end_hour.get() or "23:59"
        device = self.device_var.get()

        if not device:
            self.ax.clear()
            self.ax.set_title("Seleccione un dispositivo y aplique los filtros.", fontsize=14, color="red")
            self.canvas.draw()
            return

        start_datetime = f"{start_date} {start_hour}:00"
        end_datetime = f"{end_date} {end_hour}:59"

        query = """
            SELECT fecha_hora, valor 
            FROM datos_dispositivos d 
            JOIN dispositivos disp ON d.dispositivo_id = disp.id_dispositivo 
            WHERE disp.nombre = %s AND fecha_hora BETWEEN %s AND %s
        """
        params = [device, start_datetime, end_datetime]

        try:
            data = self.db_manager.execute_query(query, tuple(params))
            df = pd.DataFrame(data, columns=['fecha_hora', 'valor'])

            self.ax.clear()
            if df.empty:
                self.ax.set_title(f"No hay datos disponibles para {device}.", fontsize=14, color="red")
                self.canvas.draw()
                return

            df['fecha_hora'] = pd.to_datetime(df['fecha_hora'])
            df['valor'] = pd.to_numeric(df['valor'], errors='coerce')

            # Graficar datos
            self.ax.plot(df['fecha_hora'], df['valor'], marker='o', linestyle='-', color="blue")
            self.ax.set_title(f"Valores de {device} en el Tiempo", fontsize=14)
            self.ax.set_xlabel("Fecha y Hora", fontsize=12)
            self.ax.set_ylabel("Valor", fontsize=12)
            self.ax.grid(True)
            self.canvas.draw()

            # Realizar análisis
            self.update_analysis(df, device)
        except Exception as e:
            self.show_message("Error", f"No se pudo actualizar los gráficos:\n{e}")

    def update_analysis(self, df, device):
        # Limpiar el marco de análisis
        for widget in self.analysis_frame.winfo_children():
            widget.destroy()

        # Calcular estadísticas básicas
        mean = df['valor'].mean()
        std_dev = df['valor'].std()
        max_value = df['valor'].max()
        min_value = df['valor'].min()

        # Agrupar por hora para análisis más detallado
        df['hour'] = df['fecha_hora'].dt.hour
        grouped = df.groupby('hour')['valor'].mean()

        # Mostrar estadísticas generales con formato claro y ordenado
        stats_frame = CTkFrame(self.analysis_frame, fg_color="white", corner_radius=10)
        stats_frame.pack(fill="x", padx=10, pady=5)
        CTkLabel(stats_frame, text=f"Análisis para {device}", text_color="black", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=5)
        CTkLabel(stats_frame, text=f"Promedio: {mean:.2f}", text_color="black", font=("Arial", 12)).pack(anchor="w", padx=20)
        CTkLabel(stats_frame, text=f"Desviación Estándar: {std_dev:.2f}", text_color="black", font=("Arial", 12)).pack(anchor="w", padx=20)
        CTkLabel(stats_frame, text=f"Valor Máximo: {max_value:.2f}", text_color="black", font=("Arial", 12)).pack(anchor="w", padx=20)
        CTkLabel(stats_frame, text=f"Valor Mínimo: {min_value:.2f}", text_color="black", font=("Arial", 12)).pack(anchor="w", padx=20)

        # Análisis de picos horarios
        peak_hour = grouped.idxmax()
        peak_value = grouped.max()
        peak_text = f"Hora Pico: {peak_hour}:00 con un promedio de {peak_value:.2f}"
        CTkLabel(stats_frame, text=peak_text, text_color="blue", font=("Arial", 12, "italic")).pack(anchor="w", padx=20, pady=5)

        # Mostrar detalle de valores promedio por hora
        detail_frame = CTkFrame(self.analysis_frame, fg_color="#e6f7ff", corner_radius=10)
        detail_frame.pack(fill="x", padx=10, pady=10)
        CTkLabel(detail_frame, text="Promedio por Hora:", text_color="black", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=5)
        for hour, value in grouped.items():
            hour_text = f"{hour:02}:00 - Promedio: {value:.2f}"
            CTkLabel(detail_frame, text=hour_text, text_color="black", font=("Arial", 12)).pack(anchor="w", padx=20)

    def show_message(self, title, message):
        top = ctk.CTkToplevel(self)
        top.title(title)
        top.geometry("300x150")
        top.resizable(False, False)

        label = CTkLabel(top, text=message, font=("", 14))
        label.pack(pady=20)

        btn = CTkButton(top, text="OK", command=top.destroy)
        btn.pack(pady=10)