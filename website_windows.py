import os, os.path
import sys
import cherrypy
import random
import json
sys.path.insert(0, "..")

fd = ''

if os.name == 'nt':
    fd = '\\'
else:
    fd = '/'

cwd = os.path.abspath(os.getcwd()) + fd

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
class LiveData(object):

    @cherrypy.tools.accept(media='text/plain')
    def GET(self):
        a = random.randrange(32,100)
        b = random.randrange(32,100)
        return json.dumps({'var1': a, 'var2': b})

    def POST(self, **data):
        print(data, " was posted")
        return "hello"

    def PUT(self, another_string):
        pass

    def DELETE(self):
        pass


if __name__ == '__main__':
    webapp = ThePlant()
    webapp.generator = LiveData()
    cherrypy.engine.autoreload.unsubscribe()
    cherrypy.server.socket_host = '127.0.0.1'
    cherrypy.quickstart(webapp, '/', conf)
