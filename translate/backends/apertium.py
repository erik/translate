# -*- coding: utf-8 -*-

from translate import log
from translate.backend import IBackend

import glob
import os
import re
import subprocess


class ApertiumBackend(IBackend):
    name = "Apertium"
    description = "A free/open-source machine translation platform"
    preference = 20

    def __init__(self):
        try:
            self.exe = subprocess.check_output(['which', 'apertium']).strip()

            self.pairs = set()

            modes_dir = os.path.join(os.path.dirname(self.exe), '..', 'share',
                                     'apertium', 'modes')

            for file_name in [os.path.basename(f) for f in
                              glob.glob(modes_dir + '/*.mode')]:

                matches = re.search('(.*?)-([^_-]*).*\.mode', file_name)

                self.pairs.add(matches.groups())

            self.pairs = list(self.pairs)

        except subprocess.CalledProcessError:
            assert False
            self.preference = -1
            self.pairs = []
            log.warning("apertium not available, ignoring...")

    def translate(self, text, from_lang, to_lang):
        try:
            proc = subprocess.Popen(['apertium',
                                     '{0}-{1}'.format(from_lang, to_lang)],
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE)
            proc.stdin.write((text + u'\n').encode('utf-8'))
            proc.stdin.close()
            output = proc.stdout.read()[:-1].decode('utf-8')
        except Exception as e:
            log.error('Failed to translate text {0}'.format(repr(e)))
            output = None

        return output

    def language_pairs(self):
        return self.pairs
