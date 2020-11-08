import json

from waitress import serve


def application(environ, start_response):
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except (ValueError):
        request_body_size = 0

    start_response('200 OK', [('Content-Type','application/json')])

    request_body = environ['wsgi.input'].read(request_body_size)
    data = json.loads(request_body)
    print(data)
    return [json.dumps({"hello":  "world"}).encode()]


serve(application, listen='*:9998')
