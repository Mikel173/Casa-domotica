from machine import Pin, Timer, I2C, PWM, ADC
import utime
import dht
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd
import sys

# Importar Wifi_lib y urequests
import Wifi_lib
import urequests as requests
import ujson  # Para manejar JSON

# Inicializar Wi-Fi
Wifi_lib.wifi_init()

# Configuración del LCD
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=100000)
lcd = I2cLcd(i2c, 0x27, 2, 16)
lcd.clear()
lcd.backlight_on()

# Configuración del sensor ultrasónico
timer_ultrasonico = Timer()
trigger = Pin(3, Pin.OUT)
echo = Pin(2, Pin.IN)

# Configuración del sensor infrarrojo
sensor_ir = Pin(5, Pin.IN)

# Configuración del sensor de temperatura y humedad (DHT22)
dht_pin = Pin(6)
dht_sensor = dht.DHT22(dht_pin)

# Configuración del servomotor
servo = PWM(Pin(15))
servo.freq(50)

# Configuración de los LEDs originales
led = Pin(16, Pin.OUT)
led1 = Pin(17, Pin.OUT)

# Configuración del sensor de sonido y RGB
sensor_sonido = Pin(28, Pin.IN)
red_pin = PWM(Pin(13))
green_pin = PWM(Pin(8))
blue_pin = PWM(Pin(11))
red_pin.freq(1000)
green_pin.freq(1000)
blue_pin.freq(1000)

# Nuevas configuraciones para el sensor de gas y LEDs adicionales
mq2_digital = Pin(19, Pin.IN)
mq2_analog = ADC(26)
led_gas = Pin(22, Pin.OUT)
led_nuevo1 = Pin(18, Pin.OUT)
led_nuevo2 = Pin(20, Pin.OUT)

# Configuración de los botones originales y nuevos
button_next = Pin(14, Pin.IN, Pin.PULL_UP)
button_nuevo1 = Pin(21, Pin.IN, Pin.PULL_UP)
button_nuevo2 = Pin(9, Pin.IN, Pin.PULL_UP)

# Variables globales
distancia = 0
sensor_actual = 1
led_encendido = False
color_actual = 0
last_display = ["", ""]
ultimo_estado_sonido = 0
ultimo_tiempo_sonido = 0
ultimo_tiempo_log = 0
intervalo_log = 5000  # Intervalo para enviar datos y mostrar en consola (ms)
programa_activo = True

# Estados para los nuevos LEDs
led_nuevo1_state = False
led_nuevo2_state = False
umbral_gas = 35000

# Variables para almacenar datos de sensores
datos_sensores = {
    'ultrasonico': 0,
    'infrarrojo': False,
    'temperatura': 0,
    'humedad': 0,
    'sonido': False,
    'gas_digital': False,
    'gas_analog': 0,
    'led_nuevo1': False,
    'led_nuevo2': False,
    'rgb': False
}

# Mapeo de dispositivos con sus IDs y tipos
device_mappings = {
    'ultrasonico': {'id': 1, 'tipo': 'sensor'},
    'infrarrojo': {'id': 2, 'tipo': 'sensor'},
    'temperatura': {'id': 3, 'tipo': 'sensor'},
    'humedad': {'id': 4, 'tipo': 'sensor'},
    'sonido': {'id': 5, 'tipo': 'sensor'},
    'gas_digital': {'id': 6, 'tipo': 'sensor'},
    'gas_analog': {'id': 7, 'tipo': 'sensor'},
    'led_nuevo1': {'id': 8, 'tipo': 'actuador'},
    'led_nuevo2': {'id': 9, 'tipo': 'actuador'},
    'rgb': {'id': 10, 'tipo': 'actuador'}
}

def mover_servo(angulo):
    if programa_activo:
        min_duty = 1000000
        max_duty = 2000000
        duty = min_duty + (max_duty - min_duty) * angulo / 180
        servo.duty_ns(int(duty))
        # Debug: Indicar movimiento del servo
        # print(f"Servo movido a {angulo} grados")

