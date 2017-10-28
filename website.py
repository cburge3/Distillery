import os, os.path
import sys
import cherrypy
from cherrypy.process.plugins import Autoreloader
from random import randint
import paho.mqtt.client as mqtt

last_message = '0'

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("test")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global last_message
    last_message = msg.payload.decode()
    print(msg.topic+" "+msg.payload.decode())

sys.path.insert(0, "..")

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
            "tools.staticfile.filename": "/root/Distillery/templates/golden.ico"
    },
    '/style.css': {
            "tools.staticfile.on": True,
            "tools.staticfile.filename": "/root/Distillery/templates/style.css"
    },
    '/assets/canvasjs': {
        "tools.staticfile.on": True,
        "tools.staticfile.filename":
            "/root/Distillery/templates/assets/canvasjs-1.9.8/canvasjs.min.js"
    }

}


class ThePlant(object):
    @cherrypy.expose
    def index(self):
        return open('/root/Distillery/templates/index.html')

@cherrypy.expose
class OPCInterface(object):

    @cherrypy.tools.accept(media='text/plain')
    def GET(self):
        global last_message
        # input MQTT code here
        return last_message
        # return str(randint(1,10))
        # if PV is not None:
        #     cv = PV.get_data_value().Value.Value
        #     print("myvar is: ", cv)
        #     return str(cv)
        # else:
        #     return 'Unknown server error'

    def POST(self, **data):
        # output MQTT code here
        print("sent a value to controller")
        return "hello"

    def PUT(self, another_string):
        pass
        # cherrypy.session['mystring'] = another_string

    def DELETE(self):
        pass
        # cherrypy.session.pop('mystring', None)


if __name__ == '__main__':
    webapp = ThePlant()
    client = mqtt.Client()
    client.username_pw_set('ionodes', '1jg?8jJ+Ut8,')
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("localhost", 1883, 60)
    client.loop_start()
    webapp.generator = OPCInterface()
    cherrypy.engine.autoreload.unsubscribe()
    cherrypy.server.socket_host = '0.0.0.0'
    cherrypy.quickstart(webapp, '/', conf)

