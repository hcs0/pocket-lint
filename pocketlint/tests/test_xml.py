# Copyright (C) 2011 - Curtis Hovey <sinzui.is at verizon.net>
# This software is licensed under the MIT license (see the file COPYING).

from pocketlint.formatcheck import XMLChecker
from pocketlint.tests import CheckerTestCase
from pocketlint.tests.test_text import TestAnyTextMixin


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
