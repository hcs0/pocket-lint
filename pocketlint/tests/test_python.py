# Copyright (C) 2011 - Curtis Hovey <sinzui.is at verizon.net>
# This software is licensed under the MIT license (see the file COPYING).

from tempfile import NamedTemporaryFile

from pocketlint.formatcheck import (
    get_option_parser,
    PythonChecker,
    )
from pocketlint.tests import CheckerTestCase
from pocketlint.tests.test_text import TestAnyTextMixin


good_python = """\
class example:

    def __init__(self, value):
        print "Good night."
"""

good_python_on_windows = """\
class example:

    def __init__(self, value):
        try:
            open("some.file")
        except WindowsError:
            pass
"""

bad_syntax_python = """\
class Test():
    def __init__(self, default='', non_default):
        pass
"""

bad_syntax2_python = """\
class Test(
    def __init__(self, val):
        pass
"""

bad_indentation_python = """\
class Test:
    def __init__(self):
        a = 0
      b = 1
"""

ugly_python = """\
class Test:
    def __init__(self):
        a = b
"""

ugly_style_python = """\
class Test:

    def __init__(self):
        a =  "okay"
"""


ugly_style_lines_python = """\
a = 1
# Post comment.


# Pre comment.
class Test:

    # Pre comment.
    def __init__(self):
        # Inter comment.
        self.a = "okay"
"""


class TestPyflakes(CheckerTestCase):
    """Verify pyflakes integration."""

    def test_contrib_integration(self):
        from pocketlint.contrib.pyflakes.checker import messages
        self.assertTrue('pocketlint/contrib/' in messages.__file__)

    def test_code_without_issues(self):
        self.reporter.call_count = 0
        checker = PythonChecker('bogus', good_python, self.reporter)
        checker.check_flakes()
        self.assertEqual([], self.reporter.messages)
        self.assertEqual(0, self.reporter.call_count)

    def test_windows_code_without_issues(self):
        self.reporter.call_count = 0
        checker = PythonChecker(
            'bogus', good_python_on_windows, self.reporter)
        checker.check_flakes()
        self.assertEqual([], self.reporter.messages)
        self.assertEqual(0, self.reporter.call_count)

    def test_code_with_SyntaxError(self):
        self.reporter.call_count = 0
        checker = PythonChecker(
            'bogus', bad_syntax_python, self.reporter)
        checker.check_flakes()
        expected = [(
            2, 'Could not compile; non-default argument follows '
               'default argument: ')]
        self.assertEqual(expected, self.reporter.messages)
        self.assertEqual(1, self.reporter.call_count)

    def test_code_with_very_bad_SyntaxError(self):
        checker = PythonChecker(
            'bogus', bad_syntax2_python, self.reporter)
        checker.check_flakes()
        expected = [(
            2, 'Could not compile; invalid syntax: def __init__(self, val):')]
        self.assertEqual(expected, self.reporter.messages)

    def test_code_with_IndentationError(self):
        checker = PythonChecker(
            'bogus', bad_indentation_python, self.reporter)
        checker.check_flakes()
        expected = [
            (4, 'Could not compile; unindent does not match any '
                'outer indentation level: b = 1')]
        self.assertEqual(expected, self.reporter.messages)

    def test_code_with_warnings(self):
        self.reporter.call_count = 0
        checker = PythonChecker('bogus', ugly_python, self.reporter)
        checker.check_flakes()
        self.assertEqual(
            [(3, "undefined name 'b'"),
            (3, "local variable 'a' is assigned to but never used")],
            self.reporter.messages)
        self.assertEqual(2, self.reporter.call_count)


