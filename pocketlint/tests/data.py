# Copyright (C) 2011 - Curtis Hovey <sinzui.is at verizon.net>
# This software is licensed under the MIT license (see the file COPYING).
"""Test data."""


good_python = """\
class example:

    def __init__(self, value):
        print "Good night."
"""


bad_syntax_python = """\
class Test():
    def __init__(self, default='', non_default):
        pass
"""

bad_indentation_python = """\
class Test:
    def __init__(self):
        a = 0
      b = 1
"""


ugly_python = """\
class Test:
    def __init__(self):
        a = b
"""

ugly_style_python = """\
class Test:

    def __init__(self):
        a =  "okay"
"""

pdb_python = "import pdb; pdb." + "set_trace()"

utf8_python = u"a = 'this is utf-8 [\u272a]'"
