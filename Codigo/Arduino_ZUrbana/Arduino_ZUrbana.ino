
#include <Buzzer.h>
#include <LiquidCrystal.h>
#include <DHT.h>




#define DHTPIN 9     // Pin donde está conectado el DHT11
#define DHTTYPE DHT11   // Tipo de sensor DHT
#define pinSensor A0 // Pin conectado al sensor MQ-135

int vee = 7; 
int rs = 6;
int e = 5;
int d4 = 4;
int d5 = 3;
int d6 = 2;
int d7 = 1;
int temperatura;
int humedad;
int buzz = 8;


DHT dth(DHTPIN, DHTTYPE);
LiquidCrystal lcd(rs,e,d4,d5,d6,d7); 
;

// Buzzer buzzer(buzz);

void setup(){
  dth.begin();
  Serial.begin(9600);  // Inicializa la comunicación serie
}

void loop() {
    
    

    // Temperatura y Humedad
    
    temperatura = dth.readTemperature();
    humedad = dth.readHumidity();
    
    // Calidad del Aire
    int dataPPM =  analogRead(A0);

    // HUmedad del suelo
    int dataHumS  = analogRead(A1);
    
    // Sonido
    if (temperatura >= 35 || dataPPM >= 650 || dataHumS >= 750){
      tone(buzz, 1500 ,40);
    }
    if (temperatura < 35 && dataPPM <= 650 && dataHumS <= 750){
      noTone(buzz);
    }
  
   if (isnan(temperatura) || isnan(humedad)) {
    Serial.println("Error: Sensor DHT no responde.");
    return;
  }

  Serial.print("Temperatura:");
  Serial.print(temperatura);
  Serial.print(",Humedad:");
  Serial.print(humedad);
  Serial.print(",CalidadAire:");
  Serial.print(dataPPM);
  Serial.print(",HumedadSuelo:");
  Serial.println(dataHumS);
  
  delay(500);
}

