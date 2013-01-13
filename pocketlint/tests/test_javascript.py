# Copyright (C) 2011-2013 - Curtis Hovey <sinzui.is at verizon.net>
# This software is licensed under the MIT license (see the file COPYING).

from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
    )

from tempfile import NamedTemporaryFile

from pocketlint.formatcheck import(
     JavascriptChecker,
     JS
    )
from pocketlint.tests import CheckerTestCase
from pocketlint.tests.test_text import TestAnyTextMixin


good_js = """\
var a = 1;
"""

invalid_js = """\
a = 1

"""


class TestJavascript(CheckerTestCase):
    """Verify Javascript integration."""

    def setUp(self):
        super(TestJavascript, self).setUp()
        self.file = NamedTemporaryFile(prefix='pocketlint_')

    def tearDown(self):
        self.file.close()

    def test_good_js(self):
        self.file.write(good_js)
        self.file.flush()
        checker = JavascriptChecker(self.file.name, good_js, self.reporter)
        checker.check()
        self.assertEqual([], self.reporter.messages)

    def test_invalid_value(self):
        if JS is None:
            return
        self.file.write(invalid_js)
        self.file.flush()
        checker = JavascriptChecker(self.file.name, invalid_js, self.reporter)
        checker.check()
        self.assertEqual(
            [(1, "Expected ';' and instead saw '(end)'.")],
            self.reporter.messages)


class TestText(CheckerTestCase, TestAnyTextMixin):
    """Verify text integration."""

    def create_and_check(self, file_name, text):
        """Used by the TestAnyTextMixin tests."""
        checker = JavascriptChecker(file_name, text, self.reporter)
        checker.check_text()

    def test_code_with_debugger(self):
        script = "debugger;"
        checker = JavascriptChecker('bogus', script, self.reporter)
        checker.check_text()
        self.assertEqual(
            [(1, 'Line contains a call to debugger.')],
            self.reporter.messages)
