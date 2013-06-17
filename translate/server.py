 # -*- coding: utf-8 -*-

"""
Server interface for translate application. This handles the process of
handling HTTP requests and generating responses.
"""

from . import __version__, log
from backend import BackendManager
import utils

import flask

from gevent.wsgi import WSGIServer
from flask import render_template, request

app = flask.Flask(__name__,
                  static_folder="./static")

manager = None


def start(config, debug=False):
    """Start the flask Server using gevent's WSGIServer. This function doesn't
    return.
    """

    server_conf = config.get('server', dict())
    backend_conf = config.get('backend', dict())

    host = server_conf.get('bind', '0.0.0.0')
    port = server_conf.get('port', 5000)

    global manager
    manager = BackendManager(backend_conf)

    log.info("Starting server on port {0}, using host {1}".format(port, host))

    # If we're using debug mode, using flask itself to run so we can hotswap
    # code.
    if debug:
        app.run(host=host, port=port, debug=True)
    else:
        http_server = WSGIServer((host, port), app)
        http_server.serve_forever()


@app.errorhandler(400)
@utils.jsonp
def bad_request(error):

    # if this is an API request, return JSON
    if error.kind == 'api':
        resp = flask.make_response(flask.jsonify(method=error.method,
                                                 message=error.description),
                                   400)
        resp.mimetype = 'application/javascript'
        return resp
    else:
        raise error


@app.route('/')
def index():
    return render_template('index.html', version=__version__)


@app.route('/api/')
def api():
    return render_template('api.html')


@app.route('/api/v1/translators')
@utils.jsonp
def list_translators():
    return flask.jsonify(
        backends=[{
            'name': b.name,
            'description': b.description,
            'preference': b.preference,
            'pairs': b.language_pairs
        } for b in manager.backends])


@app.route('/api/v1/pairs')
@utils.jsonp
def list_pairs():

    pairs = set()

    for backend in manager.backends:
        for pair in backend.language_pairs:
            pairs.add(pair)

    return flask.jsonify(pairs=list(pairs))


@app.route('/api/v1/translate')
@utils.jsonp
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

    if backend is None:
        utils.api_abort('translate', 'No translators can handle this ' +
                        'language pair')

    trans = backend.translate(text, source_lang, dest_lang)

    if trans is None:
        utils.api_abort('translate', '{0} failed to translate text'
                        .format(trans))

    return flask.jsonify(source_lang=source_lang, dest_lang=dest_lang,
                         result=trans)
