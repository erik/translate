# -*- coding: utf-8 -*-

import flask
import json

import translate
from translate.app import app
from translate.app import views
from translate.backend import BackendManager

import requests


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
                       'text=baz', 'from=en&text=foo&to=bad-lang']:
            resp = self.client.get('/api/v1/translate?' + params)

            assert resp.status_code != 200

            js = json.loads(resp.data)

            assert js is not None
