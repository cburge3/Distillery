import paho.mqtt.client as mqtt
from utilities import ctof, iolookup, mqtt_broker_ip, mqtt_username, mqtt_key
from threading import Thread, Event
from time import sleep
import socket


class ControlExecution(Thread):
    def __init__(self, function, scan_time):
        Thread.__init__(self)
        self.function = function
        self.event = Event()
        self.scan_time = scan_time
        self.output_function = None
        self.inputs = None
        self.parameters = None
        self.outputs = None

    def run(self):
        print("Running")
        while not self.event.is_set():
            self.function(self)
            self.event.wait(self.scan_time)
        print("Stopped")
        self.event.clear()
        Thread.__init__(self)

    def stop(self):
        self.event.set()
        print("Stopping")


class ControlAlgorithm:
    def __init__(self, name, outputs, inputs, parameters, control_function, scan_time=10, testing=False):

        self.outputs = outputs
        self.inputs = inputs
        self.control_function = control_function
        self.ID = name
        self.scan_time = scan_time
        self.input_timeout_tries = 3
        # copy keys from parameter list to build a full path to subscribe to changes
        self.parameter_values = parameters
        self.parameter_paths = parameters.fromkeys(parameters, "")
        self.testing_flag = testing
        self.complete_io_addresses()
        if not self.testing_flag:
            self.client = mqtt.Client()
            self.client.username_pw_set(mqtt_username, mqtt_key)
            self.client.on_connect = self.on_connect
            self.client.on_message = self.push_to_buffer
            self.client.connect(mqtt_broker_ip, 1883, 60)
            self.client.loop_forever()
        else:
            self.dummy_client = Thread(target=self.listen_for_messages)
            self.dummy_client.start()
        self.input_buffer = {}
        self.execution = True
        # write initial parameter values to data broker
        for m in parameters:
            self.write(self.parameter_paths[m], self.parameter_values[m])
        # self.output_function = None
        # self.inputs = None
        # self.parameters = None
        # self.outputs = None
        self.main_program = ControlExecution(self.control_function, 30)
        self.main_program.output_function = self.write
        self.main_program.inputs = self.input_buffer
        self.main_program.parameters = self.parameter_values
        self.main_program.outputs = self.outputs
        self.execute()

    def complete_io_addresses(self):
        for o in self.outputs:
            self.outputs[o] = iolookup(o)
        for i in self.inputs:
            self.inputs[i] = iolookup(i)
        for key in self.parameter_paths:
            self.parameter_paths[key] = "ctrl/" + self.ID + "/" + key

    def write(self, address, value):
        if not self.testing_flag:
            self.client.publish(address, value)
        else:
            print("{1} written to {0}".format(address, value))

    def push_to_buffer(self, userdata, message):
        print("Received message '" + str(message.payload) + "' on topic '"
              + message.topic + "' with QoS " + str(message.qos))
        # temperature = float(message.payload.decode())
        self.input_buffer[message.topic.split("/")[-1]] = float(message.payload.decode())

    def on_connect(self, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        # subscribe to I/O inputs
        for i in self.inputs.values():
            self.client.subscribe(i)
            self.client.message_callback_add(i, self.push_to_buffer)
        # subscribe to internal parameters
        handle = "ctrl/" + self.ID + "/#"
        self.client.subscribe(handle)
        self.client.message_callback_add(handle, self.push_to_buffer)

    def listen_for_messages(self):
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversocket.bind(('localhost', 9000))
        serversocket.listen(5)  # become a server socket, maximum 5 connections

        while True:
            connection, address = serversocket.accept()
            buf = connection.recv(64)
            if len(buf) > 0:
                msg = buf.decode().split(",")
                # io/IOC1/in/TI100
                # ctrl/StillSequence/SP1
                print("test value accepted", msg[0], msg[1])
                address = msg[0]
                value = msg[1]
                address = address.split("/")
                if address[0] == 'io':
                    print("{0} written to address {1}".format(value, address[-1]))
                    self.input_buffer[address[-1]] = float(value)
                elif address[0] == 'ctrl':
                    print("{0} written to address {1}".format(value, address[-1]))
                    self.parameter_values[address[-1]] = float(value)

    def execute(self):
        # wait for all of the input buffer to have populated before executing the program
        print(self.input_buffer, self.inputs)
        count = 0
        while self.input_buffer.keys() != self.inputs.keys():
            sleep(self.scan_time)
            count += 1
            if count > self.input_timeout_tries:
                raise TimeoutError("No response from inputs")
        self.main_program.start()


if __name__ == '__main__':
    # test initialization of program
    out = {'EV100': "", 'EV101': "", 'EV102': "", 'EY100'
    : ""}
    ins = {'TI100': ""}
    param = {'SP1': 60, 'SP2': 155, 'SP3': 165, 'SP4': 185, 'SP5': 195}

    def make_cuts(self):
        # standard declarations
        write = self.output_function
        inputs = self.inputs
        parameters = self.parameters
        outputs = self.outputs

        temperature = ctof(inputs["TI100"])
        write(outputs['EV100'], int(parameters["SP1"] <= temperature < parameters["SP2"]))
        write(outputs['EV101'], int(parameters["SP2"] <= temperature < parameters["SP3"]))
        write(outputs['EV102'], int(parameters["SP3"] <= temperature < parameters["SP4"]))
        write(outputs['EY100'], int(parameters["SP1"] <= temperature < parameters["SP5"]))

    c = ControlAlgorithm("StillSequence", out, ins, param, make_cuts, testing=True)


