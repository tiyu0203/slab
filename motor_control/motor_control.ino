#include <Stepper.h>
#include <avr/interrupt.h>
// DC motor configuration 
#define DC1 10
#define DC2 11

// pan limit switches
#define PLIM1 A0 
#define PLIM2 A1
// tilt/altitude limit switches 
#define TLIM1 A2
#define TLIM2 A3

#define ISRDELAY 10

#define sign(x) ((x>0)-(x<0))

// serial message decoding struct union thing 
union {
  struct cm {
    long step_speed;
    int  step_count;
    int  dc_speed;
    unsigned int  dc_count;
    int checksum;
  } s;
  char bytes[sizeof(cm)];
} buffer;

// stepper motor configuration 
Stepper altitude(200,4,6,7,5);

byte lim_state;

void limit_check()
{ 
  // should probably replace with analog read but whatever
  if (~PINC & 0x01) {
    // shut down if moving in direction of limit switch, otherwise do nothing
    if (buffer.s.dc_speed > 0)
      buffer.s.dc_count = 0;
      lim_state |= 0x01;
  }
  if (~PINC & 0x02) {
    if (buffer.s.dc_speed < 0)
      buffer.s.dc_count = 0;
      lim_state |= 0x02;
  }
  if (~PINC & 0x04) {
    if (buffer.s.step_count > 0)
      buffer.s.step_count = 0;
      lim_state |= 0x04;
  }
  if (~PINC & 0x08) {
    if (buffer.s.step_count < 0)
      buffer.s.step_count = 0;
      lim_state |= 0x08;
  }
}

ISR(PCINT1_vect) 
{
  limit_check();
}

void setup() {
  // put your setup code here, to run once:
  pinMode(DC1, OUTPUT);
  pinMode(DC2, OUTPUT);

  pinMode(PLIM1, INPUT_PULLUP);
  pinMode(PLIM2, INPUT_PULLUP);
  pinMode(TLIM1, INPUT_PULLUP);
  pinMode(TLIM2, INPUT_PULLUP);
  
  cli();
  PCICR |= 0x02;
  PCMSK1 |= 0x0F;
  sei();
  
  Serial.begin(115200);
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
  Serial.print(lim_state, HEX);
  //Serial.print(num, DEC);
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
int n_steps = 1; //this has some issues, don't know if necessary
// start time for DC motor 
unsigned long start_time;

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available() > 0) {
    int num = Serial.readBytes(buffer.bytes, sizeof(buffer));
    if ( sizeof(buffer) == num && buffer.s.checksum == checksum()) {
      lim_state = 0;
      limit_check();
      //print_debug(num);
      altitude.setSpeed(buffer.s.step_speed);
      start_time = millis();
    } else { 
      // invalid command received
      // null out the buffer
      //Serial.println("Invalid data");
      for (int i=0; i<sizeof(buffer); i++) {
        buffer.bytes[i] = 0;
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

  if (buffer.s.step_count / n_steps) {
    altitude.step(sign(buffer.s.step_count) * n_steps);
    buffer.s.step_count -= sign(buffer.s.step_count)*n_steps;
  }
}
