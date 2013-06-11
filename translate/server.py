 # -*- coding: utf-8 -*-

"""
Server interface for translate application. This handles the process of
handling HTTP requests and generating responses.
"""

from . import __version__
from backend import BackendManager

import logging
import flask

from gevent.wsgi import WSGIServer
from flask import render_template, request

log = logging.getLogger(__name__)
app = flask.Flask(__name__)

manager = BackendManager()


class APIException(Exception):

    def __init__(self, method, error):
        self.method = method
        self.error = error

    def __str__(self):
        return "{0}: {1}".format(self.method, self.error)


def start(debug=False):
    """
    Start the flask Server using gevent's WSGIServer. This function doesn't
    return.
    """

    app.debug = debug

    log.info("Starting...")

    # If we're using debug mode, using flask itself to run so we can hotswap
    # code.
    if debug:
        app.run()
    else:
        http_server = WSGIServer(('', 5000), app)
        http_server.serve_forever()


@app.route('/')
def index():
    return render_template('index.html', version=__version__)


@app.route('/api/v1/')
def api():
    pass


@app.route('/api/v1/translators')
def list_translators():
    backends = [b.name() for b in manager.backends]
    return repr(backends)


@app.route('/api/v1/translate')
def translate_text():

    text = request.args.get('text', None)
    if not text:
        raise APIException('translate', 'No translation text given')

    source_lang = request.args.get('from', None)
    if not source_lang:
        raise APIException('translate', 'No source language given')

    dest_lang = request.args.get('to', None)
    if not dest_lang:
        raise APIException('translate', 'No destination language given')

    backend = manager.find_best(source_lang, dest_lang)

    # TODO: JSON-ify

    if backend is None:
        return "No translators can handle this language pair"

    return backend.translate(text, source_lang, dest_lang)
