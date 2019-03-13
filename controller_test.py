import socket
from time import sleep
from random import random
from math import sqrt
from utilities import ctof

for z in range(1,30):
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.connect(('localhost', 9000))
    clientsocket.send(str('io/IOC1/in/TI100,' + str(ctof(sqrt(30*z)+random()))
                          + ';io/IOC1/in/TI101,' + str(ctof(sqrt(30*z)+random()))).encode())
    sleep(10)
    # clientsocket.send('io/IOC1/in/TI101,47'.encode())
    # clientsocket.send('io/IOC1/in/TI100,' + str(randint(1,100)) + ''.encode())
    # clientsocket.send('io/IOC1/in/TI101,' + str(randint(1,100)) + ''.encode())
    # clientsocket.send('ctrl/bleb/SP5,100'.encode())