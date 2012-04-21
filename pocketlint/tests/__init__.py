# Copyright (C) 2011-2012 - Curtis Hovey <sinzui.is at verizon.net>
# This software is licensed under the MIT license (see the file COPYING).

import unittest

from pocketlint.formatcheck import Reporter


class CheckerTestCase(unittest.TestCase):
    """A testcase with a TestReporter for checkers."""

    def setUp(self):
        self.reporter = Reporter(Reporter.COLLECTOR)
        self.reporter.call_count = 0
