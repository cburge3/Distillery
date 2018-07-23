import os
import sys
import cherrypy
import argparse
import json
from random import randint
import paho.mqtt.client as mqttClient
import csv
import subprocess

# multi os support
if os.name == 'nt':
    fd = '\\'
else:
    fd = '/'

# command line parsing
parser = argparse.ArgumentParser(description='Serve a GUI for this control system')
parser.add_argument('-debug', metavar='debug=True/False', type=bool,
                    help='Used to debug the website without running i/o interfacing backend')
args = parser.parse_args()

cwd = os.path.dirname(os.path.realpath(__file__)) + fd

# Build copy of IO list in memory
io_list = []
with open('IO.txt') as io_file:
    for z in csv.DictReader(io_file):
        io_list.append(z)

live_data = {}
# this needs to be looked up by IO card
# io_topic_prefix = 'io/IOC1/out/'
io_output_statics = ['io/','/out/']
# receive data from all io cards
io_subscription = 'io/#'
commands = ['OutputCommand','ProgramControls']

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
        self.processes = []
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

    def PUT(self, **data):
        print(data)
        # handle different types of requests
        command = data['class']
        print(data['class'], command)
        # write to IO
        if command == commands[0]:
            for entries in io_list:
                if data['id'] == entries['IOtag']:
                    topicPath = io_output_statics[0] + entries['Card'] + io_output_statics[1] + data['id']
                    if args.debug is not True:
                        self.client.publish(io_output_statics[0] + entries['Card'] + io_output_statics[1] + data['id'],
                                            data['value'])
                    print("writing {} to {}".format(topicPath, data['value']))
        # write to non online value
        if command == commands[1]:
            ctrl_prog = subprocess.Popen
            if int(data['value']) == 1:
                print("I'm starting the program!")
                z = subprocess.Popen("python controller.py")
                self.processes.append(z)
                print(z.stdout,z.returncode)
            else:
                print("I'm stopping the program :(")
                self.processes[0].kill()
                self.processes.pop()
            pass
            # start the program here
        return "wayd"

    def POST(self, another_string):
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

