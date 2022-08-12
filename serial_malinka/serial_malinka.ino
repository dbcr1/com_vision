#define dir_R 4
#define dir_L 7
#define speed_R 5
#define speed_L 6
#define START_BYTE 0xFF
#define END_BYTE 0xFE

void setup() {
  // put your setup code here, to run once:
  pinMode(4, OUTPUT);
  pinMode(5, OUTPUT);
  pinMode(6, OUTPUT);
  pinMode(7, OUTPUT);
  Serial.begin(115200);

}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available()){
    uint8_t first_byte = 0;
    Serial.readBytes(&first_byte, 1);
    if (first_byte != START_BYTE){
      return;
    }
    uint8_t buf[6] = {};
    buf[0] = first_byte;
    Serial.readBytes(buf+1, 5);
    if (buf[0] == START_BYTE && buf[5] == END_BYTE) {
      if (buf[1] == 1) {digitalWrite(dir_R, HIGH);}
      if (buf[1] == 0) {digitalWrite(dir_R, LOW);}
      analogWrite(speed_R, buf[2]);
      if (buf[3] == 1) {digitalWrite(dir_L, HIGH);}
      if (buf[3] == 0) {digitalWrite(dir_L, LOW);}
      analogWrite(speed_L, buf[4]);

    }
  }

}
