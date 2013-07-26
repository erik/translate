# -*- coding: utf-8 -*-

"""
translate.utils
~~~~~~~~~~~~~~~

This module contains small utility snippets of code adapted to be useful for
this project. If these were not directly written for the translate project,
a link to the original source is included in the docstring.
"""

from . import log

import flask
import inspect
import subprocess
import pkgutil
import collections

from functools import wraps


def find_subclasses(path, cls):
    """Return a list of tuples containing (subclass, modulename).

    path: path to search for subclasses
    cls: class to find subclasses of
    """
    subclasses = []

    for loader, name, _ in pkgutil.walk_packages([path]):
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


# Python 2.6 doesn't support subprocess.check_output, so monkey-patch it in
if "check_output" not in dir(subprocess):
    def f(*popenargs, **kwargs):
        if 'stdout' in kwargs:
            raise ValueError('stdout argument not allowed, ' +
                             'it will be overridden.')
        process = subprocess.Popen(stdout=subprocess.PIPE,
                                   *popenargs, **kwargs)
        output, _ = process.communicate()
        retcode = process.poll()
        if retcode:
            cmd = kwargs.get("args")
            if cmd is None:
                cmd = popenargs[0]
            raise subprocess.CalledProcessError(retcode, cmd)
        return output
    subprocess.check_output = f


def update(d, u, depth=-1):
    """Recursively merge or update dict-like objects.
    >>> update({'k1': {'k2': 2}}, {'k1': {'k2': {'k3': 3}}, 'k4': 4})
    {'k1': {'k2': {'k3': 3}}, 'k4': 4}

    Code from: http://stackoverflow.com/a/14048316
    """

    for k, v in u.iteritems():
        if isinstance(v, collections.Mapping) and not depth == 0:
            r = update(d.get(k, {}), v, depth=max(depth - 1, -1))
            d[k] = r
        elif isinstance(d, collections.Mapping):
            d[k] = u[k]
        else:
            d = {k: u[k]}
    return d


def chunk_string(string, n):
    """Yield successive n-byte sized substrings from string.

    TODO: Split on word boundaries instead of middle of word...

    Code adapted from: http://stackoverflow.com/a/312464
    """

    for i in xrange(0, len(string.encode('utf-8')), n):
        yield string[i:i+n]
