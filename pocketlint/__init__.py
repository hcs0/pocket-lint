# Pyflakes is not ported to Pythong 3 yet.

import os
import subprocess


PACKAGE_PATH = os.path.dirname(__file__)


class PyFlakesChecker(object):
    """A fake for py3 that can run py2 in a sub-proc."""

    def __init__(self, tree, filename='(none)'):
        script = os.path.join(PACKAGE_PATH, 'formatcheck.py')
        args = ['/usr/bin/python2', script, filename]
        linter = subprocess.Popen(
            args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        issues, errors = linter.communicate()
        issues = issues.strip()
        if issues:
            self.messages = [
                '%s:%s' % (filename, line) for line in issues.split('\n')[1:]]
        else:
            self.messages = []
