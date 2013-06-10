# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractproperty


class AbstractBackend:
    """Base backend class definition for any additional backends.

    Every backend must implement inherit AbstractBackend and define the
    following member functions/variables:

    TODO: write me

    To register the backend, do

    ::
      AbstractBackend.register(MyBackendClass)

    """

    __metaclass__ = ABCMeta

    @abstractproperty
    def language_pairs():
        """Return a list of tuples containing ("from-lang", "to-lang") to
        indicate language pair support.

        The languages should be in ISO-639_ format, using ISO-639-1 if possible
        and falling back to ISO-639-2 if necessary.

        .. _ISO-639: http://www.loc.gov/standards/iso639-2/php/English_list.php
        """
        pass
