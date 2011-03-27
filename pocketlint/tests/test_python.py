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


class TestPyflakes(unittest.TestCase):
    """Verify pyflakes integration."""

    def test_code_without_issues(self):
        reporter = TestReporter()
        PythonChecker('bogus', good_python, reporter)
        self.assertEqual([], reporter.messages)
