import paho.mqtt.client as mqtt
from utilities import iolookup, mqtt_broker_ip, mqtt_username, mqtt_key
from threading import Thread, Event
from time import sleep
from os import sep
from os.path import dirname, realpath
import socket
import weakref
from time import localtime, strftime


class EndableThread(Thread):
    def __init__(self, *args, **kwargs):
        Thread.__init__(self, *args, **kwargs)
        self.event = Event()

    def run(self):
        print("Running")
        while not self.event.is_set():
            self._target()
        print("Stopped")
        self.event.clear()
        Thread.__init__(self)

    def stop(self):
        self.event.set()
        print("Stopping")


class ControlExecution(EndableThread):
    def __init__(self, function, scan_time, parent):
        Thread.__init__(self)
        self.parent = weakref.ref(parent)
        self.holding_class = parent
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
            self.function(self, self.holding_class)
            self.event.wait(self.scan_time)
        print("Stopped")
        self.event.clear()
        Thread.__init__(self)


class ControlAlgorithm:
    def __init__(self, name, outputs, inputs, parameters, control_function, scan_time=1, testing=False):

        # self.outputs = outputs
        self.outputs = {}
        for o in outputs:
            self.outputs[o] = ""
        # self.inputs = inputs
        self.inputs = {}
        for i in inputs:
            self.inputs[i] = ""
        self.control_function = control_function
        self.ID = name
        self.scan_time = scan_time
        self.input_timeout_tries = 1
        # copy values from parameter list to build a full path to subscribe to changes
        self.parameter_values = parameters
        self.parameter_paths = parameters.fromkeys(parameters, "")
        self.testing_flag = testing
        self.complete_io_addresses()
        self.client = []
        if not self.testing_flag:
            self.client = mqtt.Client()
            self.client.username_pw_set(mqtt_username, mqtt_key)
            self.client.on_connect = on_connect
            # package data for the client to use during connection
            self.client.user_data_set([self.inputs.values(), self.ID,
                                       [self.update_parameter_values, self.update_input_buffer]])
            self.client.on_message = self.push_to_buffer
            self.client.connect(mqtt_broker_ip, 1883, 60)
            self.client.loop_start()
        else:
            self.dummy_client = EndableThread(target=self.listen_for_messages)
            self.dummy_client.start()
        self.input_buffer = {}
        self.execution = True
        # write initial parameter values to data broker
        for m in parameters:
            self.write(self.parameter_paths[m], self.parameter_values[m])
        self.main_program = ControlExecution(self.control_function, self.scan_time, self)
        self.main_program.output_function = self.write
        self.main_program.inputs = self.input_buffer
        self.main_program.parameters = self.parameter_values
        self.main_program.outputs = self.outputs
        self.execute()

    def update_parameter_values(self, name, value):
        self.parameter_values[name] = value

    def update_input_buffer(self, name, value):
        self.input_buffer[name] = value

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
        topic = message.topic.split("/")
        if topic[1] == self.ID:
            # if parameter value recieved write to parameters
            self.parameter_values[topic[-1]] = float(message.payload.decode())
        else:
            self.input_buffer[message.topic.split("/")[-1]] = float(message.payload.decode())

    def listen_for_messages(self):
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversocket.settimeout(self.scan_time)
        serversocket.bind(('localhost', 9000))
        try:
            serversocket.listen(5)  # become a server socket, maximum 5 connections
            connection, address = serversocket.accept()
            buf = connection.recv(64)
        except socket.timeout:
            pass
        else:
            # while True:
            if len(buf) > 0:
                splits = buf.decode().split(";")
                while len(splits) > 0:
                    # print(splits[0])
                    msg = splits[0].split(",")
                    # io/IOC1/in/TI100
                    # ctrl/any_name/SP1
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
                    splits.pop(0)

    def execute(self):
        # wait for all of the input buffer to have populated before executing the program
        count = 0
        while list(self.input_buffer.keys()) != list(self.inputs.keys()):
            sleep(self.scan_time)
            count += 1
            # check_all_inputs = set(self.input_buffer.keys()) not in set(self.inputs.keys())
            if count > self.input_timeout_tries:
                if self.testing_flag:
                    # stop concurrent threads
                    self.dummy_client.stop()
                print(self.input_buffer, self.inputs)
                raise TimeoutError("No input received in {} seconds since start".
                                   format(self.scan_time * self.input_timeout_tries))
        self.main_program.start()

    def stop(self):
        if self.main_program.is_alive():
            self.main_program.stop()
        if self.dummy_client.is_alive():
            self.dummy_client.stop()

    def start(self):
        if not self.main_program.is_alive():
            self.main_program.start()

