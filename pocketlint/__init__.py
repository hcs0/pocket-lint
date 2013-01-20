# Pyflakes is not ported to Pythong 3 yet.

__all__ = [
    'PyFlakesChecker',
    'u',
    ]

import os
import subprocess
import sys


PACKAGE_PATH = os.path.dirname(__file__)


if int(sys.version[0]) < 3:
    import codecs

    def u(string):
        try:
            # This is a sanity check to work with the true text...
            text = string.decode('utf-8').encode('utf-8')
        except UnicodeDecodeError:
            # ...but this fallback is okay since this comtemt.
            text = string.decode('ascii', 'ignore').encode('utf-8')
        return codecs.unicode_escape_decode(text)[0]
else:
    def u(string):  # pyflakes:ignore
        if isinstance(string, str):
            return string
        else:
            return str(string.decode('utf-8'))


class PyFlakesChecker(object):
    """A fake for py3 that can run py2 in a sub-proc."""

    def __init__(self, tree, filename='(none)'):
        self.messages = []
        script = os.path.join(PACKAGE_PATH, 'formatcheck.py')
        command = ['python2', script, filename]
        linter = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        issues, errors = linter.communicate()
        issues = issues.decode('ascii').strip()
        if issues:
            for line in issues.split('\n')[1:]:
                line_no, message = line.split(':')
                self.messages.append(
                    '%s:%s:%s' % (filename, line_no.strip(), message.strip()))
