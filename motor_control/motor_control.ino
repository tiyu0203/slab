#include <Stepper.h>
// DC motor configuration 
#define DC1 10
#define DC2 11

// serial message decoding struct union thing 
union {
  struct cm {
    long step_speed;
    int  step_count;
    int  dc_speed;
    int  dc_count;
    int checksum;
  } s;
  char bytes[sizeof(cm)];
} buffer;

// stepper motor configuration 
Stepper altitude(200,4,6,7,5);

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  pinMode(DC1, OUTPUT);
  pinMode(DC2, OUTPUT);
}

// compute checksum to make sure received data is valid
int checksum() { 
  int sum = 0;
  for (int i=0; i<sizeof(buffer)-sizeof(sum); i++) {
    unsigned char temp = buffer.bytes[i];
    sum = sum + (unsigned char) buffer.bytes[i];
  }
  return sum;
}

void print_debug(int num) {
  Serial.print(num, DEC);
  Serial.print(' ');
  Serial.print(buffer.s.step_speed, DEC);
  Serial.print(' ');
  Serial.print(buffer.s.step_count, DEC);
  Serial.print(' ');
  Serial.print(buffer.s.dc_speed, DEC);
  Serial.print(' ');
  Serial.println(buffer.s.dc_count, DEC);
  int check = checksum();
  if (check != buffer.s.checksum) {
    Serial.print("Checksum didn't match: ");
    Serial.println(check, DEC);
  }
}

// number of steps to take for each program loop
// perhaps set to 1?
int n_steps = 10;
// start time for DC motor 
unsigned long start_time;

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available() > 0) {
    int num = Serial.readBytesUntil('\n', buffer.bytes, sizeof(buffer));
    print_debug(num); //disable debug for more speed 
    if ( sizeof(buffer) == num && buffer.s.checksum == checksum()) {
      altitude.setSpeed(buffer.s.step_speed);
      start_time = millis();
    } else { // invalid command received
      for (int i=0; i<sizeof(buffer); i++) {
        buffer[i] = 0; // null out the buffer
        // should probably have 2 buffers 
      }
    }
  }

  // set DC motor turning 
  if (buffer.s.dc_count > (millis() - start_time)) {
    // rotate the dc motor in the appropriate direction
    int rate = buffer.s.dc_speed;
    if (rate > 0) {
      analogWrite(DC1, rate);
      analogWrite(DC2, 0);
    } else {
      analogWrite(DC1, 0);
      analogWrite(DC2, -rate);
    }
  } else {
    // stop rotation
    analogWrite(DC1, 0);
    analogWrite(DC2, 0);
  }

  // Run some steps for stepper motor
  if (buffer.s.step_count / n_steps > 0) {
    altitude.step(n_steps);
    buffer.s.step_count -= n_steps;
  } else if (buffer.s.step_count / n_steps < 0) {
    altitude.step(-n_steps);
    buffer.s.step_count += n_steps;
  }

  
  
}
