# Copyright (C) 2012 - Curtis Hovey <sinzui.is at verizon.net>
# This software is licensed under the MIT license (see the file COPYING).

from tempfile import NamedTemporaryFile

from pocketlint.formatdoctest import DoctestReviewer
from pocketlint.tests import CheckerTestCase


good_doctest = """\
Example doctest
==============

You can work with file paths using os.path

    >>> import os.path
    >>> os.path.join('.', 'pocketlint', 'formatcheck.py')
    ./pocketlint/formatcheck.py
"""

malformed_doctest = """\
You can work with file paths using os.path
    >>> import os.path
    >>> os.path.join('.', 'pocketlint', 'formatcheck.py')
Narrative without WANT section.
"""


class TestDoctest(CheckerTestCase):
    """Verify doctest checking."""

    def setUp(self):
        super(TestDoctest, self).setUp()
        self.file = NamedTemporaryFile(prefix='pocketlint_')

    def tearDown(self):
        self.file.close()

    def test_doctest_without_issues(self):
        self.file.write(good_doctest)
        self.file.flush()
        checker = DoctestReviewer(
            good_doctest, self.file.name, self.reporter)
        checker.check()
        self.assertEqual([], self.reporter.messages)

    def test_doctest_malformed_doctest(self):
        self.file.write(malformed_doctest)
        self.file.flush()
        checker = DoctestReviewer(
            malformed_doctest, self.file.name, self.reporter)
        checker.check()
        expected = (
            "line 4 of the docstring for %s has inconsistent leading "
            "whitespace: 'Narrative without WANT section.'" % self.file.name)
        self.assertEqual(
            [(0, expected)], self.reporter.messages)

    def test_doctest_with_globs(self):
        # Doctest runners often setup global identifiers that are not python
        # execution issues
        doctest = "    >>> ping('text')\n    pong text"
        self.file.write(doctest)
        self.file.flush()
        checker = DoctestReviewer(
            doctest, self.file.name, self.reporter)
        checker.check()
        self.assertEqual([], self.reporter.messages)

    def test_doctest_with_python_compilation_error(self):
        doctest = "    >>> if (True\n    pong text"
        self.file.write(doctest)
        self.file.flush()
        checker = DoctestReviewer(
            doctest, self.file.name, self.reporter)
        checker.check()
        self.assertEqual(
            [(1, 'Could not compile:\n          if (True')],
            self.reporter.messages)

    def test_moin_header(self):
        doctest = "= Heading =\n\nnarrative"
        self.file.write(doctest)
        self.file.flush()
        checker = DoctestReviewer(
            doctest, self.file.name, self.reporter)
        checker.check()
        self.assertEqual(
            [(1, 'narrative uses a moin header.')],
            self.reporter.messages)

    def test_bad_indentation(self):
        doctest = "narrative\n>>> print 'done'\n"
        self.file.write(doctest)
        self.file.flush()
        checker = DoctestReviewer(
            doctest, self.file.name, self.reporter)
        checker.check()
        self.assertEqual(
            [(2, 'source has bad indentation.')],
            self.reporter.messages)

    def test_fix_bad_indentation(self):
        doctest = "narrative\n>>> print 'done'\n"
        self.file.write(doctest)
        self.file.flush()
        checker = DoctestReviewer(
            doctest, self.file.name, self.reporter)
        text = checker.format()
        self.assertEqual(
            "narrative\n\n    >>> print 'done'\n\n", text)

    def test_trailing_whitespace(self):
        doctest = "narrative  \n    >>> print 'done'\n"
        self.file.write(doctest)
        self.file.flush()
        checker = DoctestReviewer(
            doctest, self.file.name, self.reporter)
        checker.check()
        self.assertEqual(
            [(1, 'narrative has trailing whitespace.')],
            self.reporter.messages)

    def test_fix_trailing_whitespace(self):
        doctest = "narrative  \n    >>> print 'done' \n"
        self.file.write(doctest)
        self.file.flush()
        checker = DoctestReviewer(
            doctest, self.file.name, self.reporter)
        text = checker.format()
        self.assertEqual("narrative\n\n    >>> print 'done'\n\n", text)

    def test_long_line(self):
        doctest = (
            "narrative is a line that exceeds 78 characters which causes "
            "scrolling in consoles and wraps poorly in email\n")
        self.file.write(doctest)
        self.file.flush()
        checker = DoctestReviewer(
            doctest, self.file.name, self.reporter)
        checker.check()
        self.assertEqual(
            [(1, 'narrative exceeds 78 characters.')],
            self.reporter.messages)

    def test_fix_long_line(self):
        doctest = (
            "narrative is a line that exceeds 78 characters which causes "
            "scrolling in consoles and wraps poorly in email\n")
        self.file.write(doctest)
        self.file.flush()
        checker = DoctestReviewer(
            doctest, self.file.name, self.reporter)
        text = checker.format()
        expected = (
            "narrative is a line that exceeds 78 characters which causes "
            "scrolling in\nconsoles and wraps poorly in email")
        self.assertEqual(expected, text)
