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

# cwd = os.path.abspath(os.getcwd()) + fd
cwd = os.path.dirname(os.path.realpath(__file__)) + fd
last_message = '0'
live_data = {}
io_topic_prefix = 'io/IOC/'

sys.path.insert(0, "..")

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("test")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    # global last_message, live_data
    # last_message = msg.payload.decode()
    global live_data
    live_data[msg.topic] = msg.payload.decode()
    print(msg.topic+" "+msg.payload.decode())


conf = {
    '/': {
        'tools.sessions.on': True,
        'tools.staticdir.root': os.path.abspath(os.getcwd())
    },
    '/generator': {
        'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
        'tools.response_headers.on': True,
        'tools.response_headers.headers': [('Content-Type', 'text/plain')],
    },
    '/static': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': './templates'
    },
    '/favicon.ico': {
            "tools.staticfile.on": True,
            "tools.staticfile.filename": cwd + "templates" + fd + "golden.ico"
    },
    '/assets/canvasjs': {
        "tools.staticfile.on": True,
        "tools.staticfile.filename":
            cwd + "templates" + fd + "assets" + fd + "canvasjs-1.9.8" + fd + "canvasjs.min.js"
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
            self.client.loop_start()
        else:
            print("Website running in debug mode")


    @cherrypy.tools.accept(media='text/plain')
    def GET(self):
        if args.debug is not True:
            # global last_message
            # input MQTT code here
            print(last_message)
            a = live_data.copy()
            live_data.clear()
            return json.dumps(a)
        else:
            a = randint(32, 100)
            b = randint(32, 100)
            return json.dumps({'var1': a, 'var2': b})

    def POST(self, **data):
        # output MQTT code here
        if args.debug is not True:
            self.client.publish(io_topic_prefix + data['id'], data['value'])
        print(data)
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

