# -*- coding: utf-8 -*-

# This file is part of translate.
#
# translate is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# translate is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# translate.  If not, see <http://www.gnu.org/licenses/>.


"""
translate.utils
~~~~~~~~~~~~~~~

This module contains small utility snippets of code adapted to be useful for
this project. If these were not directly written for the translate project,
a link to the original source is included in the docstring.
"""

from . import log

import flask
import inspect
import subprocess
import pkgutil
import collections

from functools import wraps


def find_subclasses(path, cls):
    """Return a list of tuples containing (subclass, modulename).

    path: path to search for subclasses
    cls: class to find subclasses of
    """
    subclasses = []

    for loader, name, _ in pkgutil.walk_packages([path]):
        module = loader.find_module(name).load_module(name)
        log.debug("Searching module %s" % (name))

        for key, entry in inspect.getmembers(module, inspect.isclass):
            if key == cls.__name__:
                continue

            try:
                if issubclass(entry, cls):
                    log.debug("Found subclass: "+key)
                    subclasses.append((entry, name))
            except TypeError:
                continue

    return subclasses


def jsonp(func):
    """Wraps JSONified output for JSONP requests.

    From: https://gist.github.com/aisipos/1094140
    """
    @wraps(func)
    def decorated_function(*args, **kwargs):
        callback = flask.request.args.get('callback', False)
        if callback:
            data = str(func(*args, **kwargs).data)
            content = str(callback) + '(' + data + ')'
            mimetype = 'application/javascript'
            return flask.current_app.response_class(content, mimetype=mimetype)
        else:
            return func(*args, **kwargs)
    return decorated_function


# Python 2.6 doesn't support subprocess.check_output, so monkey-patch it in
if "check_output" not in dir(subprocess):
    def f(*popenargs, **kwargs):
        if 'stdout' in kwargs:
            raise ValueError('stdout argument not allowed, ' +
                             'it will be overridden.')
        process = subprocess.Popen(stdout=subprocess.PIPE,
                                   *popenargs, **kwargs)
        output, _ = process.communicate()
        retcode = process.poll()
        if retcode:
            cmd = kwargs.get("args")
            if cmd is None:
                cmd = popenargs[0]
            raise subprocess.CalledProcessError(retcode, cmd)
        return output
    subprocess.check_output = f


def update(d, u, depth=-1):
    """Recursively merge or update dict-like objects.
    >>> update({'k1': {'k2': 2}}, {'k1': {'k2': {'k3': 3}}, 'k4': 4})
    {'k1': {'k2': {'k3': 3}}, 'k4': 4}

    Code from: http://stackoverflow.com/a/14048316
    """

    for k, v in u.iteritems():
        if isinstance(v, collections.Mapping) and not depth == 0:
            r = update(d.get(k, {}), v, depth=max(depth - 1, -1))
            d[k] = r
        elif isinstance(d, collections.Mapping):
            d[k] = u[k]
        else:
            d = {k: u[k]}
    return d


def chunk_string(string, n):
    """Yield successive n-byte sized substrings from string.

    TODO: Split on word boundaries instead of middle of word...

    Code adapted from: http://stackoverflow.com/a/312464
    """

    for i in xrange(0, len(string.encode('utf-8')), n):
        yield string[i:i+n]


def iso639_convert(code):
    """Convert ISO639-2 language codes into ISO639-1 codes, and vice
    versa.

    Returns the code unchanged when no conversion is possible."""

    # Keep everything downcased for consistency.
    code = code.lower()

    if(len(code) == 3):  # 3 char to 2 char
        for lang in ISO_639_LANGS:
            if code == lang[0] or code == lang[1]:
                return lang[2]

    elif(len(code) == 2):  # 2 char to 3 char
        for lang in ISO_639_LANGS:
            if code == lang[2]:
                return lang[0]

    return code


