#include <OneWire.h>
#include <DallasTemperature.h>
#define ONE_WIRE_BUS 2

// Setup a oneWire instance to communicate with any OneWire devices 
// (not just Maxim/Dallas temperature ICs)
OneWire oneWire(ONE_WIRE_BUS);

// Pass our oneWire reference to Dallas Temperature.
DallasTemperature sensors(&oneWire);

byte inByte;
//inputs always wrt direction of from the field
const long inputUpdateRate = 1000;
const int tempIndBus = 0;
unsigned long previousMillis = 0;
const int discreteOut = 3;
// these are so we don't get overwhelmed with commands and still report data
int outputCounter = 0;
const int maxConsecutiveCommands = 5;


void setup(void)
{
  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }
  // Start up the library
  sensors.begin();
  pinMode(discreteOut, OUTPUT);
}


void loop() {
  unsigned long currentMillis = millis();
  // if we get an instruction byte, parse and execute commands from controller:
  if ((Serial.available() > 0) && (outputCounter < maxConsecutiveCommands)) {
    outputCounter ++;
    // get incoming byte:
    inByte = Serial.read();
      // make sure we are receiving a command byte:
  
      // parse and execute commands from controller
  
      if (bitRead(inByte, 0) == 0) {
        //discrete output
        int address = inByte >> 2;
        bool discreteCommand = bitRead(inByte, 1);
        //Serial.print(address);
        //Serial.print(discreteCommand, BIN);
        digitalWrite(address, discreteCommand);
      }
      else {
        int address = inByte >> 2;
        int analogCommand = Serial.read();
        analogWrite(address, analogCommand * 4);
        //analog output
        
      }
    // Do instructions contained within the byte
  }
  // otherwise get inputs from the field and send to controller
  else {
    if (currentMillis - previousMillis >= inputUpdateRate) {
      // send all input data from card here
      outputCounter = 0;
      sensors.requestTemperatures();
      Serial.print(sensors.getTempCByIndex(tempIndBus));
      Serial.print('\n');
      previousMillis = currentMillis;
    }
  }
}

