 # -*- coding: utf-8 -*-

"""
Server interface for translate application. This handles the process of
handling HTTP requests and generating responses.
"""

from . import __version__
from backend import BackendManager
import utils

import logging
import flask

from gevent.wsgi import WSGIServer
from flask import render_template, request

log = logging.getLogger(__name__)
app = flask.Flask(__name__)

manager = BackendManager()


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


@app.errorhandler(400)
def bad_request(error):

    # if this is an API request, return JSON
    if error.kind == 'api':
        return flask.jsonify(method=error.method,
                             message=error.description), 400
    else:
        raise error


@app.route('/')
def index():
    return render_template('index.html', version=__version__)


@app.route('/api/v1/')
def api():
    return render_template('api.html')


@app.route('/api/v1/translators')
def list_translators():
    return flask.jsonify(
        backends=[{
            'name': b.name,
            'description': b.description,
            'preference': b.preference,
        } for b in manager.backends])


@app.route('/api/v1/translate')
def translate_text():

    text = request.args.get('text', None)
    if not text:
        utils.api_abort('translate', 'No translation text given')

    source_lang = request.args.get('from', None)
    if not source_lang:
        utils.api_abort('translate', 'No source language given')

    dest_lang = request.args.get('to', None)
    if not dest_lang:
        utils.api_abort('translate', 'No destination language given')

    backend = manager.find_best(source_lang, dest_lang)

    # TODO: JSON-ify

    if backend is None:
        utils.api_abort('translate', 'No translators can handle this' +
                        'language pair')

    trans = backend.translate(text, source_lang, dest_lang)

    return flask.jsonify(source_lang=source_lang, dest_lang=dest_lang,
                         result=trans)
