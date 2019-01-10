int pressurePin = 23;
int ledPin = 13;
int pressure = 0;

void setup() {
    pinMode(ledPin, OUTPUT);
    Serial.begin(9600);
    delay(1000);
}

void loop() {
    pressure = analogRead(pressurePin);
    Serial.println(pressure);
    digitalWrite(ledPin, HIGH);
    delay(1000);
    digitalWrite(ledPin, LOW);
    delay(1000);
}
