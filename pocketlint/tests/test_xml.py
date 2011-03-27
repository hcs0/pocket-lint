# Copyright (C) 2011 - Curtis Hovey <sinzui.is at verizon.net>
# This software is licensed under the MIT license (see the file COPYING).

from pocketlint.formatcheck import XMLChecker
from pocketlint.tests import CheckerTestCase
from pocketlint.tests.test_text import TestAnyTextMixin


good_markup = """\
<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<root>
  <child>hello world</child>
</root>
"""

missing_dtd_and_xml = """\
<root>
  <child>hello&nbsp;world</child>
</root>
"""

ill_formed_markup = """\
<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<root>
  <child>hello world<
</root>
"""


class TestXML(CheckerTestCase):
    """Verify XML integration."""

    def test_good_markup(self):
        checker = XMLChecker('bogus', good_markup, self.reporter)
        checker.check()
        self.assertEqual([], self.reporter.messages)

    def test_missing_dtd_and_xml(self):
        checker = XMLChecker('bogus', missing_dtd_and_xml, self.reporter)
        checker.check()
        self.assertEqual([], self.reporter.messages)

    def test_ill_formed_markup(self):
        checker = XMLChecker('bogus', ill_formed_markup, self.reporter)
        checker.check()
        self.assertEqual(
            [(6, 'not well-formed (invalid token)')], self.reporter.messages)


class TestText(CheckerTestCase, TestAnyTextMixin):
    """Verify text integration."""

    def create_and_check(self, file_name, text):
        """Used by the TestAnyTextMixin tests."""
        checker = XMLChecker(file_name, text, self.reporter)
        checker.check_text()

    def test_long_length(self):
        pass

    def test_with_tabs(self):
        pass
