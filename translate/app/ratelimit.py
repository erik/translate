# -*- coding: utf-8 -*-

"""Simple IP-based rate-limiting functionality for Flask routes.

This code is derived from http://flask.pocoo.org/snippets/70/ but doesn't rely
on redis. Opts for simple dictionary implementation instead.
"""

import time
import flask

from threading import Lock
from functools import update_wrapper
import translate.utils


class RateLimit(object):
    mutex = Lock()
    limit_dict = {}

    enabled = False
    limit = 0
    per = 0

    def __init__(self, user, key, send_x_headers):
        self.send_x_headers = send_x_headers

        # GIL should take care of us, but just in case, we'll obtain a lock
        RateLimit.mutex.acquire()

        self.add_request(user, key)
        self.trim_requests()

        self.current = len(RateLimit.limit_dict.get(key, {}).get(user, []))

        RateLimit.mutex.release()

    def add_request(self, user, key):
        """Note that the given user made a request to the API method `key`.
        Will only append the request onto the list of requests if the user is
        under their limit (so as not to further penalize duplicate requests
        after the limit is hit).
        """
        key_dict = RateLimit.limit_dict.get(key, {})
        user_reqs = key_dict.get(user, [])

        if(len(user_reqs) < self.limit):
            user_reqs.append(int(time.time()))

        key_dict[user] = user_reqs
        RateLimit.limit_dict[key] = key_dict

    def trim_requests(self):
        """Automatically remove requests older than the limit."""
        cutoff = int(time.time()) - RateLimit.per

        # TODO: This is horrifying, rewrite it.

        RateLimit.limit_dict = dict(
            (key,
             dict((user,
                   # Take only the requests that are still valid
                   [r for r in reqs if r > cutoff]) for (user, reqs)
                  in users.items()))

            for (key, users) in
            RateLimit.limit_dict.items()
        )

    remaining = property(lambda x: RateLimit.limit - x.current)
    over_limit = property(lambda x: x.current >= RateLimit.limit)


def get_view_rate_limit():
    """Get the ratelimit for the current requester/API method"""
    return getattr(flask.g, '_view_rate_limit', None)


def on_over_limit(limit):
    """Callback function to call when API method goes over the ratelimit"""
    return translate.utils.api_abort('ratelimit',
                                     'Rate limit hit, slow down!')


def ratelimit(send_x_headers=True, over_limit_func=on_over_limit):
    """Decorator to allow current Flask route to be rate-limited.

    send_x_headers -- should we add X-RateLimit-* headers to the request?
    over_limit_func -- function to call instead of API endpoint when limit is
                       hit.
    """
    def decorator(f):
        def rate_limited(*args, **kwargs):
            if RateLimit.enabled:
                rlimit = RateLimit(flask.request.remote_addr,
                                   flask.request.endpoint,
                                   send_x_headers)
                flask.g._view_rate_limit = rlimit
                if over_limit_func is not None and rlimit.over_limit:
                    return over_limit_func(rlimit)

            return f(*args, **kwargs)
        return update_wrapper(rate_limited, f)
    return decorator
