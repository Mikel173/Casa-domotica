# app.py
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from database_manager import DatabaseManager
import bcrypt
from datetime import datetime
import pandas as pd

app = Flask(__name__)
app.secret_key = 'cambia_esta_clave'  # Cambia esta clave por una segura
db = DatabaseManager()

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        success, user_id = db.verify_user_login_any(email, password)
        if success:
            session['user_id'] = user_id
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Correo o contraseña incorrectos.")
    return render_template('login.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        correo = request.form.get('correo')
        password = request.form.get('password')
        if not nombre or not correo or not password:
            return render_template('register.html', error="Todos los campos son requeridos.")
        try:
            db.agregar_usuario(nombre, correo, password)
            return redirect(url_for('login'))
        except Exception as e:
            return render_template('register.html', error=f"Ocurrió un error: {e}")
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    # Obtener lista de dispositivos
    dispositivos = db.obtener_dispositivos()
    return render_template('dashboard.html', dispositivos=dispositivos)

@app.route('/analysis', methods=['GET','POST'])
def analysis():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    dispositivos = db.obtener_dispositivos()
    data = None
    device_selected = None
    start_date = None
    end_date = None
    avg = None
    std_dev = None
    max_val = None
    min_val = None
    peak_hour = None
    peak_value = None
    hourly_avg = None

    if request.method == 'POST':
        device_selected = request.form.get('device')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        if device_selected and start_date and end_date:
            data = db.obtener_datos_por_fechas_y_dispositivo(device_selected, start_date, end_date)
            if data:
                # Convertir datos a DataFrame
                df = pd.DataFrame(data, columns=['fecha_hora', 'valor'])
                # Convertir a datetime y float
                df['fecha_hora'] = pd.to_datetime(df['fecha_hora'])
                df['valor'] = pd.to_numeric(df['valor'], errors='coerce').fillna(0)
                
                # Calcular estadísticas
                avg = round(df['valor'].mean(), 2)
                std_dev = round(df['valor'].std(), 2)
                max_val = round(df['valor'].max(), 2)
                min_val = round(df['valor'].min(), 2)
                
                # Promedio por hora
                df['hora'] = df['fecha_hora'].dt.hour
                hourly_avg_series = df.groupby('hora')['valor'].mean()
                hourly_avg = hourly_avg_series.reset_index().values.tolist()
                
                # Hora pico
                if not hourly_avg_series.empty:
                    peak_hour = int(hourly_avg_series.idxmax())
                    peak_value = round(hourly_avg_series.max(), 2)
            else:
                # Si no hay datos, establecer valores predeterminados
                avg = 0
                std_dev = 0
                max_val = 0
                min_val = 0
                peak_hour = 0
                peak_value = 0
                hourly_avg = []

    return render_template('analysis.html', 
                           dispositivos=dispositivos, 
                           data=data, 
                           device_selected=device_selected, 
                           start_date=start_date, 
                           end_date=end_date, 
                           avg=avg, 
                           std_dev=std_dev, 
                           max_val=max_val, 
                           min_val=min_val,
                           peak_hour=peak_hour,
                           peak_value=peak_value,
                           hourly_avg=hourly_avg)

@app.route('/api/realtime_data/<int:device_id>')
def api_realtime_data(device_id):
    # Datos recientes del dispositivo seleccionado (últimos 50)
    data = db.obtener_datos_dispositivo(device_id, limit=50)
    # Devolvemos en formato JSON para JavaScript
    result = []
    for row in data:
        fecha_str = row[0].strftime('%Y-%m-%d %H:%M:%S')
        try:
            val = float(row[1])
        except ValueError:
            val = 0
        result.append({"fecha_hora": fecha_str, "valor": val})
    return jsonify(result)

if __name__ == "__main__":
    # Para acceder desde el teléfono, pon host='0.0.0.0'
    app.run(host='0.0.0.0', port=5000, debug=True)
