from serial import Serial
from opcua import Client
from opcua.ua import NumericNodeId
from queue import Queue
from time import sleep

# globals
COMPORT = 'COM3'
# COMPORT = 'COM10'
BAUDRATE = '9600'
SERVER = "opc.tcp://localhost:4840/freeopcua/server/"
MONITORED_NODES = [(4,2)]
OUTPUT_NODES = [(2,2)]
# a full list of monitored nodes would be built like this:
# [(index1, namespace1), (index2, namespace2)]
# temporary until we have a database of the structure
q = Queue()


def truncate(f, n):
    # Truncates/pads a float f to n decimal places without rounding
    s = '{}'.format(f)
    if 'e' in s or 'E' in s:
        return '{0:.{1}f}'.format(f, n)
    i, p, d = s.partition('.')
    return '.'.join([i, (d + '0' * n)[:n]])


def ctof(c):
    # Celcius to Fahrenheit
    return float(c) * 9 / 5 + 32

class USBInterface:
    def __init__(self, comport=COMPORT, baudrate=BAUDRATE, timeout=0, server=SERVER, values=MONITORED_NODES):
        self._port = Serial(comport, baudrate)
        self._client = Client(server)
        self._client.connect()
        self.nodes = values
        self._handler = SubHandler()
        self._sub = self._client.create_subscription(1000, self._handler)
        for n in self.nodes:
            z = self._client.get_node(NumericNodeId(n[0],n[1]))
            self._sub.subscribe_data_change(z)

    def start(self):
        buffer = ''
        temp = self._client.get_node(NumericNodeId(2,2))
        while True:
            # poll server for any outbound messages
            if q.empty():
                line = self._port.readline()
                # see if readuntil(\n) is a better usage here
                if line != b'':
                    line = str(line, 'utf-8')
                    if '\n' not in line:
                        # no newline - add to buffer
                        buffer += line
                    else:
                        # eo transmission append buffer broadcast value
                        buffer += (line.split('\n')[0])
                        # print(buffer)
                        temp.set_value(str(truncate(ctof(buffer), 2)))
                        buffer = ''
            else:
                message = self.createmessage()
                if type(message) is int:
                    print(message)
                    self._port.write([message])
                else:
                    for m in message:
                        self._port.write(m)

    def createmessage(self):
        command = q.get()
        # lookup node info against database or OPC tree here - hardcoded values right now
        discrete = True
        address = 3
        # initialize messages
        msg1 = 0
        msg2 = -1
        if discrete:
            #type bit is 0, write command bit
            msg1 |= command[1] << 1
        else:
            # write type bit
            msg1 |= 1 << 0
            # write output value
            msg2 = command[1]
        # add address
        msg1 |= address << 2
        q.task_done()
        if msg2 != -1:
            return msg1, msg2
        else:
            return msg1



class SubHandler(object):
    """
    Subscription Handler. To receive events from server for a subscription
    data_change and event methods are called directly from receiving thread.
    Do not do expensive, slow or network operation there. Create another
    thread if you need to do such a thing
    """

    def datachange_notification(self, node, val, data):
        print("Python: New data change event", node, val)
        q.put((node, val))

    def event_notification(self, event):
        print("Python: New event", event)


def monitorlink():
    ser = Serial(COMPORT, BAUDRATE, timeout=0)
    buffer = ''

    while True:
        # poll server for any outbound messages
        line = ser.readline()
        if line != b'':
            line = str(line, 'utf-8')
            if '\n' not in line:
                # no newline - add to buffer
                buffer += line
            else:
                # eo transmission append buffer broadcast value
                buffer += (line.split('\n')[0])
                print(buffer)
                return buffer
                buffer = ''
        # except KeyboardInterrupt:
        #     print('User terminated program')


if __name__ == '__main__':
    print("Start Serial Monitor", '\n')
    monitorlink()
