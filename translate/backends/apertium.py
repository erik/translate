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

from translate.backend import IBackend
from translate.exceptions import TranslationException

import glob
import os
import re
import subprocess

import logging
log = logging.getLogger(__name__)


class ApertiumBackend(IBackend):
    name = "Apertium"
    description = "A free/open-source machine translation platform"
    url = 'http://apertium.org'
    preference = 20
    language_pairs = []

    def activate(self, config):
        self.config = config

        if not self.config.get('active', True):
            return False

        try:
            self.exe = subprocess.check_output(['which', 'apertium']).strip()

            self.language_pairs = set()

            modes_dir = os.path.join(os.path.dirname(self.exe), '..', 'share',
                                     'apertium', 'modes')

            for file_name in [os.path.basename(f) for f in
                              glob.glob(modes_dir + '/*.mode')]:

                matches = re.search('(.*?)-(.*)\.mode', file_name)

                self.language_pairs.add(matches.groups())

            self.language_pairs = list(self.language_pairs)

        except subprocess.CalledProcessError:
            self.language_pairs = []
            log.warning("apertium not available, ignoring...")
            return False

        return True

    def deactivate(self):
        pass

    def translate(self, text, from_lang, to_lang):
        try:
            proc = subprocess.Popen(['apertium',
                                     '{0}-{1}'.format(from_lang, to_lang)],
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE)
            proc.stdin.write((text + u'\n').encode('utf-8'))
            proc.stdin.close()
            output = proc.stdout.read()[:-1].decode('utf-8')

            # Check that apertium process exited successfully
            if proc.wait() != 0:
                raise TranslationException('Apertium process exited with \
non-zero status')

        except Exception as e:
            log.error('Failed to translate text {0}'.format(repr(e)))
            raise TranslationException(repr(e))

        return output
