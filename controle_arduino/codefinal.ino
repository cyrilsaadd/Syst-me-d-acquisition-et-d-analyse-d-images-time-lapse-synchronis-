const int ledPin = 5;  // Broche de la LED

void setup() {
  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, LOW);  // Assurer que la LED est éteinte au départ
  Serial.begin(9600);  // Initialisation de la communication série
}

void loop() {
  if (Serial.available() > 0) {  // Vérifie si un message est reçu
    String command = Serial.readStringUntil('\n');  // Lire la commande

    if (command == "ON") {
      digitalWrite(ledPin, HIGH);  // Allumer la LED
    } 
    else if (command == "OFF") {
      digitalWrite(ledPin, LOW);  // Éteindre la LED
    }
  }
}
