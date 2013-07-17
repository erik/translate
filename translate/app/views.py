 # -*- coding: utf-8 -*-

from translate.app import app, log
from translate.app.ratelimit import ratelimit, RateLimit
from translate.exceptions import APIException, TranslationException
from translate import __version__

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
    if RateLimit and translate.app.ratelimit.get_view_send_x_headers():
        h = response.headers
        h.add('X-RateLimit-Remaining', str(remaining))
        h.add('X-RateLimit-Limit', str(RateLimit.limit))
        h.add('X-RateLimit-Duration', str(RateLimit.per))
        h.add('X-RateLimit-Reset', str(RateLimit.reset))
    return response


@app.errorhandler(APIException)
@translate.utils.jsonp
def bad_request(error):

    return error.jsonify()


@app.route('/')
def index():
    return render_template('index.html', version=__version__)


@app.route('/info')
def api():
    pairs = set()

    for backend in manager.backends:
        for pair in backend.language_pairs:
            pairs.add(pair)

    pairs = list(pairs)

    # Sort by from_language
    pairs = sorted(pairs, key=lambda pair: pair[0])

    return render_template('info.html',
                           version=translate.__version__,
                           backends=manager.backends,
                           pairs=pairs)


@app.route('/api/batch', methods=['POST'])
@translate.utils.jsonp
def batch_api():
    # XXX: Doesn't handle rate limiting.

    # Flask raises a special error when this isn't provided
    urls = json.loads(request.form['urls'])

    responses = []

    for url in urls:

        ctx = app.test_request_context(url)
        ctx.push()

        # XXX: This currently ignores HTTP statuses and always returns
        #      200. Should this maybe be the correct behavior?
        resp = app.full_dispatch_request()

        # If not requesting an API method (which shouldn't be done...) return a
        # JSON-escaped string instead of HTML, so that the validity of the JSON
        # response isn't ruined.
        #
        # XXX: This isn't a guarantee. There could be a different kind of error
        # that causes invalid or no JSON to be returned.
        if url.startswith("/api/v1/"):
            responses.append(resp.data)
        else:
            responses.append(json.dumps(resp.data))

        ctx.pop()

    # XXX: This assumes the server always returns valid JSON.
    js = '[\n' + (',\n'.join(responses)) + '\n]'

    resp = flask.Response(response=js, mimetype='application/json')

    return resp, 200


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
    if not text or text == "":
        raise APIException.translate(msg='No translation text given')

    source_lang = request.args.get('from', None)
    if not source_lang:
        raise APIException.translate(msg='No source language given')

    dest_lang = request.args.get('to', None)
    if not dest_lang:
        raise APIException.translate(msg='No destination language given')

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


@app.route('/api/v1/translators')
@ratelimit()
@translate.utils.jsonp
def list_translators():
    return flask.jsonify(
        backends=[{
            'name': b.name,
            'description': b.description,
            'url': b.url,
            'preference': b.preference,
            'pairs': b.language_pairs
        } for b in manager.backends])
