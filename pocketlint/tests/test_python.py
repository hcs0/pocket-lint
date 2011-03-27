# Copyright (C) 2011 - Curtis Hovey <sinzui.is at verizon.net>
# This software is licensed under the MIT license (see the file COPYING).

from tempfile import NamedTemporaryFile

from pocketlint.formatcheck import PythonChecker
from pocketlint.tests import (
    CheckerTestCase,
    data,
    )


class TestPyflakes(CheckerTestCase):
    """Verify pyflakes integration."""

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
            (4, 'Could not compile; unindent does not match any '
                'outer indentation level: b = 1')]
        self.assertEqual(expected, self.reporter.messages)

    def test_code_with_warnings(self):
        checker = PythonChecker('bogus', data.ugly_python, self.reporter)
        checker.check_flakes()
        self.assertEqual(
            [(3, "undefined name 'b'")], self.reporter.messages)


class TestPEP8(CheckerTestCase):
    """Verify PEP8 integration."""

    def setUp(self):
        super(TestPEP8, self).setUp()
        self.file = NamedTemporaryFile(prefix='pocketlint_')

    def tearDown(self):
        self.file.close()

    def test_code_without_issues(self):
        self.file.write(data.good_python)
        self.file.flush()
        checker = PythonChecker(
            self.file.name, data.good_python, self.reporter)
        checker.check_pep8()
        self.assertEqual([], self.reporter.messages)

    def test_code_with_issues(self):
        self.file.write(data.ugly_style_python)
        self.file.flush()
        checker = PythonChecker(
            self.file.name, data.ugly_style_python, self.reporter)
        checker.check_pep8()
        self.assertEqual(
            [(4, 'E222 multiple spaces after operator')],
            self.reporter.messages)


class TestText(CheckerTestCase):
    """Verify text integration."""

    def test_code_without_issues(self):
        checker = PythonChecker('bogus', data.good_python, self.reporter)
        checker.check_text()
        self.assertEqual([], self.reporter.messages)

    def test_code_with_pdb(self):
        checker = PythonChecker('bogus', data.pdb_python, self.reporter)
        checker.check_text()
        self.assertEqual(
            [(1, 'Line contains a call to pdb.')], self.reporter.messages)

    def test_code_is_utf8(self):
        checker = PythonChecker('bogus', data.utf8_python, self.reporter)
        checker.is_utf8 = True
        checker.check_text()

    def test_code_ascii_is_not_is_utf8(self):
        checker = PythonChecker('bogus', data.utf8_python, self.reporter)
        checker.check_text()
        self.assertEqual(
            [(1, 'Non-ascii characer at position 21.')],
            self.reporter.messages)
