#!/usr/bin/python
# Copyright (C) 2011-2013 - Curtis Hovey <sinzui.is at verizon.net>
# This software is licensed under the MIT license (see the file COPYING).

from __future__ import (
    absolute_import,
    print_function,
)

import re
import os
import sys
import unittest
try:
    from unittest.runner import _WritelnDecorator
    _WritelnDecorator != '# Supress redefintion warning.'
except ImportError:
    # Hack support for running the tests in Python 2.6-.
    from unittest import _WritelnDecorator

    class FakeRunner:

        def __init__(self, writelin_decorator):
            self._WritelnDecorator = writelin_decorator

    unittest.runner = FakeRunner(_WritelnDecorator)


class TPut(object):
    """Terminal colours (tput) utility."""
    _colours = [
        'black', 'blue', 'green', 'white', 'red', 'magenta', 'yellow', 'grey']

    def __init__(self):
        try:
            self.bold = os.popen('tput bold').read()
            self.reset = os.popen('tput sgr0').read()
            for i in range(8):
                cmd = 'tput setf %d' % i
                colour = self._colours[i]
                self.__dict__[colour] = os.popen(cmd).read()
                self.__dict__['bold' + colour] = (
                    self.bold + self.__dict__[colour])
        except IOError:
            # The default values of the styles are safe for all streams.
            self.bold = ''
            self.reset = ''
            for i in range(8):
                colour = self._colours[i]
                self.__dict__[colour] = ''
                self.__dict__['bold' + colour] = ''


class XTermWritelnDecorator(_WritelnDecorator):
    """Decorate lines with xterm bold and colors."""
    _test_terms = re.compile(r'^(File|Failed|Expected|Got)(.*)$', re.M)
    _test_rule = re.compile(r'^(--[-]+)$', re.M)

    def __init__(self, stream):
        """Initialize the stream and setup colors."""
        _WritelnDecorator.__init__(self, stream)
        self.tput = TPut()

    def write(self, arg):
        """Write bolded and coloured lines."""
        if arg.startswith('Doctest:'):
            text = '%s%s%s' % (self.tput.blue, arg, self.tput.reset)
        elif arg.startswith('Ran'):
            text = '%s%s%s' % (self.tput.bold, arg, self.tput.reset)
        elif arg.startswith('ERROR') or arg.startswith('FAIL:'):
            text = '%s%s%s' % (self.tput.boldred, arg, self.tput.reset)
        elif arg.endswith('FAIL'):
            text = '%s%s%s' % (self.tput.red, arg, self.tput.reset)
        elif arg.startswith('ok'):
            text = '%s%s%s' % (self.tput.blue, arg, self.tput.reset)
        elif arg.startswith('--') or arg.startswith('=='):
            text = '%s%s%s' % (self.tput.grey, arg, self.tput.reset)
        elif arg.startswith('Traceback'):
            term = r'%s\1\2%s' % (self.tput.red, self.tput.reset)
            text = self._test_terms.sub(term, arg)
            rule = r'%s\1%s' % (self.tput.grey, self.tput.reset)
            text = self._test_rule.sub(rule, text)
        else:
            text = arg
        self.stream.write(text)


def show_help():
    print('''\
python test.py [-h|--help] [test_module_regex_filter]
''')


def main():
    if len(sys.argv) > 1:
        if (sys.argv[1] in ['-h', '--help']):
            show_help()
            return
        else:
            pattern = sys.argv[1]
    else:
        pattern = 'test*.py'

    unittest.runner._WritelnDecorator = XTermWritelnDecorator
    test_loader = unittest.defaultTestLoader
    suite = unittest.TestSuite()
    for test_module in test_loader.discover('pocketlint', pattern=pattern):
        suite.addTest(test_module)
    unittest.TextTestRunner(verbosity=1).run(suite)


if __name__ == '__main__':
    main()
