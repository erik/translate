import translate.app
import translate.client
import translate.client.exceptions as tce

import time
import yaml
import requests
import pytest
import flask
import json

from multiprocessing import Process


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
            (tce.TranslateException, 500,
             {'something else': 'foobar'}, {})
        ]

        for err in errs:
            print("testing " + str(err[0]))

            resp = flask.Response(response=json.dumps(err[2]),
                                  status=err[1])
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
            (tce.TranslateException, 500)
        ]

        for err in errs:
            print("testing " + str(err[0]))

            resp = flask.Response(response='}invalid-JSON',
                                  status=err[1])
            ex = tce.TranslateException.from_response(resp)

            assert isinstance(ex, err[0])
            assert str(ex) is not None


class TestClient():

    def setup_class(self):
        config = yaml.load("""
SERVER:
  bind: '0.0.0.0'
  port: 8765

BACKENDS:
  dummy:
    active: true
  apertium:
    active: false
  apertiumweb:
    active: false
""")

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

    def teardown_class(self):
        if self.thread.is_alive():
            self.thread.terminate()

    def test_init_sanity(self):
        assert self.client.host == 'localhost'
        assert self.client.port == 8765
        assert self.client.scheme == 'http'
        assert self.client.base_url == 'http://localhost:8765/api/v1/'

    def test_language_pairs(self):
        assert self.client.language_pairs() == [('en', 'en')]
        assert self.client.pairs == [('en', 'en')]
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

    def test_client_raises_exceptions(self):
        # TODO: write me
        pass
