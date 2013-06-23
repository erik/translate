# -*- coding: utf-8 -*-

from . import log

import flask
import werkzeug
import inspect
import subprocess
import pkgutil

from functools import wraps


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


def find_subclasses(path, cls):
    """Return a list of tuples containing (subclass, modulename).

    path: path to search for subclasses
    cls: class to find subclasses of
    """
    subclasses = []

    for loader, name, ispkg in pkgutil.walk_packages([path]):
        module = loader.find_module(name).load_module(name)
        log.debug("Searching module %s" % (name))

        for key, entry in inspect.getmembers(module, inspect.isclass):
            if key == cls.__name__:
                continue

            try:
                if issubclass(entry, cls):
                    log.debug("Found subclass: "+key)
                    subclasses.append((entry, name))
            except TypeError:
                continue

    return subclasses


def jsonp(func):
    """Wraps JSONified output for JSONP requests.

    From: https://gist.github.com/aisipos/1094140
    """
    @wraps(func)
    def decorated_function(*args, **kwargs):
        callback = flask.request.args.get('callback', False)
        if callback:
            data = str(func(*args, **kwargs).data)
            content = str(callback) + '(' + data + ')'
            mimetype = 'application/javascript'
            return flask.current_app.response_class(content, mimetype=mimetype)
        else:
            return func(*args, **kwargs)
    return decorated_function


if "check_output" not in dir(subprocess):
    """Python 2.6 doesn't support subprocess.check_output, so add that in"""
    def f(*popenargs, **kwargs):
        if 'stdout' in kwargs:
            raise ValueError('stdout argument not allowed, ' +
                             'it will be overridden.')
        process = subprocess.Popen(stdout=subprocess.PIPE,
                                   *popenargs, **kwargs)
        output, unused_err = process.communicate()
        retcode = process.poll()
        if retcode:
            cmd = kwargs.get("args")
            if cmd is None:
                cmd = popenargs[0]
            raise subprocess.CalledProcessError(retcode, cmd)
        return output
    subprocess.check_output = f
