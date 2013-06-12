# -*- coding: utf-8 -*-

import flask
import werkzeug


def api_abort(method, message, status_code=400):
    """Raise an API exception for given method and message"""
    return abort_with(status_code, message, method=method, kind='api')


def abort_with(status_code, description=None, **kwargs):
    """Raise an exception containing some additional information to be handled
    by the flask application.
    """

    if not kwargs.get('kind', False):
        kwargs.kind = 'unknown'

    try:
        flask.abort(status_code, description)
    except werkzeug.exceptions.HTTPException, exc:
        exc.__dict__.update(kwargs)
        raise
