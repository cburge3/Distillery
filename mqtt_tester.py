import paho.mqtt.client as mqtt
from time import sleep

RPI_IP = '192.168.1.22'

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("test")

def on_publish(client, userdata, packet):
    print('publish success')

outputs = {'valve1': 'io/IOC1/EV100', 'valve2': 'io/IOC1/EV101', 'valve3': 'io/IOC1/EV102', 'heating_element'
           : 'io/IOC1/EY100'}
inputs = {'temp': 'io/IOC1/TT100'}

client = mqtt.Client()
client.username_pw_set('ionodes', '1jg?8jJ+Ut8,')
client.on_connect = on_connect
client.on_publish = on_publish
client.connect(RPI_IP, 1883, 60)
client.loop_start()
client.publish(outputs['heating_element'], 1)
sleep(3)
client.disconnect()