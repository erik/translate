from translate.backends.apertiumweb import ApertiumWebBackend, API_URL

import requests
import json

try:
    # If this times out, just give up with the test
    r = requests.get(API_URL + 'listPairs', timeout=5)
    obj = json.loads(r.text)

    # It seems Apertium Web API sometimes returns a nothing response
    assert obj['responseData'] != []
    assert r.status_code == 200

    class TestApertiumWeb:

        def setup_class(self):
            self.backend = ApertiumWebBackend()

        def test_init(self):
            assert self.backend.activate(dict())
            assert len(self.backend.language_pairs) != 0

        def test_translate(self):
            pair = self.backend.language_pairs[0]

            trans = self.backend.translate('hello', pair[0], pair[1])
            assert trans is not None

except:
    print('Skipping apertiumweb backend tests')
