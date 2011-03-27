# Copyright (C) 2011 - Curtis Hovey <sinzui.is at verizon.net>
# This software is licensed under the MIT license (see the file COPYING).

from pocketlint.formatcheck import(
     CSSChecker,
     HAS_CSSUTILS,
    )
from pocketlint.tests import CheckerTestCase
from pocketlint.tests.test_text import TestAnyTextMixin


good_css = """\
body {
    font-family: Ubuntu;
    }
"""

ill_formed_property = """\
body {
    font-family: Ubuntu
    color: #333;
    }
"""

invalid_value = """\
body {
    color: speckled;
    }
"""


class TestCSS(CheckerTestCase):
    """Verify CSS integration."""

    def test_good_css(self):
        checker = CSSChecker('bogus', good_css, self.reporter)
        checker.check()
        self.assertEqual([], self.reporter.messages)

    def test_ill_formed_property(self):
        if not HAS_CSSUTILS:
            return
        checker = CSSChecker('bogus', ill_formed_property, self.reporter)
        checker.check()
        messages = [
            (3, "CSSValue: No match: 'CHAR', u':'"),
            (0, 'CSSStyleDeclaration: Syntax Error in Property: '
                'font-family: Ubuntu\n    color: #333')]
        self.assertEqual(messages, self.reporter.messages)

    def test_invalid_value(self):
        if not HAS_CSSUTILS:
            return
        checker = CSSChecker('bogus', invalid_value, self.reporter)
        checker.check()
        message = (
            'Invalid value for "CSS Color Module Level 3/CSS Level 2.1" '
            'property: speckled: color')
        self.assertEqual([(2, message)], self.reporter.messages)


class TestText(CheckerTestCase, TestAnyTextMixin):
    """Verify text integration."""

    def create_and_check(self, file_name, text):
        """Used by the TestAnyTextMixin tests."""
        checker = CSSChecker(file_name, text, self.reporter)
        checker.check_text()
