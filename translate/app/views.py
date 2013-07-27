 # -*- coding: utf-8 -*-

from . import app, log
from .ratelimit import ratelimit, RateLimit
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


@app.route('/api/v1/batch', methods=['POST'])
@translate.utils.jsonp
def batch_api():
    # TODO: Should there be a limit on the number of URLs here? Even though
    #       ratelimiting is handled, this could be a potential target for
    #       DOSing the server. This batch method is also quite a bit slower
    #       than direct requests.

    # Flask raises a special error when this isn't provided
    try:
        urls = json.loads(request.form['urls'])
    except (KeyError, ValueError):
        # TODO: handle this properly
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
        # XXX: This isn't a guarantee. There could be a different kind of error
        # that causes invalid or no JSON to be returned.
        if url.startswith("/api/v1/"):
            # XXX: It's also kind of silly to load this and dump it back a few
            #      lines later...
            resp_data = json.loads(resp.data)
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
@ratelimit()
@translate.utils.jsonp
def show_info():
    # XXX: Should /info be ratelimited?
    # TODO: /ratelimit and /translators are reduntant with this one, remove?

    if RateLimit.enabled:
        user = flask.request.remote_addr

        # Make sure the ratelimit information is up to date.
        RateLimit.update_timer()

        methods = {}
        for key, users in RateLimit.limit_dict.iteritems():
            methods[key] = RateLimit.remaining(user, key)

        ratelimit = dict(limit=RateLimit.limit, per=RateLimit.per,
                         reset=RateLimit.reset, methods=methods)
    else:
        ratelimit = dict()

    backends = [{'name': b.name,
                 'description': b.description,
                 'url': b.url,
                 'preference': b.preference,
                 'pairs': b.language_pairs}
                for b in manager.backends]

    if app.config['SERVER']['sizelimit']['enabled']:
        sizelimit = app.config['SERVER']['sizelimit']['limit']
    else:
        sizelimit = -1

    return flask.jsonify(ratelimit=ratelimit, sizelimit=sizelimit,
                         backends=backends)


@app.route('/api/v1/pairs')
@ratelimit()
@translate.utils.jsonp
def list_pairs():

    pairs = set()

    for backend in manager.backends:
        for pair in backend.language_pairs:
            pairs.add(pair)

    return flask.jsonify(pairs=list(pairs))


@app.route('/api/v1/ratelimit')
@translate.utils.jsonp
def ratelimit_info():
    if RateLimit.enabled:
        user = flask.request.remote_addr

        # Make sure the ratelimit information is up to date.
        RateLimit.update_timer()

        methods = {}
        for key, users in RateLimit.limit_dict.iteritems():
            methods[key] = RateLimit.remaining(user, key)

        return flask.jsonify(limit=RateLimit.limit, per=RateLimit.per,
                             reset=RateLimit.reset, methods=methods)

    return flask.jsonify()


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
