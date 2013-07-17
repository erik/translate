import translate.app

from translate.backends.translate_backend import TranslateBackend

import time
import yaml
import requests
import flask

from multiprocessing import Process


class TestTranslateBackend():

    def setup_class(self):
        config = yaml.load("""
SERVER:
  bind: '0.0.0.0'
  port: 9876

BACKENDS:
  dummy:
    active: true
  apertium:
    active: false
  apertiumweb:
    active: false
""")

        # Hackiness to make sure this is always prefered
        TranslateBackend.preference = 1000

        # Reset the backends
        translate.app.views.manager = translate.backend.BackendManager(
            config['BACKENDS'])

        self.backend = TranslateBackend()

        self.thread = Process(target=translate.app.start_server,
                              args=(config, True))
        self.thread.start()

        # Wait for the server to spin up
        while True:
            time.sleep(0.5)
            try:
                r = requests.get('http://localhost:9876/api/v1/pairs')
                if r.status_code == 200:
                    break
            except:
                pass

    def teardown_class(self):
        if self.thread.is_alive():
            self.thread.terminate()

    def test_setup_backend(self):

        ret = self.backend.activate({
            'active': True,
            'host': 'localhost',
            'port': 9876
        })

        assert ret is True

    def test_langpairs(self):
        assert self.backend.language_pairs == [('en', 'en')]

    def test_translate(self):
        result = self.backend.translate('hello, world', 'en', 'en')

        assert result == 'hello, world'
