import translate.app
import translate.client
import translate.client.exceptions as tce
import translate.app.ratelimit

import time
import requests
import pytest
import json

from multiprocessing import Process


class ResponseTester():
    """Same members as requests.models.Response, easier to construct"""
    def __init__(self, text, status_code):
        self.text = text
        self.status_code = status_code


class TestClientExceptions():

    def test_exception_creation(self):
        errs = [
            (tce.RateLimitException, 429,
             {'details': {'limit': 0, 'per': 1, 'reset': 2}},
             {'limit': 0, 'per': 1, 'reset': 2}),
            (tce.TranslationException, 452,
             {'message': 'foobar'}, {}),
            (tce.TranslatorException, 453,
             {'details': {'from': 'foo', 'to': 'bar', 'tried': ['foobar']}},
             {'lang_pair': ('foo', 'bar'), 'tried': ['foobar']}),
            (tce.BadLanguagePairException, 454,
             {'details': {'from': 'foo', 'to': 'bar'}},
             {'lang_pair': ('foo', 'bar')}),
            (tce.SizeLimitException, 431,
             {'details': {'limit': 123, 'len': 456}},
             {'limit': 123, 'len': 456}),
            (tce.TranslateException, 500,
             {'something else': 'foobar'}, {})
        ]

        for err in errs:
            print("testing " + str(err[0]))

            obj = err[2]
            obj['code'] = err[1]

            resp = ResponseTester(json.dumps(obj), err[1])
            ex = tce.TranslateException.from_response(resp)

            assert isinstance(ex, err[0])
            # Just make sure they can represent themselves
            assert str(ex) is not None

            for k, v in err[3].items():
                assert ex.__dict__[k] == v

    def test_exception_bad_input(self):
        """Same as above, with bad JSON input"""

        errs = [
            (tce.RateLimitException, 429),
            (tce.TranslationException, 452),
            (tce.TranslatorException, 453),
            (tce.BadLanguagePairException, 454),
            (tce.TranslateException, 500),
            (tce.SizeLimitException, 431)
        ]

        for err in errs:
            print("testing " + str(err[0]))

            resp = ResponseTester('}invalid-JSON', err[1])
            ex = tce.TranslateException.from_response(resp)

            assert isinstance(ex, err[0])
            assert str(ex) is not None


class TestClient():

    def setup_class(self):
        config = json.loads("""{
"SERVER": {
  "bind": "0.0.0.0",
  "port": 8765,
  "sizelimit": {
    "enabled": true,
    "limit": 987
  }
},

"BACKENDS": {
  "dummy": {
    "active": true
  },
  "apertium": {
    "active": false
  },
  "apertiumweb": {
    "active": false
  }
}
}""")
        translate.app.ratelimit.RateLimit.enabled = False
        translate.app.views.manager = translate.backend.BackendManager(
            config['BACKENDS'])

        self.client = translate.client.Client('localhost', port=8765)

        self.thread = Process(target=translate.app.start_server,
                              args=(config, True))
        self.thread.start()

        # Wait for the server to start up
        while True:
            time.sleep(0.25)
            try:
                r = requests.get('http://localhost:8765/api/v1/pairs')

                if r.status_code == 200:
                    break
            except:
                pass

    def test_init_sanity(self):
        assert self.client.host == 'localhost'
        assert self.client.port == 8765
        assert self.client.scheme == 'http'
        assert self.client.base_url == 'http://localhost:8765/api/v1/'

    def test_can_connect(self):
        assert self.client.can_connect()

        bad_client = translate.client.Client('foo.bar', port=1234)
        assert not bad_client.can_connect()

    def test_language_pairs(self):
        assert self.client.language_pairs() == [('en', 'en')]
        assert self.client._pairs == [('en', 'en')]
        assert self.client.language_pairs(True) == [('en', 'en')]

    def test_translators(self):
        trans = self.client.translators()
        assert 'Dummy' in trans
        assert trans['Dummy']['pairs'] == [('en', 'en')]
        assert len(trans.items()) == 1

        trans = self.client.translators(True)
        assert len(trans.items()) == 1

    def test_can_translate(self):
        assert self.client.can_translate('en', 'en')
        assert not self.client.can_translate('foo', 'bar')

    def test_translate(self):
        assert self.client.translate('foobarbaz', 'en', 'en') == 'foobarbaz'

        with pytest.raises(translate.client.exceptions.TranslateException):
            self.client.translate('bad', 'arguments', 'here')

    def test_batch_translate(self):
        results = self.client.batch_translate([('good', 'en', 'en'),
                                               ('bad', 'foo', 'bar'),
                                               ('good', 'en', 'en')])

        assert len(results) == 3
        assert results[0] == 'good'
        assert isinstance(results[1], tce.TranslateException)
        assert results[2] == 'good'

    def test_batch_bad_args(self):
        for bad in [[()], 'foo', [('a', 'a')]]:
            with pytest.raises(ValueError):
                self.client.batch_translate(bad)

    def test_info(self):
        resp = self.client.info(ignore_ratelimit=False, refresh=False)
        assert self.client._info_fetched is True
        assert self.client._info.sizelimit == 987

        assert isinstance(resp, translate.client.ServerInformation)

        assert resp.sizelimit == 987
        assert resp.ratelimit is False
        assert resp.version == translate.__version__

        self.client._info_fetched = "should not be reset"

        resp = self.client.info(ignore_ratelimit=False, refresh=False)
        assert self.client._info_fetched is "should not be reset"
        assert self.client._info.sizelimit == 987

        assert resp.sizelimit == 987
        assert resp.ratelimit is False
        assert resp.version == translate.__version__

    def test_sizelimit(self):
        text = '.' * 988

        with pytest.raises(tce.SizeLimitException):
            self.client.translate(text, 'en', 'en', split_text=False)

        # Make sure we hit another if block in translate
        self.client._info_fetched = False

        assert text == self.client.translate(text, 'en', 'en',
                                             split_text=True)

    def teardown_class(self):
        if self.thread.is_alive():
            self.thread.terminate()
