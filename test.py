#!/usr/bin/python
# Copyright (C) 2007 - Curtis Hovey <sinzui.is at verizon.net>
# This software is licensed under the GNU General Public License version 2
# (see the file COPYING).
"""test.py configuration

This is a Python source file loaded at the start of testing
Edit this file to setup the test environment. Do not alter
"if __name__ == '__main__'" unless you intend to revise the
test suite.
"""

# Add additional Python lib paths as needed.
paths = [
    './plugins/',
    '/usr/lib/gedit-2/plugins/',
     ]

# Gedit has gettext compiled into builtins.
import __builtin__
from gettext import gettext
__builtin__.__dict__['_'] = gettext

# Exclude directories that match:
dir_re = r'(sourcecode)'

# The level of detail in the output.
verbosity = 2


if __name__ == '__main__':
    params = vars()
    keys = params.keys()
    [params.pop(k) for k in keys if k.startswith('__')]
    from testing.testrunner import main
    main(params)
