 # -*- coding: utf-8 -*-

from translate.app import app
from translate.app.ratelimit import get_view_rate_limit, ratelimit
from translate import __version__

import translate.utils

import flask
from flask import render_template, request

manager = None


@app.after_request
def inject_x_rate_headers(response):
    """Add ratelimit headers to response if the requested URL is an API
    endpoint that requires rate-limiting
    """

    limit = get_view_rate_limit()
    if limit and limit.send_x_headers:
        h = response.headers
        h.add('X-RateLimit-Remaining', str(limit.remaining))
        h.add('X-RateLimit-Limit', str(limit.limit))
    return response


@app.errorhandler(400)
@translate.utils.jsonp
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
@ratelimit()
@translate.utils.jsonp
def list_translators():
    return flask.jsonify(
        backends=[{
            'name': b.name,
            'description': b.description,
            'preference': b.preference,
            'pairs': b.language_pairs
        } for b in manager.backends])


@app.route('/api/v1/pairs')
@ratelimit()
@translate.utils.jsonp
def list_pairs():

    pairs = set()

    for backend in manager.backends:
        for pair in backend.language_pairs:
            pairs.add(pair)

    return flask.jsonify(pairs=list(pairs))


@app.route('/api/v1/translate')
@ratelimit()
@translate.utils.jsonp
def translate_text():

    text = request.args.get('text', None)
    if not text:
        translate.utils.api_abort('translate', 'No translation text given')

    source_lang = request.args.get('from', None)
    if not source_lang:
        translate.utils.api_abort('translate', 'No source language given')

    dest_lang = request.args.get('to', None)
    if not dest_lang:
        translate.utils.api_abort('translate', 'No destination language given')

    backend = manager.find_best(source_lang, dest_lang)

    if backend is None:
        translate.utils.api_abort('translate', 'No translators can handle ' +
                                  'this language pair')

    trans = backend.translate(text, source_lang, dest_lang)

    if trans is None:
        translate.utils.api_abort('translate', '{0} failed to translate text'
                                  .format(trans))

    return flask.jsonify(source_lang=source_lang, dest_lang=dest_lang,
                         result=trans)
