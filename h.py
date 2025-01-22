import serial
import time

# Configura el puerto serie (asegúrate de usar el puerto correcto)
arduino_port = 'COM1'  # Cambia esto al puerto donde esté tu Arduino (en Windows usa 'COMx', en Linux usa '/dev/ttyUSB0')
baud_rate = 9600

# Establecer la conexión con el Arduino
ser = serial.Serial(arduino_port, baud_rate, timeout=1)

# Esperar un momento para asegurarnos de que la conexión se establece
time.sleep(2)

while True:
    try:
        # Leer los datos del puerto serie
        if ser.in_waiting > 0:
            data = ser.readline().decode('utf-8').strip()

            # Verificar si los datos contienen una coma (es decir, el formato esperado)
            if ',' in data:
                # Separar la temperatura y humedad
                temperature, humidity = data.split(',')
                print(f'Temperatura: {temperature} °C  Humedad: {humidity} %')
            else:
                print("Datos incorrectos recibidos:", data)

    except KeyboardInterrupt:
        print("Programa detenido por el usuario.")
        break

# Cerrar el puerto serie al terminar
ser.close()
