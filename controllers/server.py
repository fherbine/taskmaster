import logging
import os
import signal
import json

from waitress import serve

from controllers.logger import Logger

LOGLEVEL = getattr(logging, os.environ.get('LOGLEVEL', 'INFO'), logging.INFO)


class Server:
    def __init__(self, manager):
        self.manager = manager
        self.lock = False
        self.log = Logger(level=LOGLEVEL)
        signal.signal(signal.SIGINT, self._handle_kb_interrupt)

    def _handle_kb_interrupt(self, *_):
        # XXX: hack
        self.log.warning('Ctrl+C, quitting program.')
        self.manager.stop_all()
        raise KeyboardInterrupt

    def application(self, environ, start_response):
        while self.lock:
            pass

        self.lock = True
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        except (ValueError):
            request_body_size = 0

        start_response('200 OK', [
            ('Content-Type', 'application/json'),
            ('Access-Control-Allow-Origin', '*'),
            ('Access-Control-Allow-Methods', 'GET, POST, PATCH, PUT, DELETE, OPTIONS'),
            ('Access-Control-Allow-Headers', 'Origin, Content-Type, X-Auth-Token')])

        request_body = environ['wsgi.input'].read(request_body_size)
        data = json.loads(request_body)
        ret = self.manager.load_tcp_command(data)

        self.lock = False
        return [json.dumps(ret).encode()]

    def serve(self):
        serve(self.application, listen='*:9998')
