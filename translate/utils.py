# -*- coding: utf-8 -*-

import logging
import os
import flask
import werkzeug
import imp
import inspect

from functools import wraps

log = logging.getLogger(__name__)


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
    """
    Taken from:
    http://www.executionunit.com/blog/2008/01/28/python-style-plugins-made-easy

    Find all subclass of cls in py files located below path
    (does look in sub directories)

    @param path: the path to the top level folder to walk
    @type path: str
    @param cls: the base class that all subclasses should inherit from
    @type cls: class
    @rtype: list
    @return: a list if classes that are subclasses of cls
    """

    subclasses = []

    def look_for_subclass(modulename, path):
        log.debug("searching %s" % (modulename))
        module = imp.load_source(modulename, path)

        #look through this dictionary for things
        #that are subclass of Job
        #but are not Job itself
        for key, entry in inspect.getmembers(module, inspect.isclass):
            if key == cls.__name__:
                continue

            try:
                if issubclass(entry, cls):
                    log.debug("Found subclass: "+key)
                    subclasses.append(entry)
            except TypeError:
                #this happens when a non-type is passed in to issubclass. We
                #don't care as it can't be a subclass of Job if it isn't a
                #type
                continue

    for root, dirs, files in os.walk(path):
        for name in files:
            if name.endswith(".py") and not name.startswith("__"):
                path = os.path.join(root, name)
                modulename = path.rsplit('.', 1)[0].replace('/', '.')
                look_for_subclass(modulename, path)

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
