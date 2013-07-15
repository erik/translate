# -*- coding: utf-8 -*-

import json

from translate.app import app, views
from translate.app.ratelimit import RateLimit
from translate.backend import BackendManager


class TestAPI():

    def setup_class(self):
        views.manager = BackendManager({})
        app.config['TESTING'] = True
        self.client = app.test_client()

    def teardown_class(self):
        pass

    def test_jsonp(self):
        for path in ['/api/v1/pairs?callback=foo',
                     '/api/v1/translators?callback=foo',
                     '/api/v1/translate?callback=foo']:
            resp = self.client.get(path)
            assert resp.data.startswith('foo(')

            # Strip jsonp (doesn't parse here)
            assert json.loads(resp.data[4:-1]) is not None

    def test_pairs_good_input(self):
        for path in ['/api/v1/pairs']:
            resp = self.client.get(path)
            assert resp.status_code == 200
            js = json.loads(resp.data)
            assert js is not None
            assert 'pairs' in js

    def test_translators_good_input(self):
        for path in ['/api/v1/translators']:
            resp = self.client.get(path)
            assert resp.status_code == 200
            js = json.loads(resp.data)
            assert js is not None
            assert 'backends' in js

    def test_translate_bad_input(self):
        for params in ['', 'from=foo&to=bar&text=baz', 'to=bar&text=baz',
                       'text=baz', 'from=en&text=foo&to=bad-lang',
                       'from=en&to=en&text=']:
            resp = self.client.get('/api/v1/translate?' + params)

            assert resp.status_code != 200

            js = json.loads(resp.data)

            assert js is not None

    def test_errors(self):
        """Make sure API functions return proper error codes/information"""

        # Kill the limiter for now
        RateLimit.enabled = False

        # Test format of error messages
        resp = self.client.get('/api/v1/translate')
        assert resp.status_code == 452
        js = json.loads(resp.data)

        assert js is not None

        for pair in [('status', 'Translation error'),
                     ('url', 'http://localhost/api/v1/translate'),
                     ('code', 452),
                     ('details', {})]:
            assert js[pair[0]] == pair[1]

        # Bad params
        for params in ['', 'from=foo&to=bar', 'from=foo&to=bar&text=',
                       'from=foo&text=bar']:
            resp = self.client.get('/api/v1/translate?' + params)
            assert resp.status_code == 452
            assert resp.status == "452 Translation error"

            js = json.loads(resp.data)
            assert js is not None

        # No translators
        resp = self.client.get('/api/v1/translate?from=foo&to=bar&text=foobar')
        assert resp.status_code == 454

        js = json.loads(resp.data)
        assert js['details']['from'] == 'foo'
        assert js['details']['to'] == 'bar'
        assert js['details']['text'] == 'foobar'

        # No translators (due to exclusion)
        resp = self.client.get('/api/v1/translate?from=en&to=en&text=foobar&\
exclude=Dummy')

        js = json.loads(resp.data)
        assert js['details']['from'] == 'en'
        assert js['details']['to'] == 'en'
        assert js['details']['text'] == 'foobar'

        assert resp.status_code == 454
