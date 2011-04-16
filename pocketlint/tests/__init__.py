# Copyright (C) 2011 - Curtis Hovey <sinzui.is at verizon.net>
# This software is licensed under the MIT license (see the file COPYING).

import unittest


class TestReporter:
    """A reporter that stores the messages in a property for interogation."""

    def __init__(self):
        self.messages = []
        self.call_count = 0

    def __call__(self, line_no, message, icon=None,
                 base_dir=None, file_name=None):
        """Report a message."""
        self.call_count += 1
        self._message_console(
            line_no, message, icon=icon,
            base_dir=base_dir, file_name=file_name)

    def _message_console(self, line_no, message, icon=None,
                         base_dir=None, file_name=None):
        """Print the messages to the console."""
        self.messages.append((line_no, message))


class CheckerTestCase(unittest.TestCase):
    """A testcase with a TestReporter for checkers."""

    def setUp(self):
        self.reporter = TestReporter()
