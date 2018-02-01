#include <Boards.h>
#include <Firmata.h>

/*
 Sketch which publishes temperature data from a DS1820 sensor to a MQTT topic.
 This sketch goes in deep sleep mode once the temperature has been sent to the MQTT
 topic and wakes up periodically (configure SLEEP_DELAY_IN_SECONDS accordingly).
 Hookup guide:
 - connect D0 pin to RST pin in order to enable the ESP8266 to wake up periodically
 - DS18B20:
     + connect VCC (3.3V) to the appropriate DS18B20 pin (VDD)
     + connect GND to the appopriate DS18B20 pin (GND)
     + connect D4 to the DS18B20 data pin (DQ)
     + connect a 4.7K resistor between DQ and VCC.

 15-Jan-18
 HIGH is low and LOW is high see github
*/

#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <Streaming.h>

// Communication settings

const char* ssid = "SlauterWireless2G";
const char* password = "falconpunch";
const char* mqtt_server = "192.168.1.9";
const char* mqtt_username = "ionodes";
const char* mqtt_password = "1jg?8jJ+Ut8,";
const char* temp_topic = "io/IOC1/in/TI100";
const char* subscription = "io/IOC1/out/#";
const char* delim = "/";

// IO Declarations

const uint8_t EV100 = D1;
const uint8_t EV101 = D2;
const uint8_t EV102 = D3;
const uint8_t ONE_WIRE_BUS = D4;
const uint8_t EY100 = D5;

// Other global setup

WiFiClient espClient;
PubSubClient client(espClient);

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature DS18B20(&oneWire);
char temperatureString[6];

unsigned long previousMillis = 0;
unsigned long inputScanRate = 10000;

void callback(char* topic, byte* payload, unsigned int length) {
  char asciiPayload[length];
  for (int i = 0; i < length; i++) {
    //Serial.print((char)payload[i]);
    asciiPayload[i] = (char)payload[i];
  }
  Serial.println();
  //convert character array payload to integer
  int payloadNumeric = atoi(asciiPayload);
  char* address;
  bool output;
  output = payloadNumeric;
  //IO is inverted in the ESP8266
  output = !output;
  address = strtok(topic, delim);
  //the target IO should be the 0,1,2nd,3rd piece of the topic
  for (int i = 0; i < 3; i++){
    address = strtok(NULL, delim);
  }
  Serial.print("Writing to ");
  Serial.print(address);
  Serial.print(" with a value of ");
  Serial.print(!output);
  
  if (strcmp(address, "EV100") == 0){
    digitalWrite(EV100, output);
  };
  if (strcmp(address, "EV101") == 0 ){
    digitalWrite(EV101, output);
  };
  if (strcmp(address, "EV102") == 0 ){
    digitalWrite(EV102, output);
  };
  if (strcmp(address, "EY100") == 0 ){
    digitalWrite(EY100, output);
  };
  Serial.println();
}

void setup() {
  // setup serial port
  Serial.begin(115200);
  // setup WiFi
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
  //setup pins
  pinMode(EY100, OUTPUT);
  pinMode(EV100, OUTPUT);
  pinMode(EV101, OUTPUT);
  pinMode(EV102, OUTPUT);
  // Initialize values 
  digitalWrite(EV100, HIGH);
  digitalWrite(EV101, HIGH);
  digitalWrite(EV102, HIGH);
  digitalWrite(EY100, HIGH);
  
  // setup OneWire bus
  DS18B20.begin();
}

void setup_wifi() {
  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  IPAddress ip(192, 168, 1, 43); // where xx is the desired IP Address
  IPAddress gateway(192, 168, 1, 1); // set gateway to match your network
  IPAddress subnet(255, 255, 255, 0); // set subnet mask to match your network
  WiFi.begin(ssid, password);
  WiFi.config(ip, gateway, subnet);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect
    if (client.connect("ESP8266Client", mqtt_username, mqtt_password)) {
      Serial.println("connected");
      // Do subscriptions here so the client resubscribe on a reconnect
      client.subscribe(subscription);
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

float getTemperature() {
  float temp;
  DS18B20.requestTemperatures(); 
  temp = DS18B20.getTempCByIndex(0);
  return temp;
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis > inputScanRate) {
    float temperature = getTemperature();
    if (temperature != 85.0 || temperature != -127.00) {
      // convert temperature to a string with two digits before the comma and 2 digits for precision
      dtostrf(temperature, 2, 2, temperatureString);
      // send temperature to the serial console
      Serial << "Sending temperature: " << temperatureString << endl;
      // send temperature to the MQTT topic
      client.publish(temp_topic, temperatureString);
      previousMillis = currentMillis;
    }
  }
}
