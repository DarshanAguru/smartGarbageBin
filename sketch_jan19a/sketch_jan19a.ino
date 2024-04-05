#include <Servo.h>

Servo myservo;

void setup() {
  Serial.begin(115200);
  myservo.attach(D5); // Assuming D5 is the pin connected to the servo
  myservo.write(0);
}

void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read();
    Serial.print(command);
    if (command == 'O') {
      myservo.write(180);
    } else if (command == 'C') {
      myservo.write(0); // Close position
    }
  }
  delay(50);
}
