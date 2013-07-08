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

    def shutdown(self):
        """Calls the deactivate functions for each of the backends to give them
        a chance to clean up after themselves if necessary.

        Called on server exit"""

        for backend in self.backends:
            backend.deactivate()

    def load_backends(self, dir_name):
        """Load all backends from the given absolute directory name"""

        for subclass, module in utils.find_subclasses(dir_name, IBackend):
            backend_conf = self.config.get(module, dict())

            # Update the preference according the configuration
            if 'preference' in backend_conf:
                subclass.preference = backend_conf['preference']

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


class TranslationException(Exception):
    """Exception to be raised when a translation backend fails to translate a
    given block of text for whatever reason.
    """
    pass


class IBackend:
    """Backend interface definition for any additional backends.

    Every backend must be a subclass for IBackend and override each of the
    members/functions present here.

    If some members are missing when the BackendManager attempts to instantiate
    the plugin class, a TypeError will be thrown, and the backend will be
    unable to load.
    """

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def activate(self, config):
        """Called upon initial activation of the backend. Should return either
        True or false to indicate whether or not activation was successful and
        the backend can be used.

        Config passed to this function is a dict, taken from the configuration
        file, using the module name of the backend as a key. e.g.
        plugins/foo/bar.py would be passed config['backends']['bar']
        """
        pass

    @abc.abstractmethod
    def deactivate(self):
        """Called upon backend deactivation (so on shutdown/reload/etc.).

        This function should perform any required clean up that needs to be
        done.
        """
        pass

    @abc.abstractmethod
    def translate(self, text, from_lang, to_lang):
        """Translate the given text from `from_lang` to `to_lang`.

        A backend will only receive this function call if has already specified
        that it can accept the given from,to pair.

        If the backend fails to produce a valid response for the given text, it
        should raise a translate.backend.TranslationException, which is a
        simple, featureless subclass of Exception. This way, the BackendManager
        will know that the request failed, and a proper error message can be
        issued to the user -- or whatever the proper course of action may be.
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

        This value can be overridden by the user by changing the relevant
        'preference' key in the settings.
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

    @abc.abstractproperty
    def url(self):
        """A link to where to find more information on this URL."""
        pass
