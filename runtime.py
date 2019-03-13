from controller import Historian, ControlAlgorithm
from time import localtime, strftime
from os import fsync
from utilities import ctof

# example usage of controller
# test initialization of program
out = []
ins = ['TI100', 'TI101']
param = {}


def update(self, parent):
    write = self.output_function
    inputs = self.inputs
    parameters = self.parameters
    outputs = self.outputs
    parent.history_file.write(strftime("%H:%M:%S", localtime()) + ","
                            + str(inputs["TI100"]) + "," + str(inputs["TI101"]) + '\n')
    parent.history_file.flush()
    fsync(parent.history_file.fileno())

a = Historian("HISTORIAN", out, ins, param, update, testing=False, scan_time=15)

# example usage of controller
# test initialization of program
out1 = ['EV100']
ins1 = ['TI100']
param1 = {'acknowledge': 0, 'new': 0, 'limit': 150}


def alarm1(self, parent_class):
    # standard declarations
    write = self.output_function
    inputs = self.inputs
    parameters = self.parameters
    outputs = self.outputs
    print(write, inputs, parameters, outputs)
    temperature = ctof(inputs["TI100"])
    write(outputs['EV100'], int(parameters["limit"] <= temperature))


b = ControlAlgorithm("TAH100", out1, ins1, param1, alarm1, scan_time=15)
# b.start()