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

        for subclass in utils.find_subclasses(dir_name, IBackend):
            try:
                backend = subclass(self.config)
            except TypeError as e:
                log.warning('Failed to load backend {0}, does it implement ' +
                            'all necessary functions and properties?'
                            .format(subclass.__name__))
                log.warning(repr(e))
                continue
            except Exception as e:
                log.warning('Failed to load backend {0} due to exception'
                            .format(subclass.__name__))
                log.warning(repr(e))
                continue

            log.info("Loading backend {0}... ".format(backend.name))
            self.backends.append(backend)

    def find_all(self, src, dst):
        """Return all translation backends that can possibly serve this
        request"""

        return [b for b in self.backends if (src, dst) in b.language_pairs()]

    def find_best(self, src, dst):
        """Find the best backend service for a given language pair"""

        best = (None, -1)

        for backend in self.backends:
            if (src, dst) in backend.language_pairs():
                if backend.preference > best[1]:
                    best = (backend, backend.preference)

        return best[0]


class IBackend:
    """Backend interface definition for any additional backends.

    Every backend must implement inherit IBackend and define the
    members/functions present here.
    """

    __metaclass__ = abc.ABCMeta

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
        """Return a list of tuples containing ("from-lang", "to-lang") to
        indicate language pair support.

        The languages should be in ISO-639_ format, using ISO-639-1 if possible
        and falling back to ISO-639-2 if necessary.

        .. _ISO-639: http://www.loc.gov/standards/iso639-2/php/English_list.php
        """
        pass
