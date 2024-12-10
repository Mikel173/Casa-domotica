# database_manager.py

import sys
import mysql.connector
from PyQt5.QtWidgets import QMessageBox
import bcrypt  # Importa bcrypt

class DatabaseManager:
    def __init__(self):
        print(">>> DatabaseManager.__init__: Intentando conectar a la base de datos...")
        try:
            self.conexion = mysql.connector.connect(
                host="127.0.0.1",        # Cambiar si es necesario
                user="root",             # Cambiar si tu usuario es diferente
                password="",             # Cambiar si tu contraseña no está vacía
                database="bd_csdomotica",
                autocommit=True,
                connection_timeout=10
            )
            print(">>> DatabaseManager.__init__: Conexión exitosa a la base de datos.")
        except mysql.connector.Error as err:
            print(f">>> DatabaseManager.__init__: Error al conectar a la base de datos: {err}")
            raise Exception(f"No se pudo conectar a la base de datos: {err}")
        except Exception as e:
            print(f">>> DatabaseManager.__init__: Error inesperado: {e}")
            raise e
    def execute_query(self, query, params=None):
        """
        Ejecuta una consulta SQL y devuelve los resultados.
        :param query: La consulta SQL a ejecutar.
        :param params: Una tupla de parámetros para la consulta.
        :return: Lista de tuplas con los resultados.
        """
        print(f">>> DatabaseManager.execute_query: Ejecutando consulta: {query} con parámetros: {params}")
        try:
            cursor = self.conexion.cursor()
            cursor.execute(query, params)
            if query.strip().upper().startswith("SELECT"):
                result = cursor.fetchall()
            else:
                result = None
            cursor.close()
            print(">>> DatabaseManager.execute_query: Consulta ejecutada con éxito.")
            return result
        except mysql.connector.Error as err:
            print(f">>> DatabaseManager.execute_query: Error al ejecutar la consulta: {err}")
            raise Exception(f"Error al ejecutar la consulta: {err}")
    def verify_user_login_any(self, user_or_email, password):
        """
        Verifica las credenciales del usuario ya sea por correo o por nombre.
        Si user_or_email contiene '@', se asume que es un correo.
        De lo contrario, se asume que es un nombre de usuario.
        """
        print(">>> DatabaseManager.verify_user_login_any:", user_or_email)
        cursor = self.conexion.cursor()

        if '@' in user_or_email:
            # Buscar por correo
            query = "SELECT password, id_usuario FROM usuarios WHERE correo=%s"
        else:
            # Buscar por nombre de usuario
            query = "SELECT password, id_usuario FROM usuarios WHERE nombre=%s"

        cursor.execute(query, (user_or_email,))
        result = cursor.fetchone()
        cursor.close()

        if result:
            stored_hashed, user_id = result
            # Reemplaza $2y$ por $2b$ si es necesario (algunos hashes podrían necesitarlo)
            if stored_hashed.startswith('$2y$'):
                stored_hashed = stored_hashed.replace('$2y$', '$2b$')

            if bcrypt.checkpw(password.encode('utf-8'), stored_hashed.encode('utf-8')):
                print(">>> DatabaseManager.verify_user_login_any: Login correcto.")
                return True, user_id

        print(">>> DatabaseManager.verify_user_login_any: Credenciales incorrectas.")
        return False, None

    # Métodos para Dispositivos
    def obtener_dispositivos(self, filtros=None):
        print(">>> DatabaseManager.obtener_dispositivos: filtros =", filtros)
        cursor = self.conexion.cursor()
        query = "SELECT id_dispositivo, nombre, tipo, ubicacion FROM dispositivos"
        params = []
        if filtros:
            condiciones = []
            if 'id_dispositivo' in filtros and filtros['id_dispositivo']:
                condiciones.append("id_dispositivo = %s")
                params.append(filtros['id_dispositivo'])
            if 'nombre' in filtros and filtros['nombre']:
                condiciones.append("nombre LIKE %s")
                params.append(f"%{filtros['nombre']}%")
            if 'tipo' in filtros and filtros['tipo']:
                condiciones.append("tipo = %s")
                params.append(filtros['tipo'])
            if 'ubicacion' in filtros and filtros['ubicacion']:
                condiciones.append("ubicacion LIKE %s")
                params.append(f"%{filtros['ubicacion']}%")
            if condiciones:
                query += " WHERE " + " AND ".join(condiciones)
        cursor.execute(query, tuple(params))
        dispositivos = cursor.fetchall()
        cursor.close()
        print(">>> DatabaseManager.obtener_dispositivos: dispositivos =", dispositivos)
        return dispositivos

    def agregar_dispositivo(self, nombre, tipo, ubicacion):
        print(">>> DatabaseManager.agregar_dispositivo:", nombre, tipo, ubicacion)
        try:
            cursor = self.conexion.cursor()
            cursor.execute("INSERT INTO dispositivos (nombre, tipo, ubicacion) VALUES (%s, %s, %s)", (nombre, tipo, ubicacion))
            self.conexion.commit()
            cursor.close()
            print(">>> DatabaseManager.agregar_dispositivo: Dispositivo agregado con éxito.")
            return True
        except mysql.connector.Error as err:
            print(">>> DatabaseManager.agregar_dispositivo: Error:", err)
            raise Exception(f"No se pudo agregar el dispositivo: {err}")

    def modificar_dispositivo(self, id_dispositivo, nombre, tipo, ubicacion):
        print(">>> DatabaseManager.modificar_dispositivo:", id_dispositivo, nombre, tipo, ubicacion)
        try:
            cursor = self.conexion.cursor()
            cursor.execute("UPDATE dispositivos SET nombre=%s, tipo=%s, ubicacion=%s WHERE id_dispositivo=%s", (nombre, tipo, ubicacion, id_dispositivo))
            self.conexion.commit()
            cursor.close()
            print(">>> DatabaseManager.modificar_dispositivo: Dispositivo modificado con éxito.")
            return True
        except mysql.connector.Error as err:
            print(">>> DatabaseManager.modificar_dispositivo: Error:", err)
            raise Exception(f"No se pudo modificar el dispositivo: {err}")

    def eliminar_dispositivo(self, id_dispositivo):
        print(">>> DatabaseManager.eliminar_dispositivo:", id_dispositivo)
        try:
            cursor = self.conexion.cursor()
            cursor.execute("DELETE FROM dispositivos WHERE id_dispositivo=%s", (id_dispositivo,))
            self.conexion.commit()
            cursor.close()
            print(">>> DatabaseManager.eliminar_dispositivo: Dispositivo eliminado con éxito.")
            return True
        except mysql.connector.Error as err:
            print(">>> DatabaseManager.eliminar_dispositivo: Error:", err)
            raise Exception(f"No se pudo eliminar el dispositivo: {err}")

    def obtener_datos_dispositivo(self, dispositivo_id, limit=50):
        print(">>> DatabaseManager.obtener_datos_dispositivo:", dispositivo_id, "limit:", limit)
        cursor = self.conexion.cursor()
        query = """
            SELECT ds.fecha_hora, ds.valor, u.nombre 
            FROM datos_dispositivos ds
            LEFT JOIN usuarios u ON ds.usuario_id = u.id_usuario
            WHERE ds.dispositivo_id = %s
            ORDER BY ds.fecha_hora DESC
            LIMIT %s
        """
        cursor.execute(query, (dispositivo_id, limit))
        datos = cursor.fetchall()
        cursor.close()
        print(">>> DatabaseManager.obtener_datos_dispositivo:", datos)
        return datos[::-1]

    # Métodos para Usuarios
    def obtener_usuarios(self):
        print(">>> DatabaseManager.obtener_usuarios")
        cursor = self.conexion.cursor()
        cursor.execute("SELECT id_usuario, nombre, correo FROM usuarios")
        usuarios = cursor.fetchall()
        cursor.close()
        print(">>> DatabaseManager.obtener_usuarios:", usuarios)
        return usuarios

    def agregar_usuario(self, nombre, correo, password):
        print(">>> DatabaseManager.agregar_usuario:", nombre, correo, password)
        try:
            cursor = self.conexion.cursor()
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            cursor.execute("INSERT INTO usuarios (nombre, correo, password) VALUES (%s, %s, %s)",
                           (nombre, correo, hashed_password.decode('utf-8')))
            self.conexion.commit()
            cursor.close()
            print(">>> DatabaseManager.agregar_usuario: Usuario agregado con éxito.")
            return True
        except mysql.connector.Error as err:
            print(">>> DatabaseManager.agregar_usuario: Error:", err)
            raise Exception(f"No se pudo agregar el usuario: {err}")

    def modificar_usuario(self, id_usuario, nombre, correo, password=None):
        print(">>> DatabaseManager.modificar_usuario:", id_usuario, nombre, correo, password)
        try:
            cursor = self.conexion.cursor()
            if password:
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
                cursor.execute("UPDATE usuarios SET nombre=%s, correo=%s, password=%s WHERE id_usuario=%s",
                               (nombre, correo, hashed_password.decode('utf-8'), id_usuario))
            else:
                cursor.execute("UPDATE usuarios SET nombre=%s, correo=%s WHERE id_usuario=%s", (nombre, correo, id_usuario))
            self.conexion.commit()
            cursor.close()
            print(">>> DatabaseManager.modificar_usuario: Usuario modificado con éxito.")
            return True
        except mysql.connector.Error as err:
            print(">>> DatabaseManager.modificar_usuario: Error:", err)
            raise Exception(f"No se pudo modificar el usuario: {err}")

    def eliminar_usuario(self, id_usuario):
        print(">>> DatabaseManager.eliminar_usuario:", id_usuario)
        try:
            cursor = self.conexion.cursor()
            cursor.execute("DELETE FROM usuarios WHERE id_usuario=%s", (id_usuario,))
            self.conexion.commit()
            cursor.close()
            print(">>> DatabaseManager.eliminar_usuario: Usuario eliminado con éxito.")
            return True
        except mysql.connector.Error as err:
            print(">>> DatabaseManager.eliminar_usuario: Error:", err)
            raise Exception(f"No se pudo eliminar el usuario: {err}")

    def log_accion_dispositivo(self, dispositivo_id, tipo_dispositivo, valor, usuario_id=None):
        print(">>> DatabaseManager.log_accion_dispositivo:", dispositivo_id, tipo_dispositivo, valor, usuario_id)
        try:
            cursor = self.conexion.cursor()
            cursor.execute("INSERT INTO datos_dispositivos (dispositivo_id, tipo_dispositivo, valor, usuario_id) VALUES (%s, %s, %s, %s)",
                           (dispositivo_id, tipo_dispositivo, valor, usuario_id))
            self.conexion.commit()
            cursor.close()
            print(">>> DatabaseManager.log_accion_dispositivo: Acción registrada con éxito.")
            return True
        except mysql.connector.Error as err:
            print(">>> DatabaseManager.log_accion_dispositivo: Error:", err)
            raise Exception(f"No se pudo registrar la acción del dispositivo: {err}")
    
    def obtener_datos_por_fechas_y_dispositivo(self, dispositivo_nombre, start_date, end_date):
    # Obtener el ID del dispositivo a partir del nombre
        query_disp = "SELECT id_dispositivo FROM dispositivos WHERE nombre=%s"
        disp_res = self.execute_query(query_disp, (dispositivo_nombre,))
        if not disp_res:
            return []
        disp_id = disp_res[0][0]

        query = """
            SELECT fecha_hora, valor
            FROM datos_dispositivos
            WHERE dispositivo_id = %s AND fecha_hora BETWEEN %s AND %s
            ORDER BY fecha_hora
        """
        return self.execute_query(query, (disp_id, start_date + " 00:00:00", end_date + " 23:59:59"))


if __name__ == "__main__":
    print(">>> database_manager.py: Probando inicialización de DatabaseManager.")
    try:
        db_manager = DatabaseManager()
        print(">>> database_manager.py: Conexión a la base de datos exitosa.")
    except Exception as e:
        print(f">>> database_manager.py: Error al inicializar DatabaseManager: {e}")
