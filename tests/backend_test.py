import pytest

import translate
import translate.backend


class TestBackendManager:

    @classmethod
    def setup_class(self):
        self.mgr = translate.backend.BackendManager()


    def test_default_loads(self):
        assert len(self.mgr.backends) == 1
        assert self.mgr.backends[0].__module__ == 'translate.backends.dummy'


    def test_dummy(self):
        assert True
