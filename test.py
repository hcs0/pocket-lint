#!/usr/bin/python
# Copyright (C) 2007 - Curtis Hovey <sinzui.is at verizon.net>
"""test.py configuration

This is a Python source file loaded at the start of testing
Edit this file to setup the test environment. Do not alter
"if __name__ == '__main__'" unless you intend to revise the
test suite.
"""

# Add additional Python lib paths as needed.
paths = ['/usr/lib/gedit-2/plugins/',
         './plugins/']

# Exclude directories that match:
dir_re = r'(sourcecode)'

# The level of detail in the output.
verbosity = 2


if __name__ == '__main__':
    params = vars()
    keys = params.keys()
    [params.pop(k) for k in keys if k.startswith('__')]
    from utils.testrunner import main
    main(params)