def sensor_ult(timer):
    global distancia, datos_sensores
    if not programa_activo:
        return
        
    trigger.low()
    utime.sleep_us(2)
    trigger.high()
    utime.sleep_us(10)  # Asegurar suficiente tiempo de disparo
    trigger.low()
    
    start = utime.ticks_us()
    # Esperar a que el echo se active con un timeout de 30ms
    while echo.value() == 0:
        if utime.ticks_diff(utime.ticks_us(), start) > 30000:
            break
    if echo.value() == 1:
        start = utime.ticks_us()
        while echo.value() == 1:
            if utime.ticks_diff(utime.ticks_us(), start) > 30000:
                break
        end = utime.ticks_us()
        duracion = utime.ticks_diff(end, start)
        distancia = (duracion * 0.0343) / 2
        datos_sensores['ultrasonico'] = distancia
    else:
        # Timeout
        datos_sensores['ultrasonico'] = -1  # Indicar error o fuera de rango

    if distancia >= 0:  # Distancia válida
        if distancia < 10:
            led.value(1)
        else:
            led.value(0)
    else:
        led.value(0)  # Apagar en caso de error

def set_color(red, green, blue):
    if programa_activo:
        red_pin.duty_u16(red)
        green_pin.duty_u16(green)
        blue_pin.duty_u16(blue)
        # Debug: Indicar estado RGB
        # print(f"RGB set to R:{red} G:{green} B:{blue}")

def cambiar_color():
    global color_actual
    if not programa_activo:
        return
        
    if color_actual == 0:
        set_color(0, 65535, 0)  # Verde
        color_actual = 1
        datos_sensores['rgb'] = True
        print("RGB Encendido Verde")
    elif color_actual == 1:
        set_color(65535, 65535, 0)  # Amarillo
        color_actual = 2
        datos_sensores['rgb'] = True
        print("RGB Encendido Amarillo")
    else:
        set_color(0, 65535, 65535)  # Cian
        color_actual = 0
        datos_sensores['rgb'] = True
        print("RGB Encendido Cian")

def apagar_rgb():
    set_color(0, 0, 0)
    global led_encendido
    led_encendido = False
    datos_sensores['rgb'] = False
    print("RGB Apagado")

def procesar_sonido():
    global ultimo_estado_sonido, ultimo_tiempo_sonido, led_encendido
    if not programa_activo:
        return
        
    tiempo_actual = utime.ticks_ms()
    
    # Detección de borde simple, sin retardos
    sonido_valor = sensor_sonido.value()
    if sonido_valor == 1 and ultimo_estado_sonido == 0:
        if utime.ticks_diff(tiempo_actual, ultimo_tiempo_sonido) > 500:
            led_encendido = not led_encendido
            if led_encendido:
                cambiar_color()
                print("RGB Encendido")
            else:
                apagar_rgb()
                print("RGB Apagado")
            ultimo_tiempo_sonido = tiempo_actual
    
    ultimo_estado_sonido = sonido_valor
    datos_sensores['sonido'] = sonido_valor == 1

def procesar_infrarrojo():
    if not programa_activo:
        return
        
    estado_ir = sensor_ir.value() == 0
    datos_sensores['infrarrojo'] = estado_ir
    
    if estado_ir:
        led1.value(1)
        mover_servo(180)
        print("Infrarrojo: Detectado")
    else:
        led1.value(0)
        mover_servo(0)
        print("Infrarrojo: No detectado")

def procesar_gas():
    if not programa_activo:
        return
        
    # Leer valores del sensor de gas
    gas_digital = mq2_digital.value() == 0
    gas_analog = mq2_analog.read_u16()
    
    datos_sensores['gas_digital'] = gas_digital
    datos_sensores['gas_analog'] = gas_analog
    
    # Activar LED si se detecta gas
    if gas_digital or gas_analog > umbral_gas:
        led_gas.on()
        print("Gas detectado")
    else:
        led_gas.off()
        print("Gas no detectado")

def actualizar_datos_sensores(timer):
    if not programa_activo:
        return
        
    procesar_infrarrojo()
    procesar_sonido()
    procesar_gas()
    # Los botones ahora son manejados por interrupciones
    
    try:
        dht_sensor.measure()
        datos_sensores['temperatura'] = dht_sensor.temperature()
        datos_sensores['humedad'] = dht_sensor.humidity()
        print(f"Temperatura: {datos_sensores['temperatura']:.1f}°C, Humedad: {datos_sensores['humedad']:.1f}%")
    except Exception as e:
        datos_sensores['temperatura'] = -999
        datos_sensores['humedad'] = -999
        print(f"Error leyendo DHT22: {e}")
    
    # Actualizar estados de los actuadores en datos_sensores
    datos_sensores['rgb'] = led_encendido

