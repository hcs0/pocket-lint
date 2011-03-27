# Copyright (C) 2011 - Curtis Hovey <sinzui.is at verizon.net>
# This software is licensed under the MIT license (see the file COPYING).

from pocketlint.formatcheck import AnyTextChecker
from pocketlint.tests import CheckerTestCase


class TestAnyTextMixin:
    """A mixin that provides common text tests."""

    def create_and_check(self, file_name, text):
        raise NotImplemented

    def test_without_conflicts(self):
        self.create_and_check('bogus', '<<<<<< look')
        self.assertEqual([], self.reporter.messages)

    def test_with_conflicts(self):
        self.create_and_check('bogus', '<<<<<<' + '<')
        self.assertEqual(
            [(1, 'File has conflicts.')], self.reporter.messages)

    def test_length_okay(self):
        self.create_and_check('bogus', 'short line')
        self.assertEqual([], self.reporter.messages)

    def test_long_length(self):
        long_line = '1234 56189' * 8
        self.create_and_check('bogus', long_line)
        self.assertEqual(
            [(1, 'Line exceeds 78 characters.')],
            self.reporter.messages)

    def test_no_trailing_whitespace(self):
        self.create_and_check('bogus', 'no trailing white-space')
        self.assertEqual([], self.reporter.messages)

    def test_trailing_whitespace(self):
        self.create_and_check('bogus', 'trailing white-space ')
        self.assertEqual(
            [(1, 'Line has trailing whitespace.')],
            self.reporter.messages)

    def test_without_tabs(self):
        self.create_and_check('bogus', '    without tabs')
        self.assertEqual([], self.reporter.messages)

    def test_with_tabs(self):
        self.create_and_check('bogus', '\twith tabs')
        self.assertEqual(
            [(1, 'Line contains a tab character.')],
            self.reporter.messages)


class TestText(CheckerTestCase, TestAnyTextMixin):
    """Verify text integration."""

    def create_and_check(self, file_name, text):
        checker = AnyTextChecker(file_name, text, self.reporter)
        checker.check()

    def test_with_tabs(self):
        """Text files may contain tabs.."""
        pass
