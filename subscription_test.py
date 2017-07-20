from opcua import Client
from opcua.ua import NumericNodeId
# from opcua.tools import Node
from time import sleep


class SubHandler(object):

    """
    Subscription Handler. To receive events from server for a subscription
    data_change and event methods are called directly from receiving thread.
    Do not do expensive, slow or network operation there. Create another
    thread if you need to do such a thing
    """


    def datachange_notification(self, node, val, data):
        print("Python: New data change event", node, val)


    def event_notification(self, event):
        print("Python: New event", event)

namespace = 2
index = 4
handler = SubHandler()
client = Client("opc.tcp://localhost:4840/freeopcua/server/")
try:
    a = NumericNodeId(index, namespace)
    client.connect()
    # r = client.get_root_node()
    o = client.get_objects_node()
    print(o.get_children())
    # print(r.get_children())
    print(client.get_namespace_array())
    n = client.get_node(a)
    print(n.get_browse_name())
    print(n.nodeid)
    print(n.get_description())
    # print(n.get_data_type(),n.get_description())
    sub = client.create_subscription(2253, handler)
    print(sub)
    sub.subscribe_data_change(n)
    sleep(45)

    # sub.subscribe_data_change(2253)
    # sub.create_monitored_items()
    # sub.subscribe_data_change(a)

finally:
    client.disconnect()