def mostrar_consola():
    if not programa_activo:
        return
        
    print("\033[2J\033[H")
    print("=== Estado de todos los sensores ===")
    if datos_sensores['ultrasonico'] >=0:
        print(f"Ultrasónico: {datos_sensores['ultrasonico']:.1f} cm")
    else:
        print("Ultrasónico: Error")
    print(f"Infrarrojo: {'Detectado' if datos_sensores['infrarrojo'] else 'No detectado'}")
    if datos_sensores['temperatura'] != -999:
        print(f"Temperatura: {datos_sensores['temperatura']:.1f}°C")
    else:
        print("Temperatura: Error")
    if datos_sensores['humedad'] != -999:
        print(f"Humedad: {datos_sensores['humedad']:.1f}%")
    else:
        print("Humedad: Error")
    print(f"Sonido: {'Detectado' if datos_sensores['sonido'] else 'No detectado'}")
    print(f"Gas Digital: {'Detectado' if datos_sensores['gas_digital'] else 'No detectado'}")
    print(f"Gas Analógico: {datos_sensores['gas_analog']}")
    print(f"RGB: {'Encendido' if datos_sensores['rgb'] else 'Apagado'}")
    print(f"LED Nuevo 1: {'Encendido' if datos_sensores['led_nuevo1'] else 'Apagado'}")
    print(f"LED Nuevo 2: {'Encendido' if datos_sensores['led_nuevo2'] else 'Apagado'}")
    print("================================")
    print("Presiona Ctrl+C para detener el programa")

def mostrar_datos(sensor):
    if not programa_activo:
        return
        
    global last_display
    linea1, linea2 = "", ""

    if sensor == 1:
        linea1 = "Ultrasonico"
        if datos_sensores['ultrasonico'] >=0:
            linea2 = f"Obj:{datos_sensores['ultrasonico']:.1f}cm"
        else:
            linea2 = "Obj: Error"
    elif sensor == 2:
        linea1 = "Infrarrojo"
        linea2 = "Obj detectado" if datos_sensores['infrarrojo'] else "Nada detectado"
    elif sensor == 3:
        linea1 = "Temp y Humedad"
        if datos_sensores['temperatura'] != -999:
            linea2 = f"T:{datos_sensores['temperatura']:.1f}C H:{datos_sensores['humedad']:.1f}%"
        else:
            linea2 = "Error leyendo"
    elif sensor == 4:
        linea1 = "Sensor Sonido"
        linea2 = "RGB ENCENDIDO" if datos_sensores['rgb'] else "RGB APAGADO"
    elif sensor == 5:  # Caso para el sensor de gas
        linea1 = "Sensor Gas"
        linea2 = f"Gas: {datos_sensores['gas_analog']}"

    # Rellenar manualmente con espacios hasta 16 caracteres
    def pad_line(line):
        return (line + ' ' * 16)[:16]

    # Actualizar solo las líneas que han cambiado
    if pad_line(linea1) != pad_line(last_display[0]):
        lcd.move_to(0, 0)
        lcd.putstr(pad_line(linea1))

    if pad_line(linea2) != pad_line(last_display[1]):
        lcd.move_to(0, 1)
        lcd.putstr(pad_line(linea2))

    last_display = [linea1, linea2]
    # Debug: Indicar actualización del LCD
    # print(f"LCD actualizado: {linea1} | {linea2}")

def cambiar_sensor(pin):
    global sensor_actual
    if not programa_activo:
        return
    
    sensor_actual += 1
    if sensor_actual > 5:  # Ajustado para incluir el sensor de gas
        sensor_actual = 1
    print(f"Cambiando a sensor {sensor_actual}")

