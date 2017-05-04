import sys
sys.path.insert(0, "..")
import time
import random


from opcua import ua, Server
from opcua.server.history_sql import HistorySQLite


if __name__ == "__main__":

    # setup our server
    server = Server()
    server.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/")

    # setup our own namespace, not really necessary but should as spec
    uri = "http://chipburge.com"
    idx = server.register_namespace(uri)

    # get Objects node, this is where we should put our custom stuff
    objects = server.get_objects_node()

    # populating our address space
    TI100 = objects.add_object(idx, "MyObject")
    TT100 = TI100.add_variable(idx, "MyVariable", ua.Variant(0, ua.VariantType.Double))
    # myvar.set_writable()  # Set MyVariable to be writable by clients

    # Configure server to use sqlite as history database (default is a simple memory dict)
    server.iserver.history_manager.set_storage(HistorySQLite("my_datavalue_history.sql"))

    # starting!
    server.start()

    # enable data change history for this particular node, must be called after start since it uses subscription
    server.historize_node_data_change(TT100, period=None, count=100)

    try:
        count = 0
        while True:
            time.sleep(1)
            count += 0.1
            TT100.set_value(25*random.random())

    finally:
        # close connection, remove subscriptions, etc
        server.stop()
