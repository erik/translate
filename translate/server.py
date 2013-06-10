 # -*- coding: utf-8 -*-

"""
Server interface for translate application. This handles the process of
handling HTTP requests and generating responses.
"""

from . import __version__

import logging

from gevent.wsgi import WSGIServer
from flask import Flask, render_template

log = logging.getLogger(__name__)
app = Flask(__name__)

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


@app.route('/api')
def api():
    pass
