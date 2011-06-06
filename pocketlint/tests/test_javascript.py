# Copyright (C) 2011 - Curtis Hovey <sinzui.is at verizon.net>
# This software is licensed under the MIT license (see the file COPYING).

from pocketlint.formatcheck import(
     JavascriptChecker,
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

    def test_good_js(self):
        checker = JavascriptChecker('bogus', good_js, self.reporter)
        checker.check()
        self.assertEqual([], self.reporter.messages)

    def test_invalid_value(self):
        checker = JavascriptChecker('bogus', invalid_js, self.reporter)
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
