import subprocess

from translate.backends.apertiumweb import ApertiumWebBackend, API_URL

import requests

try:
    # If this times out, just give up with the test
    requests.get(API_URL, timeout=5)

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

except requests.exceptions.RequestException as exc:
    print('Skipping apertiumweb backend tests')
