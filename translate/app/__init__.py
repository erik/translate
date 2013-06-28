 # -*- coding: utf-8 -*-

"""
Server interface for translate application. This handles the process of
handling HTTP requests and generating responses.
"""

from translate import log
from translate.backend import BackendManager

import flask

from gevent.wsgi import WSGIServer

app = flask.Flask(__name__, static_folder="./static")

from translate.app import views
from translate.app.ratelimit import RateLimit


def start(config, debug=False):
    """Start the flask Server using gevent's WSGIServer. This function doesn't
    return.
    """

    server_conf = config.get('server', dict())
    backend_conf = config.get('backends', dict())

    host = server_conf.get('bind', '0.0.0.0')
    port = server_conf.get('port', 5000)

    views.manager = BackendManager(backend_conf)

    ratelimit = server_conf.get('ratelimit', None)
    if ratelimit is not None:
        RateLimit.enabled = ratelimit.get('enabled', False)
        RateLimit.limit = ratelimit.get('limit', 0)
        RateLimit.per = ratelimit.get('per', 0)

    log.info("Starting server on port {0}, using host {1}".format(port, host))

    # If we're using debug mode, using flask itself to run so we can hotswap
    # code.
    if debug:
        app.run(host=host, port=port, debug=True)
    else:
        http_server = WSGIServer((host, port), app)
        http_server.serve_forever()