def enviar_datos():
    if not programa_activo:
        return

    headers = {'Content-Type': 'application/json'}
    datos_para_enviar = []
    for sensor_name, device_info in device_mappings.items():
        dispositivo_id = device_info['id']
        tipo_dispositivo = device_info['tipo']
        valor = datos_sensores.get(sensor_name)

        # Convertir el valor a cadena según su tipo
        if isinstance(valor, bool):
            valor_str = '1' if valor else '0'
        elif isinstance(valor, float):
            valor_str = f"{valor:.2f}"
        elif isinstance(valor, int):
            valor_str = str(valor)
        else:
            valor_str = str(valor)

        # Determinar el usuario_id basado en el dispositivo_id
        # Ajusta esta lógica según tus necesidades
        if dispositivo_id == 3:
            usuario_id = '2'
        else:
            usuario_id = '1'

        # Añadir al arreglo de datos
        post_data = {
            'dispositivo_id': str(dispositivo_id),
            'tipo_dispositivo': tipo_dispositivo,
            'valor': valor_str,
            'usuario_id': usuario_id  # Ajusta el ID de usuario según corresponda
        }
        datos_para_enviar.append(post_data)

    # Enviar todos los datos en una sola solicitud
    try:
        json_data = ujson.dumps({'datos': datos_para_enviar})
        url = "http://192.168.114.179/CasaInteligente/php/insercion.php"  # Reemplaza con la URL de tu servidor
        response = requests.post(url, data=json_data, headers=headers, timeout=5)  # Aumentado timeout a 5s
        print("Status Code:", response.status_code)
        try:
            print("Respuesta del servidor:", response.text)
        except:
            pass
        if response.status_code == 200:
            print("Datos enviados exitosamente")
        else:
            print(f"Error al enviar datos. Estado: {response.status_code}")
        response.close()
    except Exception as e:
        print('Error al enviar datos:', e)

def limpiar_recursos():
    try:
        timer_ultrasonico.deinit()
        timer_actualizar.deinit()
        timer_envio.deinit()
        timer_mostrar_consola.deinit()
        led.value(0)
        led1.value(0)
        led_gas.value(0)
        led_nuevo1.value(0)
        led_nuevo2.value(0)
        red_pin.duty_u16(0)
        green_pin.duty_u16(0)
        blue_pin.duty_u16(0)
        servo.duty_u16(0)
        lcd.clear()
        lcd.backlight_off()
        print("Programa detenido correctamente")
    except Exception as e:
        print(f"Error al limpiar recursos: {e}")

# Configurar interrupciones para los botones
button_next.irq(trigger=Pin.IRQ_FALLING, handler=cambiar_sensor)

# Manejo de botones nuevos con interrupciones
def handle_button_nuevo1(pin):
    global led_nuevo1_state
    if not programa_activo:
        return
    # Toggle state
    led_nuevo1_state = not led_nuevo1_state
    led_nuevo1.value(led_nuevo1_state)
    datos_sensores['led_nuevo1'] = led_nuevo1_state
    print(f"LED Nuevo 1 {'Encendido' if led_nuevo1_state else 'Apagado'}")

def handle_button_nuevo2(pin):
    global led_nuevo2_state
    if not programa_activo:
        return
    # Toggle state
    led_nuevo2_state = not led_nuevo2_state
    led_nuevo2.value(led_nuevo2_state)
    datos_sensores['led_nuevo2'] = led_nuevo2_state
    print(f"LED Nuevo 2 {'Encendido' if led_nuevo2_state else 'Apagado'}")

button_nuevo1.irq(trigger=Pin.IRQ_FALLING, handler=handle_button_nuevo1)
button_nuevo2.irq(trigger=Pin.IRQ_FALLING, handler=handle_button_nuevo2)

# Configurar Timers para actualizar sensores y enviar datos
timer_actualizar = Timer()
timer_actualizar.init(freq=2, mode=Timer.PERIODIC, callback=actualizar_datos_sensores)  # 2Hz

timer_envio = Timer()
timer_envio.init(freq=0.2, mode=Timer.PERIODIC, callback=lambda t: enviar_datos())  # every 5 seconds

timer_mostrar_consola = Timer()
timer_mostrar_consola.init(freq=0.2, mode=Timer.PERIODIC, callback=lambda t: mostrar_consola())  # every 5 seconds

# Inicializar el Timer para el sensor ultrasónico a 5Hz
timer_ultrasonico.init(freq=5, mode=Timer.PERIODIC, callback=sensor_ult)

# Bucle principal para actualizar el LCD
try:
    while programa_activo:
        mostrar_datos(sensor_actual)
        utime.sleep_ms(50)  # Mantener el bucle principal ligero
except KeyboardInterrupt:
    print("\nDeteniendo el programa...")
    programa_activo = False
    limpiar_recursos()
    sys.exit()
    
except Exception as e:
    print(f"Error en el programa: {e}")
    programa_activo = False
    limpiar_recursos()
    sys.exit()