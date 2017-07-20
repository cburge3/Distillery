import sys
import time
import random
from serial.serialutil import SerialException
from getserialdata import monitorlink, USBInterface
from opcua import ua, Server
from opcua.server.history_sql import HistorySQLite
sys.path.insert(0, "..")


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

    TI100 = objects.add_object(idx, "Temperature_Sensor")
    TT100 = TI100.add_variable(idx, "analog_input", ua.Variant(0, ua.VariantType.Double))
    TT100.set_writable()
    JS101 = objects.add_object(idx, "Heater")
    JZ101 = JS101.add_variable(idx, "discrete_output", ua.Variant(bool(False), ua.VariantType.Boolean))
    JZ101.set_writable()

    # server.export_xml_by_ns("dummy.xml",idx)
    # myvar.set_writable()  # Set MyVariable to be writable by clients

    # Configure server to use sqlite as history database (default is a simple memory dict)
    server.iserver.history_manager.set_storage(HistorySQLite("databases\\my_datavalue_history.sql"))

    # starting!
    server.start()

    # enable data change history for this particular node, must be called after start since it uses subscription
    server.historize_node_data_change(TT100, period=None, count=100)

    iface = USBInterface()
    iface.start()
    # try:
    #     pass
    #     # while True:
    #
    #         # value = monitorlink()
    #         # value = str(truncate(ctof(value), 2))
    #         # TT100.set_value(value)
    #         # time.sleep(1)
    # except SerialException:
    #     print("random data since Arduino is not available")
    #     while True:
    #         value = 25 * random.random()
    #         value = str(truncate(ctof(value), 2))
    #         TT100.set_value(value)
    #         time.sleep(1)
    # finally:
    #     # close connection, remove subscriptions, etc
    #     server.stop()
