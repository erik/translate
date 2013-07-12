import translate.app
import translate.client

import time
import yaml
import requests
import pytest

from multiprocessing import Process


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
                requests.get('http://localhost:8765')
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

    def test_translate(self):
        assert self.client.translate('foobarbaz', 'en', 'en') == 'foobarbaz'

        with pytest.raises(translate.client.exceptions.TranslateException):
            self.client.translate('bad', 'arguments', 'here')
