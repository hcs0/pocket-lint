#!/usr/bin/python
# Copyright (C) 2007-2009 - Curtis Hovey <sinzui.is at verizon.net>
# This software is licensed under the GNU General Public License version 2
# (see the file COPYING).
"""Generate a fake implementation of Gedit for development and testing."""

import os


fakes_dir = 'gedit'
fake_defs = ('gedit', 'geditcommands', 'geditutils')

fakegen = 'fakegen.py'
fakegen_path = '../testing/%s' % fakegen

os.chdir(fakes_dir)
print "Creating fake implementation in %s." % fakes_dir
for defs in fake_defs:
    os.spawnl(os.P_WAIT, fakegen_path, fakegen, '%s.defs' % defs)
    print "Created %s." % defs
print "Rerun gen-gedit.py whenever gedit's defs or overrides are updated."