class TestPEP8(CheckerTestCase):
    """Verify PEP8 integration."""

    def setUp(self):
        super(TestPEP8, self).setUp()
        self.file = NamedTemporaryFile(prefix='pocketlint_')

    def tearDown(self):
        self.file.close()

    def test_code_without_issues(self):
        self.file.write(good_python)
        self.file.flush()
        checker = PythonChecker(
            self.file.name, good_python, self.reporter)
        checker.check_pep8()
        self.assertEqual([], self.reporter.messages)

    def test_bad_syntax(self):
        self.file.write(bad_syntax2_python)
        self.file.flush()
        checker = PythonChecker(
            self.file.name, ugly_style_python, self.reporter)
        checker.check_pep8()
        self.assertEqual(
            [(4, 'EOF in multi-line statement')],
            self.reporter.messages)

    def test_code_with_IndentationError(self):
        self.file.write(bad_indentation_python)
        self.file.flush()
        checker = PythonChecker(
            self.file.name, bad_indentation_python, self.reporter)
        checker.check_pep8()
        expected = [(
            4, 'unindent does not match any outer indentation level: b = 1')]
        self.assertEqual(expected, self.reporter.messages)

    def test_code_with_issues(self):
        self.file.write(ugly_style_python)
        self.file.flush()
        checker = PythonChecker(
            self.file.name, ugly_style_python, self.reporter)
        checker.check_pep8()
        self.assertEqual(
            [(4, 'E222 multiple spaces after operator')],
            self.reporter.messages)

    def test_code_with_comments(self):
        self.file.write(ugly_style_lines_python)
        self.file.flush()
        checker = PythonChecker(
            self.file.name, ugly_style_lines_python, self.reporter)
        checker.check_pep8()
        self.assertEqual([], self.reporter.messages)

    def test_long_length_good(self):
        long_line = '1234 56189' * 7 + '12345678' + '\n'
        self.file.write(long_line)
        self.file.flush()
        checker = PythonChecker(self.file.name, long_line, self.reporter)
        checker.check_pep8()
        self.assertEqual([], self.reporter.messages)

    def test_long_length_bad(self):
        long_line = '1234 56189' * 8 + '\n'
        self.file.write(long_line)
        self.file.flush()
        checker = PythonChecker(self.file.name, long_line, self.reporter)
        checker.check_pep8()
        self.assertEqual(
            [(1, 'E501 line too long (80 characters)')],
            self.reporter.messages)

    def test_long_length_options(self):
        long_line = '1234 56189' * 7 + '\n'
        parser = get_option_parser()
        (options, sources) = parser.parse_args(['-m', '60'])
        self.file.write(long_line)
        self.file.flush()
        checker = PythonChecker(
            self.file.name, long_line, self.reporter, options)
        checker.check_pep8()
        self.assertEqual(
            [(1, 'E501 line too long (70 characters)')],
            self.reporter.messages)


class TestText(CheckerTestCase, TestAnyTextMixin):
    """Verify text integration."""

    def test_with_tabs(self):
        # pep8 checks this.
        pass

    def test_trailing_whitespace(self):
        # pep8 checks this.
        pass

    def test_long_length(self):
        # pep8 checks this.
        pass

    def create_and_check(self, file_name, text):
        """Used by the TestAnyTextMixin tests."""
        checker = PythonChecker(file_name, text, self.reporter)
        checker.check_text()

    def test_code_without_issues(self):
        checker = PythonChecker('bogus', good_python, self.reporter)
        checker.check_text()
        self.assertEqual([], self.reporter.messages)

    def test_code_with_pdb(self):
        pdb_python = "import pdb; pdb." + "set_trace()"
        checker = PythonChecker('bogus', pdb_python, self.reporter)
        checker.check_text()
        self.assertEqual(
            [(1, 'Line contains a call to pdb.')], self.reporter.messages)

    def _test_encoding(self, python, expected_encoding='foo-encoding'):
        checker = PythonChecker(
           'bogus', python % dict(encoding=expected_encoding), self.reporter)
        checker.check_text()
        self.assertEqual(expected_encoding, checker.encoding)

    def test_pep0263_no_encoding(self):
        self._test_encoding("# First line\n# Second line\n\n", 'ascii')

    def test_pep0263_encoding_standard_coding(self):
        self._test_encoding("# coding=%(encoding)s\n")

    def test_pep0263_encoding_standard_encoding(self):
        self._test_encoding("# encoding=%(encoding)s\n")

    def test_pep0263_encoding_emacs(self):
        self._test_encoding("# -*- coding: %(encoding)s -*-\n")

    def test_pep0263_encoding_vim(self):
        self._test_encoding("# vim: set fileencoding=%(encoding)s :\n")

    def test_pep0263_encoding_2nd_line(self):
        self._test_encoding("# First line\n# coding=%(encoding)s\n\n")

    def test_code_utf8(self):
        utf8_python = u"a = 'this is utf-8 [\u272a]'"
        checker = PythonChecker('bogus', utf8_python, self.reporter)
        checker.encoding = 'utf-8'
        checker.check_text()

    def test_code_ascii_is_not_utf8(self):
        utf8_python = u"a = 'this is utf-8 [\u272a]'"
        checker = PythonChecker('bogus', utf8_python, self.reporter)
        checker.check_text()
        self.assertEqual(
            [(1, 'Non-ascii characer at position 21.')],
            self.reporter.messages)
