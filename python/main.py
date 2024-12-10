from customtkinter import *
from database_manager import DatabaseManager
from login_frame import LoginFrame
from main_window import MainWindow

class MainApp(CTk):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.title("Aplicación Domótica")

        # Primero defines la resolución base
        width = 1280
        height = 720
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)

        # Actualizas la ventana para obtener dimensiones de la pantalla
        self.update_idletasks()

        # Calculas la posición para centrar la ventana
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        # Estableces nueva geometría con la ventana centrada
        self.geometry(f"{width}x{height}+{x}+{y}")

        # Mostrar el login frame al inicio
        self.current_frame = None
        self.show_login_frame()


    def show_login_frame(self):
        """Muestra el frame de inicio de sesión."""
        if self.current_frame is not None:
            self.current_frame.destroy()
        self.current_frame = LoginFrame(self, self.db_manager)
        self.current_frame.pack(fill="both", expand=True)

    def show_dashboard(self):
        """Muestra el dashboard principal (MainWindow)."""
        if self.current_frame is not None:
            self.current_frame.destroy()
        self.current_frame = MainWindow(self, self.db_manager)
        self.current_frame.pack(fill="both", expand=True)
    def show_register_frame(self):
        """Muestra el frame de registro."""
        if self.current_frame is not None:
            self.current_frame.destroy()
        from register_frame import RegisterFrame
        self.current_frame = RegisterFrame(self, self.db_manager)
        self.current_frame.pack(fill="both", expand=True)


def main():
    """Función principal para iniciar la aplicación."""
    set_appearance_mode("System")  # Opcional: "Dark", "Light", "System"
    set_default_color_theme("blue")  # Tema de color

    db_manager = DatabaseManager()
    app = MainApp(db_manager)
    app.mainloop()

if __name__ == "__main__":
    main()
