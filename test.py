#!/usr/bin/python
"""A simple doctest runner.

This test app loads testrc.py to set test environment configuration
information.
"""

import doctest
import os
import re
import sys
import unittest


class Env(object):
    """The test environment properties."""


def setup_env():
    """Setup the test environment."""
    if testrc.paths:
        [sys.path.append(os.path.abspath(path)) for path in testrc.paths]
    if testrc.dir_re:
        Env.dir_re = re.compile(testrc.dir_re)
    if testrc.file_re:
        Env.file_re = re.compile(testrc.file_re)


def find_files(root_dir, skip_dir_pattern, file_re):
    """Generate a list of matching files below a directory."""
    for path, subdirs, files in os.walk(root_dir):
        subdirs[:] = [dir for dir in subdirs
                      if skip_dir_pattern.match(dir) is None]
        for file in files:
            file_path = os.path.join(path, file)
            if os.path.islink(file_path):
                continue
            if file_re.match(file) is not None:
                yield os.path.join(path, file)


def project_dir():
    """The project directory for this script."""
    script_path = os.path.abspath(sys.argv[0])
    return '/'.join(script_path.split('/')[0:-2])


def main():
    """Run the specified tests or all.
    
    Uses an option command line argument that is a regulat expression to
    select a subset of tests to run.
    """
    os.chdir(project_dir())
    like = ''
    if len(sys.argv) > 1:
        like = sys.argv[1]
    Env.file_re = re.compile(r'.*(%s).*\.doctest' % like)
    for file_path in find_files('./' , Env.dir_re, Env.file_re):
        sys.stdout.write('Testing %s:\n' % file_path)
        sys.stdout.flush()
        suite = doctest.DocFileSuite(file_path)
        unittest.TextTestRunner().run(suite)


if __name__ == '__main__':
    # The resource configuration file should contain all
    # the project specific test information.
    try:
        import testrc
    except ImportError:
        print "Create testrc.py to configure the test environment."
        Env.dir_re = re.compile('(sourcecode)')
        Env.file_re = re.compile('.*(pyc$)')
    else:
        setup_env()

    main()
