 # -*- coding: utf-8 -*-

"""
translate.app
~~~~~~~~~~~~~

Server interface for translate application. This handles the process of
handling HTTP requests and generating responses.
"""

from translate import log
from translate.backend import BackendManager

import translate.utils

import flask

app = flask.Flask(__name__, static_folder="./static")

app.config.from_object('translate.app.defaultsettings')
app.config.from_object('settings')

from translate.app import views
from translate.app.ratelimit import RateLimit


@app.before_first_request
def initialize_flask():
    """Make sure that the flask application is properly configured before it
    serves any requests
    """

    server_conf = app.config['SERVER']
    backend_conf = app.config['BACKENDS']

    views.manager = BackendManager(backend_conf)

    ratelimit = server_conf.get('ratelimit', None)
    if ratelimit is not None and ratelimit.get('enabled', False):
        RateLimit.enable(limit=ratelimit['limit'], per=ratelimit['per'])

    def deinitialize_manager():
        """Do any cleanup that needs to be done (for backends in particular)
        before the server terminates."""

        log.info("Shutting down server...")
        views.manager.shutdown()

    # Cleanup the server on ^C
    import atexit
    atexit.register(deinitialize_manager)


def start_server(custom_config={}, debug=True):
    """Start the flask Server using flask's built in Werkzeug server. This
    function doesn't return.
    """

    app.config = translate.utils.update(app.config, custom_config)

    server_conf = app.config['SERVER']

    host = server_conf['bind']
    port = server_conf['port']

    log.info("Starting server on port {0}, using host {1}".format(port, host))

    app.run(host=host, port=port, debug=debug)
