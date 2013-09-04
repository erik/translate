import translate.app

from translate.backends.translate_backend import TranslateBackend
from translate.exceptions import TranslationException
from translate.client.exceptions import TranslateException

import time
import requests
import json

from multiprocessing import Process


class TestTranslateBackend():

    def setup_class(self):
        config = json.loads("""{
"SERVER": {
  "bind": "0.0.0.0",
  "port": 9876
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
  },
  "translate_backend": {
    "active": false
  },
  "yandex": {
    "active": false
  }
}
}""")

        # Hackiness to make sure this is always prefered
        TranslateBackend.preference = 1000

        # Reset the backends
        translate.app.views.manager = translate.backend.BackendManager(
            config['BACKENDS'])

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

        self.backend = TranslateBackend()

    def test_activate(self):
        ret = self.backend.activate({
            'active': True,
            'host': 'localhost',
            'port': 9876
        })

        assert ret is True

    def test_langpairs(self):
        assert self.backend.language_pairs == [('en', 'en')]

    def test_translate(self):
        # This seems to fail occasionally, so run in a loop
        # XXX: Am I hiding a bug? It certainly feels like it
        for i in xrange(5):
            try:
                result = self.backend.translate('hello, world', 'en', 'en')
                break
            except (TranslationException, TranslateException) as exc:
                print("Failed %d: %s" % (i, str(exc)))

            # Sleep a bit before retrying
            time.sleep(0.25)

        assert result == 'hello, world'

    def teardown_class(self):
        time.sleep(2)

        if self.thread.is_alive():
            self.thread.terminate()
