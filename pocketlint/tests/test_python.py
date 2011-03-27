# Copyright (C) 2009-2010 - Curtis Hovey <sinzui.is at verizon.net>
# This software is licensed under the MIT license (see the file COPYING).

import unittest
from pocketlint.formatcheck import PythonChecker


class TestReporter:
    """A reporter that stores the messages in a property for interogation."""

    def __init__(self):
        self.messages = []

    def __call__(self, line_no, message, icon=None,
                 base_dir=None, file_name=None):
        """Report a message."""
        self._message_console(
            line_no, message, icon=icon,
            base_dir=base_dir, file_name=file_name)

    def _message_console(self, line_no, message, icon=None,
                         base_dir=None, file_name=None):
        """Print the messages to the console."""
        self.messages.append((line_no, message))


good_python = """
class example:
    def __init__(self, value):
        print "Good night."
"""


bad_python = """
class Test():
    def __init__(self, default='', non_default):
        pass
"""

bad_indentation_python = """
class Test:
    def __init__(self):
        a = 0
      b = 1
"""



class TestPyflakes(unittest.TestCase):
    """Verify pyflakes integration."""

    def test_code_without_issues(self):
        reporter = TestReporter()
        checker = PythonChecker('bogus', good_python, reporter)
        checker.check_flakes()
        self.assertEqual([], reporter.messages)

    def test_code_with_syntax_issues(self):
        reporter = TestReporter()
        checker = PythonChecker('bogus', bad_python, reporter)
        checker.check_flakes()
        expected = [(
            0, 'Could not compile; non-default argument follows '
               'default argument: ')]
        self.assertEqual(expected, reporter.messages)

    def test_code_with_indentation_issues(self):
        reporter = TestReporter()
        checker = PythonChecker('bogus', bad_indentation_python, reporter)
        checker.check_flakes()
        expected = [
            (5, 'Could not compile; unindent does not match any '
                'outer indentation level: b = 1')]
        self.assertEqual(expected, reporter.messages)
