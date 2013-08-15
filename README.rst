=========
translate
=========

.. image:: https://travis-ci.org/boredomist/translate.png?branch=master
   :target: https://travis-ci.org/boredomist/translate

About
_____

This project is part of Google Summer of Code 2013, working with the `Sugar Labs
<http://sugarlabs.org>`_ project.

A live instance of this project is hosted at `translate.erikprice.net
<http://translate.erikprice.net>`_. I wouldn't rely on it for production, but
feel free to use it as a test.

In brief, this project aims to create a server application that provides a
convenient interface to many machine translation backends, automatically, as
well as a Python API to utilize this server.

For some more complete information on how to use this server / client, check
out `the documentation <http://boredomist.github.io/translate>`_.

And yes, the actual name is pending.

Developing
__________

Setting this up should be pretty straightforward. Open an issue on the tracker
if you run into any issues getting this to work. I'd suggest doing this in a
virtualenv.

If you want to build the documentation in :code:`docs/`, you'll need Sphinx
(:code:`pip install Sphinx`).

Running the test suite and checking for linting errors requires a few
additional dependencies not specified in :code:`requirements.txt`. These are
not necessary if you aren't going to be working on the server. To install::

    pip install pytest flake8

Currently working with Python 2.6 and 2.7. 3.x support may be included at some
point in the future, but don't count on it.

Setup process::

    pip install -r requirements.txt
    python setup.py develop
    # edit settings.py as needed

That should be it. Try running the executables with the :code:`--help` flag to
get a sense of how to work with them::

    ./bin/translate --help
    ./bin/translate-client --help

The debug flag is useful if you're doing any kind of development, as it will
reload the server when a changed file is detected and print out some useful
information.

License
______

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program.  If not, see <http://www.gnu.org/licenses/>.
