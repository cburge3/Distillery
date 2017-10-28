import os, os.path
import sys
from opcua import Client
import cherrypy
from cherrypy.process.plugins import Autoreloader
import random
import json
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
            "tools.staticfile.filename": "C:\\Users\\cburge\\PycharmProjects\\Distillery\\templates\\golden.ico"
    },
    '/style.css': {
            "tools.staticfile.on": True,
            "tools.staticfile.filename": "C:\\Users\\cburge\\PycharmProjects\\Distillery\\templates\\style.css"
    },
    '/assets/canvasjs': {
        "tools.staticfile.on": True,
        "tools.staticfile.filename":
            "C:\\Users\\cburge\\PycharmProjects\\Distillery\\templates\\assets\\canvasjs-1.9.8\\canvasjs.min.js"
    }

}


class ThePlant(object):
    @cherrypy.expose
    def index(self):
        return open('templates\\index.html')



@cherrypy.expose
class OPCInterface(object):

    @cherrypy.tools.accept(media='text/plain')
    def GET(self):
        a = random.randrange(32,100)
        b = random.randrange(32,100)
        z = [a,b]
        return json.dumps({'var1': a, 'var2': b})

    def POST(self, **data):
        opc_addr = ["0:Objects", "2:Heater", "2:discrete_output"]
        var = root.get_child(opc_addr)
        current_value = var.get_data_value().Value.Value
        root.get_child(opc_addr).set_value(not current_value, var.get_data_type_as_variant_type())
        print(var.get_data_value().Value.Value)
        return "hello"

    def PUT(self, another_string):
        pass
        # cherrypy.session['mystring'] = another_string

    def DELETE(self):
        pass
        # cherrypy.session.pop('mystring', None)


if __name__ == '__main__':
    client = Client("opc.tcp://localhost:4840/freeopcua/server/")
    webapp = ThePlant()
    webapp.generator = OPCInterface()
    try:
        client.connect()
        root = client.get_root_node()
        objects = client.get_objects_node()
        # PV = root.get_child(["0:Objects", "2:MyObject", "2:MyVariable"])
    except ConnectionRefusedError:
        print('OPC server appears to be down')
    cherrypy.engine.autoreload.unsubscribe()
    cherrypy.server.socket_host = '127.0.0.1'
    cherrypy.quickstart(webapp, '/', conf)
    # finally:
    #     client.disconnect()