# note that these methods for the MQTT client lie outside of the scope of the class

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    # subscribe to I/O inputs
    # For reference: self.client.user_data_set([self.inputs.values, self.ID])
    for i in userdata[0]:
        client.subscribe(i)
        client.message_callback_add(i, on_message)
    # subscribe to internal parameters
    handle = "ctrl/" + userdata[1] + "/#"
    client.subscribe(handle)
    client.message_callback_add(handle, on_message)

def on_message(client, userdata, message):
    print(userdata[1] + " received message '" + str(message.payload) + "' on topic '"
          + message.topic + "' with QoS " + str(message.qos))
    # temperature = float(message.payload.decode())
    topic = message.topic.split("/")
    value = float(message.payload.decode())
    if topic[1] == userdata[1]:
        # if parameter value recieved write to parameters
        update = userdata[2][0]
        update(topic[-1], value)
        # self.parameter_values[topic[-1]] = float(message.payload.decode())
    else:
        update = userdata[2][1]
        update(topic[-1], value)
        # self.input_buffer[message.topic.split("/")[-1]] = float(message.payload.decode())

class Historian(ControlAlgorithm):
    def __init__(self, name, outputs, inputs, parameters, control_function, scan_time=20, testing=True):
        start_time = strftime("%d%b%Y_%H-%M-%S", localtime())
        cwd = dirname(realpath(__file__)) + sep
        self.history_file = open(cwd + "databases" + sep + start_time + '.txt', 'w')
        self.history_file.write("Time," + ",".join(inputs) + '\n')
        # print(self.history_file.write("Time"))
        print("opened " + start_time + " log file")
        ControlAlgorithm.__init__(self, name, outputs, inputs, parameters, control_function, scan_time, testing)

    def stop(self):
        self.history_file.close()
        ControlAlgorithm.stop()


# if __name__ == '__main__':
#     # example usage of controller
#     # test initialization of program
#     # new syntax for input / output list
#     # out = {'EV100': "", 'EV101': "", 'EV102': "", 'EY100'
#     # : ""}
#     # ins = {'TI100': ""}
#     ins = ['TI100']
#     out = ['EV100', 'EV101', 'EV102', 'EY100']
#     param = {'SP1': 185, 'SP2': 155, 'SP3': 165, 'SP4': 185, 'SP5': 195, 'timeout': 8}
#
#     def make_cuts(self, parent_class):
#         # standard declarations
#         write = self.output_function
#         inputs = self.inputs
#         parameters = self.parameter_values
#         outputs = self.outputs
#
#         # temperature = ctof(inputs["TI100"])
#         # write(outputs['EV100'], int(parameters["SP1"] <= temperature < parameters["SP2"]))
#         # write(outputs['EV101'], int(parameters["SP2"] <= temperature < parameters["SP3"]))
#         # write(outputs['EV102'], int(parameters["SP3"] <= temperature < parameters["SP4"]))
#         # write(outputs['EY100'], int(parameters["SP1"] <= temperature < parameters["SP5"]))
#
#     c = ControlAlgorithm("StillSequence", out, ins, param, make_cuts, testing=True, scan_time=10)
#     print("nothing else happening")
#     sleep(26)
#     c.stop()

    # client side to test values to programs
    # import socket
    #
    # clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # clientsocket.connect(('localhost', 9000))
    # clientsocket.send('io/IOC1/in/TI100,82'.encode())
    # # clientsocket.send('ctrl/bleb/SP5,100'.encode())



