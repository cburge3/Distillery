import socket

clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientsocket.connect(('localhost', 9000))
clientsocket.send('io/IOC1/in/TI100,83'.encode())
# clientsocket.send('ctrl/bleb/SP5,100'.encode())