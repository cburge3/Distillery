import paho.mqtt.client as mqtt
from utilities import ctof

mqtt_hub_ip = '192.168.1.9'
prefix = 'io/IOC1/out/'
outputs = {'valve1': prefix + 'EV100', 'valve2': prefix + 'EV101', 'valve3': prefix + 'EV102', 'heating_element'
           : prefix + 'EY100'}
inputs = {'temp': 'io/IOC1/in/TI100'}

# setpoints = [165, 180, 190, 195]
setpoints = [18.5, 19, 19.5, 20, 20.5]

def tempchange(client, userdata, message):
    print("Received message '" + str(message.payload) + "' on topic '"
          + message.topic + "' with QoS " + str(message.qos))
    temperature = float(message.payload.decode())
    # temperature = ctof(temperature)
    print(temperature)
    client.publish(outputs['valve1'], int(setpoints[0] <= temperature < setpoints[1]))
    client.publish(outputs['valve2'], int(setpoints[1] <= temperature < setpoints[2]))
    client.publish(outputs['valve3'], int(setpoints[2] <= temperature < setpoints[3]))
    client.publish(outputs['heating_element'], int(setpoints[3] <= temperature < setpoints[4]))
    print(temperature < setpoints[3])
    # client.publish(outputs['heating_element'], int(temperature < setpoints[3]))



def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(inputs['temp'])
    client.message_callback_add(inputs['temp'], tempchange)


if __name__ == '__main__':
    client = mqtt.Client()
    client.username_pw_set('ionodes', '1jg?8jJ+Ut8,')
    client.on_connect = on_connect
    client.on_message = tempchange
    client.connect(mqtt_hub_ip, 1883, 60)
    client.loop_forever()


