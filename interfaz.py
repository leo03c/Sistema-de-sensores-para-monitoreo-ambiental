import sys
import time
import serial
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QWidget
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis
from PyQt5.QtGui import QPainter
import psycopg2
import logging

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("sensor_interface.log"),
        logging.StreamHandler()
    ]
)

# Configuración de la conexión serial al Arduino
ARDUINO_PORT = "COM10"  # Cambia esto si el puerto es diferente
BAUD_RATE = 9600

# Configuración de la base de datos PostgreSQL
DB_CONFIG = {
    "dbname": "PID",
    "user": "postgres",  # Cambia esto a tu usuario de PostgreSQL
    "password": "1210",  # Cambia esto a tu contraseña de PostgreSQL
    "host": "localhost",
    "port": 5432
}

class SensorInterface(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Monitoreo de Sensores")
        self.setGeometry(100, 100, 1200, 400)
        self.init_ui()
        self.arduino = self.inicializar_arduino()
        self.db_conn = self.inicializar_db()
        self.timer = QTimer()
        self.timer.timeout.connect(self.mostrar_valor_actual)
        self.lectura_activa = False
        self.tiempo = 0

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        main_layout = QHBoxLayout()

        # Panel de datos
        data_layout = QVBoxLayout()

        self.title_label = QLabel("Sistema de Monitoreo de Sensores", self)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #2C3E50;")
        data_layout.addWidget(self.title_label)

        # Tarjetas de datos
        self.temp_label = self.crear_tarjeta("Temperatura: -- °C", "#2980B9")
        self.hum_label = self.crear_tarjeta("Humedad: -- %", "#27AE60")
        self.air_quality_label = self.crear_tarjeta("Calidad del Aire: -- %", "#8E44AD")
        self.soil_moisture_label = self.crear_tarjeta("Humedad del Suelo: -- %", "#D35400")

        data_layout.addWidget(self.temp_label["widget"])
        data_layout.addWidget(self.hum_label["widget"])
        data_layout.addWidget(self.air_quality_label["widget"])
        data_layout.addWidget(self.soil_moisture_label["widget"])

        self.start_button = QPushButton("Iniciar Lectura", self)
        self.start_button.setStyleSheet("""QPushButton { background-color: #1ABC9C; color: white; font-size: 20px; padding: 15px; border-radius: 12px; text-align: center; } QPushButton:hover { background-color: #16A085; } QPushButton:pressed { background-color: #1C7C6B; }""")
        self.start_button.setCursor(Qt.PointingHandCursor)
        self.start_button.clicked.connect(self.toggle_lectura)
        data_layout.addWidget(self.start_button)

        main_layout.addLayout(data_layout)

        # Panel de gráficos
        self.chart = QChart()
        self.chart.setTitle("Valores de Sensores")
        self.chart.setAnimationOptions(QChart.SeriesAnimations)

        self.series_temp = QLineSeries()
        self.series_temp.setName("Temperatura")
        self.series_hum = QLineSeries()
        self.series_hum.setName("Humedad")
        self.series_air_quality = QLineSeries()
        self.series_air_quality.setName("Calidad del Aire")
        self.series_soil_moisture = QLineSeries()
        self.series_soil_moisture.setName("Humedad del Suelo")

        self.chart.addSeries(self.series_temp)
        self.chart.addSeries(self.series_hum)
        self.chart.addSeries(self.series_air_quality)
        self.chart.addSeries(self.series_soil_moisture)

        self.axis_x = QValueAxis()
        self.axis_x.setTitleText("Tiempo")
        self.axis_x.setLabelFormat("%d")
        self.axis_x.setTickCount(20)
        self.chart.addAxis(self.axis_x, Qt.AlignBottom)

        self.axis_y = QValueAxis()
        self.axis_y.setTitleText("Mediciones")
        self.axis_y.setLabelFormat("%.1f")
        self.chart.addAxis(self.axis_y, Qt.AlignLeft)

        for series in [self.series_temp, self.series_hum, self.series_air_quality, self.series_soil_moisture]:
            series.attachAxis(self.axis_x)
            series.attachAxis(self.axis_y)

        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        main_layout.addWidget(self.chart_view)

        self.central_widget.setLayout(main_layout)

    def crear_tarjeta(self, texto, color):
        tarjeta = QWidget(self)
        tarjeta.setStyleSheet(f"background-color: {color}; border-radius: 15px; padding: 20px;")
        layout = QVBoxLayout(tarjeta)
        label = QLabel(texto, tarjeta)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 20px; color: white;")
        layout.addWidget(label)
        return {"widget": tarjeta, "label": label}

    def inicializar_arduino(self):
        try:
            arduino = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=1)
            logging.info(f"Conectado al puerto {ARDUINO_PORT}")
            time.sleep(2)  # Esperar a que el puerto se inicialice
            return arduino
        except serial.SerialException as e:
            logging.critical(f"Error al conectar con Arduino: {e}")
            return None

    def inicializar_db(self):
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            logging.info("Conexión a la base de datos exitosa.")
            return conn
        except psycopg2.Error as e:
            logging.critical(f"Error al conectar a la base de datos: {e}")
            return None

    def toggle_lectura(self):
        if self.lectura_activa:
            self.timer.stop()
            self.lectura_activa = False
            self.start_button.setText("Iniciar Lectura")
            logging.info("Lectura detenida.")
        else:
            if self.arduino:
                self.timer.start(1000)
                self.lectura_activa = True
                self.start_button.setText("Detener Lectura")
                logging.info("Lectura automática iniciada.")

    def guardar_datos_db(self, timestamp, temperatura, humedad, calidad_aire, humedad_suelo):
        if self.db_conn:
            try:
                with self.db_conn.cursor() as cursor:
                    query = """
                    INSERT INTO mediciones (timestamp, temperatura, humedad, calidad_aire, humedad_suelo)
                    VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor.execute(query, (timestamp, temperatura, humedad, calidad_aire, humedad_suelo))
                    self.db_conn.commit()
                    logging.info("Datos guardados en la base de datos.")
            except psycopg2.Error as e:
                logging.error(f"Error al guardar en la base de datos: {e}")

    def mostrar_valor_actual(self):
        if self.arduino and self.arduino.in_waiting > 0:
            data = self.arduino.readline().decode('utf-8').strip()

            if data:
                try:
                    parts = data.split(",")
                    temperatura = float(parts[0].split(":")[1])
                    humedad = float(parts[1].split(":")[1])

                    # Escala de humedad del aire (asumir valor de 0 a 1023)
                    calidad_aire_raw = float(parts[2].split(":")[1])  # Valor de calidad del aire
                    humedad_suelo_raw = float(parts[3].split(":")[1])  # Valor de humedad del suelo

                    # Convertir a porcentaje
                    calidad_aire_porcentaje = (calidad_aire_raw / 1000) * 100  # Asumiendo máximo de 1000
                    humedad_suelo_porcentaje = (humedad_suelo_raw / 1023) * 100  # Asumiendo máximo de 1023

                    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

                    # Agregar datos a las series
                    self.series_temp.append(self.tiempo, temperatura)
                    self.series_hum.append(self.tiempo, humedad)
                    self.series_air_quality.append(self.tiempo, calidad_aire_porcentaje)
                    self.series_soil_moisture.append(self.tiempo, humedad_suelo_porcentaje)

                    # Actualizar las tarjetas de valores
                    self.temp_label["label"].setText(f"Temperatura: {temperatura:.2f} °C")
                    self.hum_label["label"].setText(f"Humedad: {humedad:.2f} %")
                    self.air_quality_label["label"].setText(f"Calidad del Aire: {calidad_aire_porcentaje:.2f} %")
                    self.soil_moisture_label["label"].setText(f"Humedad del Suelo: {humedad_suelo_porcentaje:.2f} %")

                    # Calcular el valor máximo dinámico del eje Y
                    max_value = max(
                        max([p.y() for p in self.series_temp.pointsVector()], default=0),
                        max([p.y() for p in self.series_hum.pointsVector()], default=0),
                        max([p.y() for p in self.series_air_quality.pointsVector()], default=0),
                        max([p.y() for p in self.series_soil_moisture.pointsVector()], default=0)
                    )
                    max_value += 10  # Margen adicional superior

                    # Ajustar rangos de los ejes
                    self.axis_x.setRange(0, self.tiempo + 10)
                    self.axis_y.setRange(0, max_value)

                    # Guardar datos en la base de datos
                    self.guardar_datos_db(timestamp, temperatura, humedad, calidad_aire_porcentaje, humedad_suelo_porcentaje)

                    self.tiempo += 1
                except (IndexError, ValueError) as e:
                    logging.error(f"Error al procesar los datos: {data} - {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = SensorInterface()
    ventana.show()
    sys.exit(app.exec_())
