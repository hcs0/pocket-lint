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
    ./pocketlint/formatcheck.pu
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
