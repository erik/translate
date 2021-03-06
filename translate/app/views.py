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
translate.app.views
~~~~~~~~~~~~~~~~~~~

This module defines the Flask routes (URL endpoints) that the translate server
specifies. All HTML and JSON responses are generated here.
"""

from . import app, log
from .ratelimit import ratelimit, RateLimit
from translate.exceptions import APIException, TranslationException

import translate.app
import translate.utils

import flask
from flask import render_template, request

import json


manager = None


@app.after_request
def inject_x_rate_headers(response):
    """Add ratelimit headers to response if the requested URL is an API
    endpoint that requires rate-limiting
    """

    remaining = translate.app.ratelimit.get_view_rate_limit_remaining()
    if RateLimit.enabled and translate.app.ratelimit.get_view_send_x_headers():
        h = response.headers
        h.add('X-RateLimit-Remaining', str(remaining))
        h.add('X-RateLimit-Limit', str(RateLimit.limit))
        h.add('X-RateLimit-Duration', str(RateLimit.per))
        h.add('X-RateLimit-Reset', str(RateLimit.reset))
    return response


@app.errorhandler(APIException)
@translate.utils.jsonp
def bad_request(error):
    """If an APIException is raised, generate a response (.jsonify() creates a
    proper flask response)
    """
    return error.jsonify()


@app.route('/')
def html_index():
    """Index page, obviously enough."""
    return render_template('index.html')


@app.route('/info')
def html_info():
    """Show information about the server, in HTML form."""

    pairs = set()

    for backend in manager.backends:
        for pair in backend.language_pairs:
            pairs.add(pair)

    pairs = list(pairs)

    # Sort by from_language
    pairs = sorted(pairs, key=lambda pair: pair[0])

    if app.config['SERVER']['sizelimit']['enabled']:
        sizelimit = app.config['SERVER']['sizelimit']['limit']
    else:
        sizelimit = False

    if RateLimit.enabled:

        RateLimit.update_timer()

        user = flask.request.remote_addr
        methods = {}
        for key, users in RateLimit.limit_dict.iteritems():
            methods[key] = RateLimit.remaining(user, key)

        ratelimit = dict(limit=RateLimit.limit, per=RateLimit.per,
                         reset=RateLimit.reset, methods=methods)
    else:
        ratelimit = False

    return render_template('info.html',
                           version=translate.__version__,
                           supported_api=translate.app.API_VERSION_SUPPORT,
                           backends=manager.backends,
                           sizelimit=sizelimit,
                           ratelimit=ratelimit,
                           pairs=pairs)


@app.route('/api/v1/batch', methods=['POST'])
@translate.utils.jsonp
def batch_api():
    """Batch multiple API calls into a single request."""
    # TODO: Should there be a limit on the number of URLs here? Even though
    #       ratelimiting is handled, this could be a potential target for
    #       DOSing the server. This batch method is also quite a bit slower
    #       than direct requests.

    # Flask raises a special error when this isn't provided
    try:
        urls = json.loads(request.form['urls'])
    except (KeyError, ValueError):
        # Die with a 400 BAD REQUEST if we're given... a bad request.
        flask.abort(400)

    responses = []

    for url in urls:

        # Pretend flask was just given the specified URL
        ctx = app.test_request_context(url)
        ctx.push()

        # Dispatch URL (error + route handling) as a normal request.
        resp = app.full_dispatch_request()

        # If we requested an API url, load the serialized JSON so that the
        # entire response can be loaded by the caller as a single JSON
        # parse. If we didn't request an API method, just return a string, to
        # be JSON-escaped when the final response is created.
        #
        # TODO: Maybe require API urls only?
        if url.startswith("/api/v1/"):
            try:
                resp_data = json.loads(resp.data)
            except ValueError:
                resp_data = {'error': "Bad JSON returned %s" % resp.data}
        else:
            resp_data = resp.data

        # This will overwrite duplicate headers (resp.headers is a multimap),
        # but we don't care about that, since there shouldn't be any duplicates
        # returned.
        headers = {}
        for k, v in resp.headers.iteritems():
            headers[k] = v

        responses.append(dict(status=resp.status_code,
                              headers=headers,
                              url=url,
                              data=resp_data))

        ctx.pop()

    # Pretty print
    js = json.dumps(responses, sort_keys=True, indent=4)
    resp = flask.Response(response=js, mimetype='application/json')

    return resp, 200


@app.route('/api/v1/info')
@translate.utils.jsonp
def show_info():
    """JSON version of server information"""

    resp_obj = {
        'version': translate.__version__,
        'api_versions': translate.app.API_VERSION_SUPPORT
    }

    resp_obj['backends'] = [{'name': b.name,
                             'description': b.description,
                             'url': b.url,
                             'preference': b.preference,
                             'pairs': b.language_pairs}
                            for b in manager.backends]

    if RateLimit.enabled:
        user = flask.request.remote_addr

        # Make sure the ratelimit information is up to date.
        RateLimit.update_timer()

        methods = {}
        for key, users in RateLimit.limit_dict.iteritems():
            methods[key] = RateLimit.remaining(user, key)

        resp_obj['ratelimit'] = dict(limit=RateLimit.limit, per=RateLimit.per,
                                     reset=RateLimit.reset, methods=methods)

    if app.config['SERVER']['sizelimit']['enabled']:
        resp_obj['sizelimit'] = app.config['SERVER']['sizelimit']['limit']

    return flask.jsonify(**resp_obj)


# XXX: Should this really be limited? I think no...
@app.route('/api/v1/pairs')
@ratelimit()
@translate.utils.jsonp
def list_pairs():
    """Deduplicated list of language pairs that the server supports."""

    pairs = set()

    for backend in manager.backends:
        for pair in backend.language_pairs:
            pairs.add(pair)

    return flask.jsonify(pairs=list(pairs))


@app.route('/api/v1/translate')
@ratelimit()
@translate.utils.jsonp
def translate_text():
    """Translate some text"""

    text = request.args.get('text', None)
    if not text or text == "":
        raise APIException.translate(msg='No translation text given')

    source_lang = request.args.get('from', None)
    if not source_lang:
        raise APIException.translate(msg='No source language given')

    dest_lang = request.args.get('to', None)
    if not dest_lang:
        raise APIException.translate(msg='No destination language given')

    bytelen = len(text.encode('utf-8'))
    conf = app.config['SERVER']['sizelimit']

    if conf['enabled'] and bytelen > conf['limit']:
        raise APIException.sizelimit(len=bytelen, limit=conf['limit'])

    # Try each translator sequentially (sorted by preference) until one works
    backends = manager.find_all(source_lang, dest_lang)

    # List of translator backend names that the client does not want to use
    excludes = request.args.getlist('exclude')

    if len(backends) == 0:
        raise APIException.pair(from_lang=source_lang, to_lang=dest_lang,
                                text=text)

    tried = []

    for backend in backends:
        if backend.name in excludes:
            log.info("Skipping %s, client disapproved.", backend.name)
            continue

        tried.append(backend.name)

        try:
            trans = backend.translate(text, source_lang, dest_lang)

            if trans is None or trans == "":
                raise TranslationException("Received empty result text")

            return flask.Response(json.dumps({
                'from': source_lang,
                'to': dest_lang,
                'result': trans,
                'translator': backend.name
            }), mimetype='application/json')

        except TranslationException as exc:
            log.warning('{0} failed to translate text: {1}'
                        .format(backend.name, exc))

    raise APIException.translator(from_lang=source_lang, to_lang=dest_lang,
                                  text=text, tried=tried)
