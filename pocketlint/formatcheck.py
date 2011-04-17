#!/usr/bin/python
# Copyright (C) 2009-2011 - Curtis Hovey <sinzui.is at verizon.net>
# This software is licensed under the MIT license (see the file COPYING).
"""Check for syntax and style problems."""

from __future__ import with_statement

__metaclass__ = type

import compiler
import htmlentitydefs
import logging
import mimetypes
import os
import re
import subprocess
import sys

from optparse import OptionParser
from StringIO import StringIO
from tokenize import TokenError
from xml.etree import ElementTree
try:
    from xml.etree.ElementTree import ParseError
    ParseError != '# Supress redefintion warning.'
except ImportError:
    # Python 2.6 and below.
    ParseError = object()
from xml.parsers.expat import ErrorString, ExpatError

from formatdoctest import DoctestReviewer

import contrib.pep8 as pep8
from contrib.pyflakes.checker import Checker
try:
    import cssutils
    HAS_CSSUTILS = True
except ImportError:
    HAS_CSSUTILS = False

# Javascript checking is available if spider money's js is available.
js = subprocess.Popen(
    ['which', 'js'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
js_exec, ignore = js.communicate()
if js.returncode != 0:
    JS = None
else:
    JS = js_exec.strip()

__all__ = [
    'Reporter',
    'UniversalChecker',
    ]


class Reporter:
    """Common rules for checkers."""
    CONSOLE = object()
    FILE_LINES = object()

    def __init__(self, report_type, treeview=None):
        self.report_type = report_type
        self.file_lines_view = treeview
        if self.file_lines_view is not None:
            self.treestore = self.file_lines_view.get_model()
        self.piter = None
        self._last_file_name = None

    def __call__(self, line_no, message, icon=None,
                 base_dir=None, file_name=None):
        """Report a message."""
        if self.report_type == self.FILE_LINES:
            self._message_file_lines(
                line_no, message, icon=icon,
                base_dir=base_dir, file_name=file_name)
        else:
            self._message_console(
                line_no, message, icon=icon,
                base_dir=base_dir, file_name=file_name)

    def _message_console(self, line_no, message, icon=None,
                         base_dir=None, file_name=None):
        """Print the messages to the console."""
        self._message_console_group(base_dir, file_name)
        print '    %4s: %s' % (line_no, message)

    def _message_console_group(self, base_dir, file_name):
        """Print the file name is it has not been seen yet."""
        source = (base_dir, file_name)
        if file_name is not None and source != self._last_file_name:
            self._last_file_name = source
            print '%s' % os.path.join('./', base_dir, file_name)

    def _message_file_lines(self, line_no, message, icon=None,
                            base_dir=None, file_name=None):
        """Display the messages in the file_lines_view."""
        if self.piter is None:
            mime_type = 'gnome-mime-text'
            self.piter = self.treestore.append(
                None, (file_name, mime_type, 0, None, base_dir))
        self.treestore.append(
            self.piter, (file_name, icon, line_no, message, base_dir))


class Language:
    """Supported Language types."""
    TEXT = object()
    PYTHON = object()
    DOCTEST = object()
    CSS = object()
    JAVASCRIPT = object()
    SH = object()
    XML = object()
    XSLT = object()
    HTML = object()
    ZPT = object()
    ZCML = object()
    DOCBOOK = object()
    LOG = object()
    SQL = object()

    XML_LIKE = (XML, XSLT, HTML, ZPT, ZCML, DOCBOOK)

    mimetypes.add_type('application/x-zope-configuation', '.zcml')
    mimetypes.add_type('application/x-zope-page-template', '.pt')
    mimetypes.add_type('text/x-python-doctest', '.doctest')
    mimetypes.add_type('text/x-log', '.log')
    mime_type_language = {
        'text/x-python': PYTHON,
        'text/x-python-doctest': DOCTEST,
        'text/css': CSS,
        'text/html': HTML,
        'text/plain': TEXT,
        'text/x-sql': SQL,
        'text/x-log': LOG,
        'application/javascript': JAVASCRIPT,
        'application/xml': XML,
        'application/x-sh': SH,
        'application/x-zope-configuation': ZCML,
        'application/x-zope-page-template': ZPT,
        }
    doctest_pattern = re.compile(
        r'^.*(doc|test|stories).*/.*\.(txt|doctest)$')

    @staticmethod
    def get_language(file_path):
        """Return the language for the source."""
        # Doctests can easilly be mistyped, so it must be checked first.
        if Language.doctest_pattern.match(file_path):
            return Language.DOCTEST
        mime_type, encoding = mimetypes.guess_type(file_path)
        if mime_type is None:
            # This could be a very bad guess.
            return Language.TEXT
        elif mime_type in Language.mime_type_language:
            return Language.mime_type_language[mime_type]
        elif mime_type in Language.XML_LIKE:
            return Language.XML
        elif mime_type.endswith('+xml'):
            return Language.XML
        elif 'text/' in mime_type:
            return Language.TEXT
        else:
            return None

    @staticmethod
    def is_editable(file_path):
        """ Only search mime-types that are like sources can open.

        A fuzzy match of text/ or +xml is good, but some files types are
        unknown or described as application data.
        """
        return Language.get_language(file_path) is not None


class BaseChecker:
    """Common rules for checkers.

    The Decedent must provide self.file_name and self.base_dir
    """

    def __init__(self, file_path, text, reporter=None):
        self.file_path = file_path
        self.base_dir = os.path.dirname(file_path)
        self.file_name = os.path.basename(file_path)
        self.text = text
        self.set_reporter(reporter=reporter)

    def set_reporter(self, reporter=None):
        """Set the reporter for messages."""
        if reporter is None:
            reporter = Reporter(Reporter.CONSOLE)
        self._reporter = reporter

    def message(self, line_no, message, icon=None,
                base_dir=None, file_name=None):
        """Report the message."""
        if base_dir is None:
            base_dir = self.base_dir
        if file_name is None:
            file_name = self.file_name
        self._reporter(
            line_no, message, icon=icon,
            base_dir=base_dir, file_name=file_name)

    def check(self):
        """Check the content."""
        raise NotImplementedError


class UniversalChecker(BaseChecker):
    """Check and reformat doctests."""

    def __init__(self, file_path, text=None, language=None, reporter=None):
        self.file_path = file_path
        self.base_dir = os.path.dirname(file_path)
        self.file_name = os.path.basename(file_path)
        self.text = text
        self.set_reporter(reporter=reporter)
        self.language = language
        self.file_lines_view = None

    def check(self):
        """Check the file syntax and style."""
        if self.language is Language.PYTHON:
            PythonChecker(self.file_path, self.text, self._reporter).check()
        elif self.language is Language.DOCTEST:
            DoctestReviewer(self.text, self.file_path, self._reporter).check()
        elif self.language is Language.CSS:
            CSSChecker(self.file_path, self.text, self._reporter).check()
        elif self.language in Language.XML_LIKE:
            XMLChecker(self.file_path, self.text, self._reporter).check()
        elif self.language is Language.JAVASCRIPT:
            JavascriptChecker(
                self.file_path, self.text, self._reporter).check()
        elif self.language is Language.LOG:
            # Log files are not source, but they are often in source code
            # trees.
            pass
        else:
            AnyTextChecker(self.file_path, self.text, self._reporter).check()


class AnyTextMixin:
    """Common checks for many checkers."""

    def check_conflicts(self, line_no, line):
        """Check that there are no merge conflict markers."""
        if line.startswith('<' * 7) or line.startswith('>' * 7):
            self.message(line_no, 'File has conflicts.', icon='errror')

    def check_length(self, line_no, line):
        """Check the length of the line."""
        if len(line) > 78:
            self.message(
                line_no, 'Line exceeds 78 characters.', icon='info')

    def check_trailing_whitespace(self, line_no, line):
        """Check for the presence of trailing whitespace in the line."""
        if line.endswith(' '):
            self.message(
                line_no, 'Line has trailing whitespace.', icon='info')

    def check_tab(self, line_no, line):
        """Check for the presence of tabs in the line."""
        if '\t' in line:
            self.message(
                line_no, 'Line contains a tab character.', icon='info')


class AnyTextChecker(BaseChecker, AnyTextMixin):
    """Verify the text of the document."""

    def __init__(self, file_path, text, reporter=None):
        self.file_path = file_path
        self.base_dir = os.path.dirname(file_path)
        self.file_name = os.path.basename(file_path)
        self.text = text
        self.set_reporter(reporter=reporter)

    def check(self):
        """Call each line_method for each line in text."""
        for line_no, line in enumerate(self.text.splitlines()):
            line_no += 1
            self.check_length(line_no, line)
            self.check_trailing_whitespace(line_no, line)
            self.check_conflicts(line_no, line)


class SQLChecker(BaseChecker, AnyTextMixin):
    """Verify SQL style."""

    def check(self):
        """Call each line_method for each line in text."""
        # Consider http://code.google.com/p/python-sqlparse/ to verify
        # keywords and reformatting.
        for line_no, line in enumerate(self.text.splitlines()):
            line_no += 1
            self.check_trailing_whitespace(line_no, line)
            self.check_tab(line_no, line)
            self.check_conflicts(line_no, line)


class XMLChecker(BaseChecker, AnyTextMixin):
    """Check XML documents."""

    xml_decl_pattern = re.compile(r'<\?xml .*?\?>')
    xhtml_doctype = """
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
          "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
        """

    def check(self):
        """Check the syntax of the python code."""
        if self.text == '':
            return
        parser = ElementTree.XMLParser()
        parser.entity.update(htmlentitydefs.entitydefs)
        offset = 0
        text = self.text
        if text.find('<!DOCTYPE') == -1:
            # Expat requires a doctype to honour parser.entity.
            offset = 3
            match = self.xml_decl_pattern.search(text)
            if match is None:
                text = self.xhtml_doctype + text
            else:
                start, end = match.span(0)
                text = text[:start] + self.xhtml_doctype + text[end:]
        try:
            ElementTree.parse(StringIO(text), parser)
        except (ExpatError, ParseError), error:
            if hasattr(error, 'code'):
                error_message = ErrorString(error.code)
                if hasattr(error, 'position') and error.position:
                    error_lineno, error_charno = error.position
                    error_lineno = error_lineno - offset
                elif error.lineno:
                    # Python 2.6-
                    error_lineno = error.lineno - offset
                else:
                    error_lineno = 0
            else:
                error_message, location = str(error).rsplit(':')
                error_lineno = int(location.split(',')[0].split()[1])- offset
            self.message(error_lineno, error_message, icon='error')
        self.check_text()

    def check_text(self):
        for line_no, line in enumerate(self.text.splitlines()):
            line_no += 1
            self.check_trailing_whitespace(line_no, line)
            self.check_conflicts(line_no, line)


class CSSReporterHandler(logging.Handler):
    """A logging handler that uses the checker to report issues."""

    error_pattern = re.compile(
        r'(?P<issue>[^(]+): \((?P<text>[^,]+, [^,]+), (?P<lineno>\d+).*')
    message_pattern = re.compile(
        r'(?P<issue>[^:]+:[^:]+): (?P<text>.*) (?P<lineno>0)$')

    def __init__(self, checker):
        logging.Handler.__init__(self, logging.INFO)
        self.checker = checker

    def handleError(self, record):
        pass

    def emit(self, record):
        if record.levelname == 'ERROR':
            icon = 'error'
        else:
            icon = 'info'
        matches = self.checker.message_pattern.search(record.getMessage())
        if matches is None:
            matches = self.error_pattern.search(record.getMessage())
        try:
            line_no = matches.group('lineno')
            message = "%s: %s" % (
                matches.group('issue'), matches.group('text'))
        except AttributeError:
            line_no = 0
            message = record.getMessage()
        self.checker.message(int(line_no), message, icon=icon)


class CSSChecker(BaseChecker, AnyTextMixin):
    """Check XML documents."""

    message_pattern = re.compile(
        r'[^ ]+ (?P<issue>.*) \[(?P<lineno>\d+):\d+: (?P<text>.+)\]')

    def check(self):
        """Check the syntax of the CSS code."""
        if self.text == '' or not HAS_CSSUTILS:
            return
        handler = CSSReporterHandler(self)
        log = logging.getLogger('pocket-lint')
        log.addHandler(handler)
        parser = cssutils.CSSParser(
            log=log, loglevel=logging.INFO, raiseExceptions=False)
        parser.parseString(self.text)
        log.removeHandler(handler)
        self.check_text()

    def check_text(self):
        """Call each line_method for each line in text."""
        for line_no, line in enumerate(self.text.splitlines()):
            line_no += 1
            self.check_length(line_no, line)
            self.check_trailing_whitespace(line_no, line)
            self.check_conflicts(line_no, line)
            self.check_tab(line_no, line)


class PythonChecker(BaseChecker, AnyTextMixin):
    """Check python source code."""

    def __init__(self, file_path, text, reporter=None):
        super(PythonChecker, self).__init__(
            file_path, text, reporter=reporter)
        self.is_utf8 = False

    def check(self):
        """Check the syntax of the python code."""
        if self.text == '':
            return
        self.check_flakes()
        self.check_pep8()
        self.check_text()

    def check_flakes(self):
        """Check compilation and syntax."""
        try:
            tree = compiler.parse(self.text)
        except (SyntaxError, IndentationError), exc:
            line_no = exc.lineno or 0
            line = exc.text or ''
            explanation = 'Could not compile; %s' % exc.msg
            message = '%s: %s' % (explanation, line.strip())
            self.message(line_no, message, icon='error')
        else:
            warnings = Checker(tree)
            for warning in warnings.messages:
                dummy, line_no, message = str(warning).split(':')
                self.message(int(line_no), message.strip(), icon='error')

    def check_pep8(self):
        """Check style."""
        try:
            # Monkey patch pep8 for direct access to the messages.
            original_report_error = pep8.Checker.report_error

            def pep8_report_error(ignore, line_no, offset, message, check):
                self.message(line_no, message, icon='info')

            pep8.Checker.report_error = pep8_report_error
            pep8.process_options([self.file_path])
            try:
                pep8.Checker(self.file_path).check_all()
            except TokenError, er:
                message, location = er.args
                self.message(location[0], message, icon='error')
        finally:
            Checker.report_error = original_report_error

    def check_text(self):
        """Call each line_method for each line in text."""
        for line_no, line in enumerate(self.text.splitlines()):
            line_no += 1
            if line_no in (1, 2) and '# -*- coding: utf-8 -*-' in line:
                self.is_utf8 = True
            self.check_pdb(line_no, line)
            self.check_length(line_no, line)
            self.check_trailing_whitespace(line_no, line)
            self.check_conflicts(line_no, line)
            self.check_tab(line_no, line)
            self.check_ascii(line_no, line)

    def check_pdb(self, line_no, line):
        """Check the length of the line."""
        pdb_call = 'pdb.' + 'set_trace'
        if pdb_call in line:
            self.message(
                line_no, 'Line contains a call to pdb.', icon='error')

    def check_ascii(self, line_no, line):
        """Check that the line is ascii."""
        if self.is_utf8:
            return
        try:
            line.encode('ascii')
        except UnicodeEncodeError, error:
            self.message(
                line_no, 'Non-ascii characer at position %s.' % error.end,
                icon='error')


class JavascriptChecker(BaseChecker, AnyTextMixin):
    """Check python source code."""

    HERE = os.path.dirname(__file__)
    FULLJSLINT = os.path.join(HERE, 'contrib/fulljslint.js')
    JSREPORTER = os.path.join(HERE, 'jsreporter.js')

    def check(self):
        """Check the syntax of the javascript code."""
        if JS is None or self.text == '':
            return
        args = [JS, '-f', self.FULLJSLINT, self.JSREPORTER, self.text]
        jslint = subprocess.Popen(
            args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        issues, errors = jslint.communicate()
        issues = issues.strip()
        if issues:
            for issue in issues.splitlines():
                line_no, char_no_, message = issue.split('::')
                self.message(int(line_no), message, icon='error')
        self.check_text()

    def check_text(self):
        """Call each line_method for each line in text."""
        for line_no, line in enumerate(self.text.splitlines()):
            line_no += 1
            self.check_length(line_no, line)
            self.check_trailing_whitespace(line_no, line)
            self.check_conflicts(line_no, line)
            self.check_tab(line_no, line)


def get_option_parser():
    """Return the option parser for this program."""
    usage = "usage: %prog [options] arg1"
    parser = OptionParser(usage=usage)
    parser.add_option(
        "-v", "--verbose", action="store_true", dest="verbose")
    parser.add_option(
        "-q", "--quiet", action="store_false", dest="verbose")
    parser.set_defaults(verbose=True)
    return parser


def check_sources(sources, reporter=None):
    if reporter is None:
        reporter = Reporter(Reporter.CONSOLE)
    for source in sources:
        file_path = os.path.normpath(source)
        if os.path.isdir(source) or not Language.is_editable(source):
            continue
        language = Language.get_language(file_path)
        with open(file_path) as file_:
            text = file_.read()
        checker = UniversalChecker(
            file_path, text=text, language=language, reporter=reporter)
        checker.check()


def main(argv=None):
    """Run the command line operations."""
    if argv is None:
        argv = sys.argv
    parser = get_option_parser()
    (options, sources) = parser.parse_args(args=argv[1:])
    # Handle standard args.
    if len(sources) == 0:
        parser.error("Expected file paths.")
    if options.verbose:
        pass
    reporter = Reporter(Reporter.CONSOLE)
    check_sources(sources, reporter)


if __name__ == '__main__':
    sys.exit(main())
