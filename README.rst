=========
translate
=========

.. image:: https://travis-ci.org/boredomist/translate.png?branch=master
   :target: https://travis-ci.org/boredomist/translate

About
_____

This project is part of Google Summer of Code 2013, working with the `Sugar Labs
<http://sugarlabs.org>`_ project.

This README will become more useful over time, but for now, a more complete
overview of the goals that I intend to accomplish with this project can be found
`on the Sugar Labs wiki
<http://wiki.sugarlabs.org/go/Summer_of_Code/Translation_Server>`_.

In brief, this project aims to create a server application that provides a
convenient interface to many machine translation backends, automatically, as
well as a Python API to utilize this server.

And yes, the actual name is pending.

Setup
_____

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

That should be it. Installing is currently working, but not terribly useful. To
run::

    ./bin/translate [--debug]

The debug flag is useful if you're doing any kind of development, as it will
reload the server when a changed file is detected.

Alternatively, using uWSGI (other systems should be similar)::

    uwsgi -s /tmp/mysock.sock -w translate.app:app [--http 127.0.0.1:8080]

The http flag tells uwsgi to use its HTTP server. Don't use it if
you're using some other server (Apache, nginx, ...).


Setup with nginx
~~~~~~~~~~~~~~~~

This is an example setup of translate using a internet-facing nginx server and
uWSGI to serve up the translate app. Modify as necessary. Eventually, I'll
create a fabric deployment script (issue #14) to make this simpler.

Here is the relevant section of :code:`/etc/nginx/nginx.conf`. Make sure you
make any necessary adjustments::

  server {
    server_name translate.example.com;

    location / { try_files $uri @translate; }
    location @translate {
      include uwsgi_params;
      uwsgi_pass unix:///tmp/translate.sock;
    }
  }


After we have that setup, all that's left is to start uWSGI. Take a look at
:code:`translate.uwsgi` for a base configuration. I dropped everything in
:code:`/var/www/translate/`, but it can be placed wherever, so long as you
update the configuration.


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
