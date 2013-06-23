# -*- coding: utf-8 -*-

import abc
import utils

from . import log


class BackendManager:
    """Handles the loading and management of various translation service
    backends."""

    def __init__(self, config):
        self.backends = []
        self.config = config

        # Load the default backends
        self.load_backends('translate/backends')

    def load_backends(self, dir_name):
        """Load all backends from the given absolute directory name"""

        for subclass, module in utils.find_subclasses(dir_name, IBackend):
            backend_conf = self.config.get(module, dict())

            try:
                backend = subclass()
            except Exception as e:
                log.warning('Failed to load backend {0} due to exception. ' +
                            'Make sure it implements all required properties' +
                            ' and members'.format(subclass.__name__))
                log.warning(repr(e))
                continue

            if backend.activate(backend_conf):
                log.info("Loading backend {0}... ".format(backend.name))
                self.backends.append(backend)
            else:
                log.info("Disabling backend {0}...".format(backend.name))

    def find_all(self, src, dst):
        """Return all translation backends that can possibly serve this
        request, sorted by preference (high first)
        """

        backends = [b for b in self.backends
                    if (src, dst) in b.language_pairs]

        return sorted(backends, key=lambda b: b.preference)

    def find_best(self, src, dst):
        """Find the best backend service for a given language pair"""

        best = (None, -1)

        for backend in self.backends:
            if (src, dst) in backend.language_pairs:
                if backend.preference > best[1]:
                    best = (backend, backend.preference)

        return best[0]


class IBackend:
    """Backend interface definition for any additional backends.

    Every backend must implement inherit IBackend and define the
    members/functions present here.
    """

    __metaclass__ = abc.ABCMeta

    def activate(self, config):
        """Called upon initial activation of the backend. Should return either
        True or false to indicate whether or not activation was successful and
        the backend can be used.

        Config passed to this function is a dict, taken from the configuration
        file, using the module name of the backend as a key. e.g.
        plugins/foo/bar.py would be passed config['backends']['bar']
        """
        pass

    def deactivate(self):
        """Called upon backend deactivation (so on shutdown/reload/etc.).

        This function should perform any required clean up that needs to be
        done.
        """
        pass

    def translate(self, text, from_lang, to_lang):
        """Translate the given text from `from_lang` to `to_lang`.

        A backend will only receive this function call if has already specified
        that it can accept the given from,to pair.
        """
        pass

    @abc.abstractproperty
    def name(self):
        """Name of this translation backend."""
        pass

    @abc.abstractproperty
    def description(self):
        """Short description of this translation backend."""
        pass

    @abc.abstractproperty
    def preference(self):
        """Return an integer representing the overall precedence this
        translation backend should use.

        If two backends overlap for a language pair, the one with the highest
        preference is used.

        Higher values indicate a higher precedence.
        """
        pass

    @abc.abstractproperty
    def language_pairs(self):
        """A list of tuples containing ("from-lang", "to-lang") to
        indicate language pair support.

        The languages should be in ISO-639_ format, using ISO-639-1 if possible
        and falling back to ISO-639-2 if necessary.

        .. _ISO-639: http://www.loc.gov/standards/iso639-2/php/English_list.php
        """
        pass
