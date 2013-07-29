# -*- coding: utf-8 -*-

"""
translate.client.client
~~~~~~~~~~~~~~~~~~~~~~~

"""

import json
import requests
import urllib

from .exceptions import HTTPException, TranslateException, \
    BadLanguagePairException

import logging
logging.basicConfig()
log = logging.getLogger(__name__)

# TODO: Handle rate limiting
# TODO: Handle size limiting automatically (split into multiple requests)
# TODO: More (i.e. some) error handling
# TODO: All of these functions assume good JSON (exc. explicit errors). This is
#       probably very bad.


class Client(object):
    """A client for interacting with translate server v1 API

    Note that almost every function here may raise a
    translate.exceptions.TranslateException, if communication to the server
    fails.
    """

    def __init__(self, host, port=5000, scheme='http', timeout=5, **kwargs):
        """Set up Client object.

        :param host: hostname if the translate server to connect to.
        :param port: port number translate server is on.
        :param scheme: if the server is using SSL, change this to
        'https'
        :param timeout: number of seconds after which to give up on
        requests.
        """
        self.host = host
        self.scheme = scheme
        self.port = port
        self.timeout = timeout
        self.options = kwargs

        self.base_url = "{0}://{1}:{2}/api/v1/".format(self.scheme, self.host,
                                                       self.port)

        # Private variables (a lot more likely to change / be unsuitable for
        # public API use)
        self._pairs = None
        self._backends = None
        self._sizelimit = None
        self._ratelimit = None
        self._info_fetched = False

    def can_connect(self):
        """Try to connect to the specified server. If a dummy request succeeds,
        True will be returned. If some kind of connection error (timeout, HTTP
        status != 200, ...) occurs, then False will be returned.
        """

        # Let's save some time and do something that will be useful anyway...
        try:
            self.info(refresh=True)
        except TranslateException as exc:
            log.warning("Couldn't reach %s: %s", self.base_url, str(exc))
            return False

        return True

    def info(self, ignore_ratelimit=False, refresh=False):
        """Collect information about this instance of the translate
        server.

        This function uses the /api/v1/info method to collect its information.

        A dict is returned containing the relevant info::

          {'backends': { NAME : ... },
           'ratelimit': { ... }, (False if ratelimit disabled)
           'sizelimit': int or False if sizelimit disabled
          }

        See the API documentation for the contents of the 'backends' and
        'ratelimit' dicts.

        Note that if refresh=False and the data has already been collected,
        an additional call to /api/v1/ratelimit will have to be made to avoid
        stale data or guesses.

        :param ignore_ratelimit: If this is True, won't bother to make a
                                 separate request for current ratelimit
                                 information. This is a bit quicker if you
                                 don't need the info anyway.
        :param refresh: Whether or not to ignore cached data and redownload.
        """
        # TODO: use namedtuple instead of dict for response object?
        # TODO: Test all of this!

        response = {}

        if not self._info_fetched or refresh:
            obj = self._request('info')

            self._backends = {}

            for b in obj['backends']:
                # Convert arrays to tuples
                b['pairs'] = [(p[0], p[1]) for p in b['pairs']]
                self._backends[b['name']] = b

            # Make sure these don't get out of sync by forcing language pairs
            # to regenerate as well
            self._pairs = None

            if 'sizelimit' in obj:
                self._sizelimit = obj['sizelimit']
            else:
                self._sizelimit = False

            if 'ratelimit' in obj:
                response['ratelimit'] = obj['ratelimit']

            self._info_fetched = True

        elif not ignore_ratelimit:
            limit_obj = self._request('ratelimit')

            if not limit_obj == {}:
                response['ratelimit'] = limit_obj

        else:
            if self._ratelimit is not None:
                response['ratelimit'] = self._ratelimit

        response['backends'] = self._backends
        response['sizelimit'] = self._sizelimit

        if 'ratelimit' in response:
            self._ratelimit = response['ratelimit']

            # Don't store transient information
            del self._ratelimit['reset']
            del self._ratelimit['methods']

        return response

    def language_pairs(self, refresh=False):
        """Get the list of supported language pairs. If refresh is True, will
        ignore previously cached results and hit the server again.

        :param refresh: Whether or not to ignore cached data and redownload.
        """

        if refresh or (self._pairs is None):
            obj = self._request('pairs')
            self._pairs = [(p[0], p[1]) for p in obj['pairs']]

        return self._pairs

    def translators(self, refresh=False):
        """Returns a dict containing names of translation services available
        and some basic info about them

        :param refresh: Whether or not to ignore cached data and redownload.
        """

        if refresh or (self._backends is None):
            obj = self._request('translators')

            self._backends = {}

            for b in obj['backends']:
                # Convert arrays to tuples
                b['pairs'] = [(p[0], p[1]) for p in b['pairs']]
                self._backends[b['name']] = b

            # Make sure these don't get out of sync by forcing language pairs
            # to regenerate as well
            self._pairs = None

        return self._backends

    def translate(self, text, from_lang, to_lang, refresh=False):
        """Translate a given string of text between languages.

        :param text: String of text to translate.
        :param from_lang: Language to translate from.
        :param to_lang: Language to translate to.
        :param refresh: Whether or not to ignore cached data and redownload.
        """

        # Check that we're translating between valid languages
        if (from_lang, to_lang) not in self.language_pairs(refresh=refresh):
            raise BadLanguagePairException(lang_pair=(from_lang, to_lang))

        try:
            kwargs = {'from': from_lang, 'to': to_lang, 'text': text}
            obj = self._request('translate', **kwargs)

            return obj['result']

        except TranslateException as exc:
            log.error("Failed to translate text (%s-%s): %s",
                      from_lang, to_lang, exc)
            raise exc

    def batch_translate(self, params, ignore_timeout=False):
        """Translate multiple texts and language pairs in a single
        call. Returns a list of strings containing the resulting translated
        texts, or an Exception object, if the request failed.

        This function won't raise any exceptions explicitly, so it's important
        to check the results.

        XXX: Is this Pythonic or even good API design? Not sure how else to
             handle it.

        :param params: list of (text, from_lang, to_lang).
        :param ignore_timeout: (False) Making N requests will likely take N
                               times as long, so it may be a good idea to
                               ignore the HTTP request timeout time
        """

        orig_timeout = self.timeout

        if ignore_timeout:
            # I think 1000 seconds is more than reasonable as a cut off. (Who
            # would wait >16 minutes for this?)
            self.timeout = 1000

        urls = []

        # TODO: could do client-side checking to see if lang pair
        #       supported. I doubt it would help much of anything.
        for tupl in params:
            if len(tupl) != 3:
                raise ValueError("Badly formed argument, expected tuple \
of (text, from, to), got " + repr(tupl))

            text = urllib.quote(tupl[0], safe='')
            from_lang = urllib.quote(tupl[1], safe='')
            to_lang = urllib.quote(tupl[2], safe='')

            urls.append("/api/v1/translate?from={0}&to={1}&text={2}"
                        .format(from_lang, to_lang, text))

        results = []

        try:
            objs = self._post_request('batch', urls=json.dumps(urls))

            for obj in objs:
                if obj['status'] != 200:
                    results.append(TranslateException.
                                   from_json(obj, obj['status']))
                else:
                    results.append(obj['data']['result'])

        except TranslateException as exc:
            log.error("Failed batch translate: %s", str(exc))
            raise exc

        finally:
            self.timeout = orig_timeout

        return results

    def can_translate(self, from_lang, to_lang, refresh=False):
        """Returns whether or not the translate server supports the given
        language pair.

        :param from_lang: Language to translate from.
        :param to_lang: Language to translate to.
        :param refresh: Whether or not to ignore cached data and redownload.
        """

        return (from_lang, to_lang) in self.language_pairs(refresh=refresh)

    def _request(self, method, **kwargs):
        """Convenience function to call an API function for the given client
        and return parsed JSON, or raise a TranslateException on error.
        """

        url = self.base_url + method

        try:
            req = requests.get(url, timeout=self.timeout, params=kwargs)
        except requests.exceptions.RequestException as exc:
            raise HTTPException(repr(exc))

        if req.status_code != 200:
            raise TranslateException.from_response(req)

        obj = json.loads(req.text)

        return obj

    def _post_request(self, method, **kwargs):
        """Same concept as _request, this function sends a HTTP POST with the
        given kwargs as POST data"""

        url = self.base_url + method

        try:
            req = requests.post(url, timeout=self.timeout, data=kwargs)
        except requests.exceptions.RequestException as exc:
            raise HTTPException(repr(exc))

        if req.status_code != 200:
            raise TranslateException.from_response(req)

        obj = json.loads(req.text)

        return obj
