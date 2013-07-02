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

Currently working with Python 2.6 and 2.7. 3.x support may be included at some
point in the future, but don't count on it.

Setup process::

    pip install -r requirements.txt
    python setup.py develop
    # edit settings.py as needed

That should be it. Installing isn't currently working. To run::

    ./bin/translate [--debug] [--config /path/to/config]


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
