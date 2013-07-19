# -*- coding: utf-8 -*-

"""Simple IP-based rate-limiting functionality for Flask routes.

This code is derived from http://flask.pocoo.org/snippets/70/ but doesn't rely
on redis. Opts for simple dictionary implementation instead.
"""

import time
import flask
import threading

from functools import update_wrapper
from translate.exceptions import APIException


RATELIMIT_MUTEX = threading.Lock()


class RateLimit(object):
    """This singleton class manages all API requests, taking care of pruning
    and adding them as necessary
    """

    limit_dict = {}

    enabled = False
    limit = 0
    per = 0
    reset = 0

    @staticmethod
    def enable(limit, per):
        """Initialize rate limiting with given limit / per values."""

        RateLimit.enabled = True
        RateLimit.limit = limit
        RateLimit.per = per
        RateLimit.reset = (time.time() // per) * per + per

    @staticmethod
    def add_request(user, key):
        """Record that the given user (IP-address) made a request to the
        specified API endpoint (/api/v1/METHOD)

        If the current ratelimit window has expired, clears all requests and
        resets the timer before adding the request in.
        """

        # GIL should take care of us, but just in case we'll obtain a lock so
        # concurrent requests can't do any harm.
        RATELIMIT_MUTEX.acquire()

        now = time.time()

        # Limit has expired, flush requests and reset timer
        if RateLimit.reset <= now:
            RateLimit.reset = (now // RateLimit.per) * RateLimit.per +\
                RateLimit.per

            RateLimit.limit_dict = {}

        key_dict = RateLimit.limit_dict.get(key, {})

        # Add to requests this user has made
        key_dict[user] = key_dict.get(user, 0) + 1

        RateLimit.limit_dict[key] = key_dict

        RATELIMIT_MUTEX.release()

    @staticmethod
    def remaining(user, key):
        """Return how many request the current user has for the given API
        method during this request period.
        """

        reqs = RateLimit.limit_dict.get(key, {}).get(user, 0)

        # Make sure we never return a negative number of requests remaining
        if reqs > RateLimit.limit:
            return 0

        return RateLimit.limit - reqs

    @staticmethod
    def over_limit(user, key):
        """Is the current user over the rate limit for the given API method"""
        reqs = RateLimit.limit_dict.get(key, {}).get(user, 0)
        return reqs > RateLimit.limit


def get_view_rate_limit_remaining():
    """Get the ratelimit for the current requester / API method"""
    return getattr(flask.g, '_view_rate_limit_remaining', None)


def get_view_send_x_headers():
    """Whether or not the current view should send X-RateLimit-* headers."""
    return getattr(flask.g, '_send_rate_limit_x_headers', False)


def on_over_limit():
    """Callback function to call when API method goes over the ratelimit"""

    raise APIException.ratelimit(limit=RateLimit.limit, per=RateLimit.per,
                                 reset=RateLimit.reset)


def ratelimit(send_x_headers=True, over_limit_func=on_over_limit):
    """Decorator to allow current Flask route to be rate-limited.

    send_x_headers -- should we add X-RateLimit-* headers to the request?
    over_limit_func -- function to call instead of API endpoint when limit is
    hit.
    """
    def decorator(f):
        def rate_limited(*args, **kwargs):
            if RateLimit.enabled:
                # Base rate limiting on IPs
                user = flask.request.remote_addr
                key = flask.request.endpoint

                RateLimit.add_request(user, key)

                flask.g._send_rate_limit_x_headers = send_x_headers
                flask.g._view_rate_limit_remaining =\
                    RateLimit.remaining(user, key)

                if over_limit_func is not None and\
                   RateLimit.over_limit(user, key):

                    return over_limit_func()

            return f(*args, **kwargs)
        return update_wrapper(rate_limited, f)
    return decorator
