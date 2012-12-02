# Copyright (C) 2011-2012 - Curtis Hovey <sinzui.is at verizon.net>
# This software is licensed under the MIT license (see the file COPYING).

from pocketlint.formatcheck import (
    AnyTextChecker,
    get_option_parser,
    )
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
        long_line = '1234 56189' * 9
        self.create_and_check('bogus', long_line)
        self.assertEqual(
            [(1, 'Line exceeds 80 characters.')],
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

    def create_and_check(self, file_name, text, options=None):
        checker = AnyTextChecker(
            file_name, text, self.reporter, options)
        checker.check()

    def test_with_tabs(self):
        """Text files may contain tabs.."""
        pass

    def test_long_length_options(self):
        long_line = '1234 56189' * 5
        parser = get_option_parser()
        (options, sources) = parser.parse_args(['-m', '49'])
        self.create_and_check('bogus', long_line, options=options)
        self.assertEqual(
            [(1, 'Line exceeds 49 characters.')],
            self.reporter.messages)

    def test_windows_newlines(self):
        """Files with Windows newlines are reported with errors."""
        content = '\r\nbla\r\nbla\r\n'
        checker = AnyTextChecker(
            'bogus', content, self.reporter)
        checker.check()
        self.assertEqual(
            [(0, 'File contains Windows new lines.')],
            self.reporter.messages)
        self.assertEqual(1, self.reporter.call_count)
