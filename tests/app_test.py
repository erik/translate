# -*- coding: utf-8 -*-

import flask
import json

import translate
from translate.app import app
from translate.app import views

import requests


class TestApp():

    def setup_class(self):
        views.manager = translate.backend.BackendManager({})

        app.config['TESTING'] = True

        self.client = app.test_client()

    def teardown_class(self):
        pass

    def test_render_index(self):
        resp = self.client.get('/')

        assert resp.status_code == 200

    def test_render_api(self):
        # redirects to /api/
        assert self.client.get('/api').status_code == 301

        assert self.client.get('/api/').status_code == 200

    def test_404(self):
        resp = self.client.get('/asdasdasdasd')

        assert resp.status_code == 404
