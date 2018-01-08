import paho.mqtt.client as mqtt

outputs = {'valve1': 'io/IOC1/EV100', 'valve2': 'io/IOC1/EV101', 'valve3': 'io/IOC1/EV102', 'heating_element'
           : 'io/IOC1/EY100'}
inputs = {'temp': 'io/IOC1/TT100'}
setpoints = [165, 180, 190, 195]


def tempchange(client, userdata, message):
    temperature = message.payload
    client.publish(outputs['valve1'], setpoints[0] <= temperature < setpoints[1])
    client.publish(outputs['valve2'], setpoints[1] <= temperature < setpoints[2])
    client.publish(outputs['valve3'], setpoints[2] <= temperature < setpoints[3])
    client.publish(outputs['heating_element'], temperature < setpoints[3])

    print("Received message '" + str(message.payload) + "' on topic '"
          + message.topic + "' with QoS " + str(message.qos))


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
    # client.on_message = on_message
    client.loop_start()


