import serial
import time

# Configuración del puerto serial
arduino_port = "COM10"  # Cambia esto si el puerto es diferente
baud_rate = 9600       # Velocidad de comunicación (debe coincidir con el Serial.begin del Arduino)

try:
    # Abre la conexión serial
    arduino = serial.Serial(arduino_port, baud_rate, timeout=1)
    print(f"Conectado al puerto {arduino_port}")
    time.sleep(2)  # Esperar a que el puerto se inicialice

    while True:
        # Lee una línea desde el puerto serial
        data = arduino.readline().decode('utf-8').strip()

        # Verifica si hay datos válidos
        if data:
            print(f"Datos recibidos: {data}")

            # Separar los valores según el formato del Arduino
            if "Temperatura" in data:
                try:
                    # Extrae los valores clave del mensaje
                    parts = data.split(",")
                    temperatura = parts[0].split(":")[1]
                    humedad = parts[1].split(":")[1]
                    calidad_aire = parts[2].split(":")[1]
                    humedad_suelo = parts[3].split(":")[1]

                    # Mostrar los valores
                    print(f"Temperatura: {temperatura} °C")
                    print(f"Humedad: {humedad} %")
                    print(f"Calidad del Aire: {calidad_aire} PPM")
                    print(f"Humedad del Suelo: {humedad_suelo}")
                    print("-" * 30)

                except (IndexError, ValueError) as e:
                    print(f"Error al procesar los datos: {e}")

except serial.SerialException as e:
    print(f"Error al conectar con el puerto {arduino_port}: {e}")
except KeyboardInterrupt:
    print("\nConexión terminada por el usuario.")
finally:
    # Cierra la conexión serial si está abierta
    if 'arduino' in locals() and arduino.is_open:
        arduino.close()
        print("Conexión cerrada.")
