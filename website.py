import os
import sys
import cherrypy
import argparse
import json
from random import randint
import paho.mqtt.client as mqttClient

if os.name == 'nt':
    fd = '\\'
else:
    fd = '/'

parser = argparse.ArgumentParser(description='Serve a GUI for this control system')
parser.add_argument('-debug', metavar='debug=True/False', type=bool,
                    help='Used to debug the website without running i/o')
args = parser.parse_args()

cwd = os.path.dirname(os.path.realpath(__file__)) + fd

live_data = {}
io_topic_prefix = 'io/IOC1/out/'
io_subscription = 'io/IOC1/in/#'

sys.path.insert(0, "..")

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(io_subscription)


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global live_data
    # assume that unique tag is last in the MQTT topic structure
    topic = msg.topic.split('/')[-1]
    live_data[topic] = msg.payload.decode()
    print(msg.topic+" "+msg.payload.decode())


conf = {
    '/': {
        'tools.sessions.on': True
        # 'tools.staticdir.root': os.path.abspath(os.getcwd())
    },
    '/generator': {
        'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
        'tools.response_headers.on': True,
        'tools.response_headers.headers': [('Content-Type', 'text/plain')],
    },
    '/static': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': cwd + "templates"
    },
    '/favicon.ico': {
            "tools.staticfile.on": True,
            "tools.staticfile.filename": cwd + "templates" + fd + "golden.ico"
    }
}


class ThePlant(object):
    @cherrypy.expose
    def index(self):
        return open(cwd + "templates" + fd + "index.html")

@cherrypy.expose
class AJAXInterface(object):

    def __init__(self):
        if args.debug is not True:
            self.client = mqttClient.Client()
            self.client.username_pw_set('ionodes', '1jg?8jJ+Ut8,')
            self.client.on_connect = on_connect
            self.client.on_message = on_message
            self.client.connect("localhost", 1883, 60)
            print("Connecting engine to MQTT server...")
            self.client.loop_start()
        else:
            print("Website running in debug mode")


    @cherrypy.tools.accept(media='text/plain')
    def GET(self):
        if args.debug is not True:
            global live_data
            a = live_data.copy()
            live_data.clear()
            return json.dumps(a)
        else:
            a = randint(32, 100)
            b = randint(32, 100)
            return json.dumps({'TI100': a, 'TI101': b})

    def POST(self, **data):
        print(data)
        if args.debug is not True:
            self.client.publish(io_topic_prefix + data['id'], data['value'])
        return "wayd"

    def PUT(self, another_string):
        pass
        # cherrypy.session['mystring'] = another_string

    def DELETE(self):
        pass
        # cherrypy.session.pop('mystring', None)


if __name__ == '__main__':
    webapp = ThePlant()
    webapp.generator = AJAXInterface()
    cherrypy.engine.autoreload.unsubscribe()
    cherrypy.server.socket_host = '0.0.0.0'
    cherrypy.quickstart(webapp, '/', conf)

