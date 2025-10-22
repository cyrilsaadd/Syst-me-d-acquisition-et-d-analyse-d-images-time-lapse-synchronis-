const int ledPin = 5;  // Broche de la LED

void setup() {
  pinMode(ledPin, OUTPUT);
  analogWrite(ledPin, 0);  // Assure que la LED est éteinte au départ
  Serial.begin(9600);  // Initialisation de la communication série
  Serial.println("Arduino prêt. En attente de commandes.");
}

void loop() {
  if (Serial.available() > 0) {  // Vérifie si un message est reçu
    String command = Serial.readStringUntil('\n');  // Lire la commande jusqu'à la nouvelle ligne

    if (command.startsWith("LUM=")) {
      int pwm_value = command.substring(4).toInt();  // Extraire la valeur PWM après "LUM="
      if (pwm_value >= 0 && pwm_value <= 255) {
        analogWrite(ledPin, pwm_value);  // Modifier l'intensité de la LED
        Serial.print("Intensité de la LED mise à: ");
        Serial.println(pwm_value);
      } else {
        Serial.println("Valeur PWM invalide. Doit être entre 0 et 255.");
      }
    } 
    else if (command == "OFF") {
      analogWrite(ledPin, 0);  // Éteindre la LED
      Serial.println("LED éteinte.");
    }
  }
}