ISO_639_LANGS = [
    # [0]: an alpha-3 (bibliographic) code
    # [1]: an alpha-3 (terminologic) code (when given)
    # [2]: an alpha-2 code
    ["aar", "", "aa"],
    ["abk", "", "ab"],
    ["afr", "", "af"],
    ["aka", "", "ak"],
    ["alb", "sqi", "sq"],
    ["amh", "", "am"],
    ["ara", "", "ar"],
    ["arg", "", "an"],
    ["arm", "hye", "hy"],
    ["asm", "", "as"],
    ["ava", "", "av"],
    ["ave", "", "ae"],
    ["aym", "", "ay"],
    ["aze", "", "az"],
    ["bak", "", "ba"],
    ["bam", "", "bm"],
    ["baq", "eus", "eu"],
    ["bel", "", "be"],
    ["ben", "", "bn"],
    ["bih", "", "bh"],
    ["bis", "", "bi"],
    ["bos", "", "bs"],
    ["bre", "", "br"],
    ["bul", "", "bg"],
    ["bur", "mya", "my"],
    ["cat", "", "ca"],
    ["cha", "", "ch"],
    ["che", "", "ce"],
    ["chi", "zho", "zh"],
    ["chu", "", "cu"],
    ["chv", "", "cv"],
    ["cor", "", "kw"],
    ["cos", "", "co"],
    ["cre", "", "cr"],
    ["cze", "ces", "cs"],
    ["dan", "", "da"],
    ["div", "", "dv"],
    ["dut", "nld", "nl"],
    ["dzo", "", "dz"],
    ["eng", "", "en"],
    ["epo", "", "eo"],
    ["est", "", "et"],
    ["ewe", "", "ee"],
    ["fao", "", "fo"],
    ["fij", "", "fj"],
    ["fin", "", "fi"],
    ["fre", "fra", "fr"],
    ["fry", "", "fy"],
    ["ful", "", "ff"],
    ["geo", "kat", "ka"],
    ["ger", "deu", "de"],
    ["gla", "", "gd"],
    ["gle", "", "ga"],
    ["glg", "", "gl"],
    ["glv", "", "gv"],
    ["gre", "ell", "el"],
    ["grn", "", "gn"],
    ["guj", "", "gu"],
    ["hat", "", "ht"],
    ["hau", "", "ha"],
    ["heb", "", "he"],
    ["her", "", "hz"],
    ["hin", "", "hi"],
    ["hmo", "", "ho"],
    ["hrv", "", "hr"],
    ["hun", "", "hu"],
    ["ibo", "", "ig"],
    ["ice", "isl", "is"],
    ["ido", "", "io"],
    ["iii", "", "ii"],
    ["iku", "", "iu"],
    ["ile", "", "ie"],
    ["ina", "", "ia"],
    ["ind", "", "id"],
    ["ipk", "", "ik"],
    ["ita", "", "it"],
    ["jav", "", "jv"],
    ["jpn", "", "ja"],
    ["kal", "", "kl"],
    ["kan", "", "kn"],
    ["kas", "", "ks"],
    ["kau", "", "kr"],
    ["kaz", "", "kk"],
    ["khm", "", "km"],
    ["kik", "", "ki"],
    ["kin", "", "rw"],
    ["kir", "", "ky"],
    ["kom", "", "kv"],
    ["kon", "", "kg"],
    ["kor", "", "ko"],
    ["kua", "", "kj"],
    ["kur", "", "ku"],
    ["lao", "", "lo"],
    ["lat", "", "la"],
    ["lav", "", "lv"],
    ["lim", "", "li"],
    ["lin", "", "ln"],
    ["lit", "", "lt"],
    ["ltz", "", "lb"],
    ["lub", "", "lu"],
    ["lug", "", "lg"],
    ["mac", "mkd", "mk"],
    ["mah", "", "mh"],
    ["mal", "", "ml"],
    ["mao", "mri", "mi"],
    ["mar", "", "mr"],
    ["may", "msa", "ms"],
    ["mlg", "", "mg"],
    ["mlt", "", "mt"],
    ["mon", "", "mn"],
    ["nau", "", "na"],
    ["nav", "", "nv"],
    ["nbl", "", "nr"],
    ["nde", "", "nd"],
    ["ndo", "", "ng"],
    ["nep", "", "ne"],
    ["nno", "", "nn"],
    ["nob", "", "nb"],
    ["nor", "", "no"],
    ["nya", "", "ny"],
    ["oci", "", "oc"],
    ["oji", "", "oj"],
    ["ori", "", "or"],
    ["orm", "", "om"],
    ["oss", "", "os"],
    ["pan", "", "pa"],
    ["per", "fas", "fa"],
    ["pli", "", "pi"],
    ["pol", "", "pl"],
    ["por", "", "pt"],
    ["pus", "", "ps"],
    ["que", "", "qu"],
    ["roh", "", "rm"],
    ["rum", "ron", "ro"],
    ["run", "", "rn"],
    ["rus", "", "ru"],
    ["sag", "", "sg"],
    ["san", "", "sa"],
    ["sin", "", "si"],
    ["slo", "slk", "sk"],
    ["slv", "", "sl"],
    ["sme", "", "se"],
    ["smo", "", "sm"],
    ["sna", "", "sn"],
    ["snd", "", "sd"],
    ["som", "", "so"],
    ["sot", "", "st"],
    ["spa", "", "es"],
    ["srd", "", "sc"],
    ["srp", "", "sr"],
    ["ssw", "", "ss"],
    ["sun", "", "su"],
    ["swa", "", "sw"],
    ["swe", "", "sv"],
    ["tah", "", "ty"],
    ["tam", "", "ta"],
    ["tat", "", "tt"],
    ["tel", "", "te"],
    ["tgk", "", "tg"],
    ["tgl", "", "tl"],
    ["tha", "", "th"],
    ["tib", "bod", "bo"],
    ["tir", "", "ti"],
    ["ton", "", "to"],
    ["tsn", "", "tn"],
    ["tso", "", "ts"],
    ["tuk", "", "tk"],
    ["tur", "", "tr"],
    ["twi", "", "tw"],
    ["uig", "", "ug"],
    ["ukr", "", "uk"],
    ["urd", "", "ur"],
    ["uzb", "", "uz"],
    ["ven", "", "ve"],
    ["vie", "", "vi"],
    ["vol", "", "vo"],
    ["wel", "cym", "cy"],
    ["wln", "", "wa"],
    ["wol", "", "wo"],
    ["xho", "", "xh"],
    ["yid", "", "yi"],
    ["yor", "", "yo"],
    ["zha", "", "za"],
    ["zul", "", "zu"],
]
