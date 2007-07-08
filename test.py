#!/usr/bin/python
"""A simple doctest runner.

This test app loads testrc.py to set test environment configuration
information.
"""

import doctest
import optparse
import os
import re
import sys
import unittest
from unittest import _WritelnDecorator


class Env(object):
    """The test environment properties."""
    @classmethod
    def get(cls, key, default):
        """Return the key value when exists, or the default."""
        if key in Env.__dict__:
            return Env.__dict__[key]
        else:
            return default


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


def parse_args():
    """Parse the command line arguments and return the options."""
    parser = optparse.OptionParser(
        usage="usage: %prog [%options]")
    parser.add_option(
        "-d", "--display", dest="display", type="string",
        help="format output (t | x). Text is default.")
    parser.add_option(
        "-v", "--verbosity", dest="verbosity", default=0, action='count',
        help="The verbosity of the ouput")
    parser.add_option(
        "-t", "--test", dest="test_pattern", type="string",
        help="A regular expression pattern used to select the testst to run.")
    parser.set_defaults(
        display=Env.get('t', 't'), verbosity=Env.get('verbosity', 1),
        test_pattern='.*')
    return parser.parse_args()


def setup_env():
    """Setup the test environment.
    
    This function merges the command line args with testrc customizations
    and the default values.
    """
    Env.dir_re = re.compile(testrc.__dict__.get('dir_re', '(sourcecode)'))
    if 'paths' in testrc.__dict__:
        [sys.path.append(os.path.abspath(path)) for path in testrc.paths]
    if 'verbosity' in testrc.__dict__:
        Env.verbosity  = testrc.verbosity

    (options, args) = parse_args()
    Env.verbosity = options.verbosity
    if options.display == 'x':
        Env.write_decorator = XTermWritelnDecorator
    else:
        # text display
        Env.write_decorator = unittest._WritelnDecorator

    if len(args) >= 1:
        Env.test_pattern = args[0]
    else:
        Env.test_pattern = options.test_pattern


def find_tests(root_dir, skip_dir_re='sourcecode', test_pattern='.*'):
    """Generate a list of matching test files below a directory."""
    file_re = re.compile(r'.*(%s).*\.(txt|doctest)$' % test_pattern)
    for path, subdirs, files in os.walk(root_dir):
        subdirs[:] = [dir for dir in subdirs
                      if skip_dir_re.match(dir) is None]
        if path.endswith('tests'):
            for file in files:
                file_path = os.path.join(path, file)
                if os.path.islink(file_path):
                    continue
                if file_re.match(file_path) is not None:
                    yield os.path.join(path, file)


def project_dir():
    """The project directory for this script."""
    script_path = os.path.abspath(sys.argv[0])
    return '/'.join(script_path.split('/')[0:-1])


def main():
    """Run the specified tests or all.
    
    Uses an option command line argument that is a regulat expression to
    select a subset of tests to run.
    """
    setup_env()
    os.chdir(project_dir())
    suite = unittest.TestSuite()
    for file_path in find_tests('./' , Env.dir_re, Env.test_pattern):
        suite.addTest(doctest.DocFileTest(file_path))
    # Format the output.
    unittest._WritelnDecorator = Env.write_decorator
    unittest.TextTestRunner(verbosity=Env.verbosity).run(suite)


if __name__ == '__main__':
    # The resource configuration file should contain all
    # the project specific test information.
    try:
        import testrc
    except ImportError:
        testrc = object()
    main()
