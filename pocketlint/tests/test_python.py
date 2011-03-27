# Copyright (C) 2011 - Curtis Hovey <sinzui.is at verizon.net>
# This software is licensed under the MIT license (see the file COPYING).

import unittest
from pocketlint.formatcheck import PythonChecker
from pocketlint.tests import (
    data,
    TestReporter,
    )


class TestPyflakes(unittest.TestCase):
    """Verify pyflakes integration."""

    def setUp(self):
        self.reporter = TestReporter()

    def test_code_without_issues(self):
        checker = PythonChecker('bogus', data.good_python, self.reporter)
        checker.check_flakes()
        self.assertEqual([], self.reporter.messages)

    def test_code_with_SyntaxError(self):
        checker = PythonChecker(
            'bogus', data.bad_syntax_python, self.reporter)
        checker.check_flakes()
        expected = [(
            0, 'Could not compile; non-default argument follows '
               'default argument: ')]
        self.assertEqual(expected, self.reporter.messages)

    def test_code_with_IndentationError(self):
        checker = PythonChecker(
            'bogus', data.bad_indentation_python, self.reporter)
        checker.check_flakes()
        expected = [
            (5, 'Could not compile; unindent does not match any '
                'outer indentation level: b = 1')]
        self.assertEqual(expected, self.reporter.messages)

    def test_code_with_warnings(self):
        checker = PythonChecker('bogus', data.ugly_python, self.reporter)
        checker.check_flakes()
        expected = [(4, "undefined name 'b'")]
        self.assertEqual(expected, self.reporter.messages)
