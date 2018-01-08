from time import strftime, localtime, sleep
from os import fsync
from getserialdata import monitorlink
from opcua import Client

history_interval = 10

def truncate(f, n):
    # Truncates/pads a float f to n decimal places without rounding
    s = '{}'.format(f)
    if 'e' in s or 'E' in s:
        return '{0:.{1}f}'.format(f, n)
    i, p, d = s.partition('.')
    return '.'.join([i, (d+'0'*n)[:n]])

def ctof(c):
    return float(c) * 9 / 5 + 32

if __name__ == '__main__':
    with open("databases\\tempdata" + strftime("%a_%d_%b_%H_%M_%S", localtime()) + ".log", 'w') as logfile:
        while True:
            # value = monitorlink()
            # value = str(truncate(ctof(value), 2))
            client = Client("opc.tcp://localhost:4840/freeopcua/server/")
            try:
                client.connect()
                root = client.get_root_node()
                myvar = root.get_child(["0:Objects", "2:MyObject", "2:MyVariable"])
                value = myvar.get_data_value().Value.Value
                logfile.write(strftime("%a %d %b %Y %H:%M:%S", localtime()) + ',' + str(value) + '\n')
                # make sure to push the python and windows buffers to the file in case of ungraceful exit
                logfile.flush()
                fsync(logfile.fileno())
                sleep(history_interval)
            finally:
                client.disconnect()