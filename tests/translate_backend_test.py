import translate.app

from translate.backends.translate_backend import TranslateBackend

import time
import yaml
import requests

from multiprocessing import Process


class TestTranslateBackend():

    def setup_class(self):
        config = yaml.load("""
server:
  bind: '0.0.0.0'
  port: 9876

backends:
  dummy:
    active: true
  apertium:
    active: false
  apertiumweb:
    active: false
""")

        # Hackiness to make sure this is always prefered
        TranslateBackend.preference = 1000

        self.backend = TranslateBackend()

        self.thread = Process(target=translate.app.start, args=(config, True))
        self.thread.start()

        # Wait for the server to spin up
        while True:
            time.sleep(0.5)
            try:
                requests.get('http://localhost:9876')
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
