from time import strftime, localtime, sleep
from os import fsync
import paho.mqtt.client as mqttClient
import threading
import subprocess

history_interval = 10
mqtt_hub_ip = '192.168.1.9'

scope = 'io/IOC1/in/#'
logfile = open("databases\\tempdata" + strftime("%a_%d_%b_%H_%M_%S", localtime()) + ".log", 'w')

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe('scope')


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    # assume that unique tag is last in the MQTT topic structure
    topic = msg.topic
    payload = msg.payload.decode()
    print(msg.topic+" "+msg.payload.decode())
    timestamp = strftime("%a %d %b %Y %H:%M:%S", localtime())
    logfile.write(','.join([timestamp, topic, payload]) + '\n')
    # make sure to push the python and windows buffers to the file in case of ungraceful exit
    logfile.flush()
    fsync(logfile.fileno())

def setup_historian():
    client = mqttClient.Client()
    client.username_pw_set('ionodes', '1jg?8jJ+Ut8,')
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(mqtt_hub_ip, 1883, 60)
    print("Connecting engine to MQTT server...")
    client.loop_start()


if __name__ == '__main__':
    client = mqttClient.Client()
    client.username_pw_set('ionodes', '1jg?8jJ+Ut8,')
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(mqtt_hub_ip, 1883, 60)
    print("Connecting engine to MQTT server...")
    client.loop_forever()

