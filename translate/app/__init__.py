 # -*- coding: utf-8 -*-

# This file is part of translate.
#
# translate is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# translate is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# translate.  If not, see <http://www.gnu.org/licenses/>.

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


# API versions that we support (can respond to /api/VERSION/METHOD). It is the
# server's job to be backward compatible, not the client's (at least for now)
API_VERSION_SUPPORT = ['v1']


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
        before the server terminates.
        """

        log.info("Shutting down server...")
        views.manager.shutdown()

    # Cleanup the server on ^C
    import atexit
    atexit.register(deinitialize_manager)


def start_server(custom_config, debug=True):
    """Start the flask Server using flask's built in Werkzeug server. This
    function doesn't return.
    """

    app.config = translate.utils.update(app.config, custom_config)

    server_conf = app.config['SERVER']

    host = server_conf['host']
    port = server_conf['port']

    log.info("Starting server on port {0}, using host {1}".format(port, host))

    # Extra, optional arguments to be passed as kwargs.
    options = {}

    if server_conf['ssl']['enabled']:
        log.info('Using SSL')

        options['ssl_context'] = (server_conf['ssl']['cert'],
                                  server_conf['ssl']['key'])

    app.run(host=host, port=port, debug=debug, **options)
