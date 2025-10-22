const int ledPin = 5;  // Broche de sortie PWM
float amplitude = 255.0;  // Amplitude maximale (0-255)
float periode = 20000.0;   // Période en millisecondes
unsigned long previousMillis = 0; // Pour le suivi du temps

void setup() {
  pinMode(ledPin, OUTPUT);
  Serial.begin(9600);
  Serial.println("Entrez la commande sous la forme: AMPLITUDE,PERIODE");
}

void loop() {
  // Lire les commandes entrantes pour modifier amplitude et période
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    parseCommand(command);
  }

  // Calcul du temps actuel
  unsigned long currentMillis = millis();

  // Générer le signal sinusoidal
  if (currentMillis - previousMillis >= 20) { // 20 ms pour ~50 Hz
    previousMillis = currentMillis;
    float t = (float)currentMillis / periode * 2 * PI; // Calcul du temps normalisé
    float value = (amplitude / 2.0) * (1 + sin(t)); // Formule de la sinusoïde (entre 0 et amplitude)
    analogWrite(ledPin, (int)value); // Ecriture PWM
  }
}

// Fonction pour parser les commandes entrantes
void parseCommand(String command) {
  int commaIndex = command.indexOf(',');

  if (commaIndex > 0) {
    String ampStr = command.substring(0, commaIndex);
    String periodStr = command.substring(commaIndex + 1);

    float newAmplitude = atof(ampStr.c_str());
    float newPeriode = atof(periodStr.c_str());

    if (newAmplitude >= 0 && newAmplitude <= 255 && newPeriode > 0) {
      amplitude = newAmplitude;
      periode = newPeriode;
      Serial.print("Amplitude mise à: ");
      Serial.println(amplitude);
      Serial.print("Période mise à: ");
      Serial.println(periode);
    } else {
      Serial.println("Valeurs invalides. Format: AMPLITUDE,PERIODE");
    }
  } else {
    Serial.println("Commande invalide. Utilisez: AMPLITUDE,PERIODE");
  }
}

