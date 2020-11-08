import os
import json

from waitress import serve


class Server:
    def __init__(self, manager):
        self.manager = manager

    def application(self, environ, start_response):
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        except (ValueError):
            request_body_size = 0

        start_response('200 OK', [
            ('Content-Type','application/json'),
            ('Access-Control-Allow-Origin', '*'),
            ('Access-Control-Allow-Methods', 'GET, POST, PATCH, PUT, DELETE, OPTIONS'),
            ('Access-Control-Allow-Headers', 'Origin, Content-Type, X-Auth-Token')])

        request_body = environ['wsgi.input'].read(request_body_size)
        data = json.loads(request_body)
        try:
            ret = self.manager.load_tcp_command(data)
        except:
            os.system('fuser -k 9998/tcp')
        return [json.dumps(ret).encode()]


    def serve(self):
        serve(self.application, listen='*:9998')
