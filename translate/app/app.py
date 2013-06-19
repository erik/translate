 # -*- coding: utf-8 -*-

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
