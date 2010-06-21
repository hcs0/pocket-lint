#!/usr/bin/python
# Copyright (C) 2009 - Curtis Hovey <sinzui.is at verizon.net>
# This software is licensed under the GNU General Public License version 2
# (see the file COPYING).
"""Check for syntax and style problems."""

__metatype__ = type

__all__ = [
    'Reporter',
    'UniversalChecker',
    ]

import compiler
import htmlentitydefs
import logging
import mimetypes
import os
import re
import sys

from optparse import OptionParser
from StringIO import StringIO
from xml.etree import ElementTree
from xml.parsers.expat import ErrorString, ExpatError

from gdp.formatdoctest import DoctestReviewer

import contrib.pep8 as pep8
from contrib.pyflakes.checker import Checker
try:
    import cssutils
    HAS_CSSUTILS = True
except ImportError:
    HAS_CSSUTILS = False


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
        print '%4s: %s' % (line_no, message)

    def _message_file_lines(self, line_no, message, icon=None,
                            base_dir=None, file_name=None):
        """Display the messages in the file_lines_view."""
        if self.piter is None:
            mime_type = 'gnome-mime-text'
            self.piter = self.treestore.append(
                None, (file_name, mime_type, 0, None, base_dir))
        self.treestore.append(
            self.piter, (file_name, icon, line_no, message, base_dir))


class ReporterHandler(logging.Handler):
    """A logging handler that uses the checker to report issues."""

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
        line_no = matches.group(2)
        message = "%s: %s" % (matches.group(1), matches.group(3))
        self.checker.message(int(line_no), message, icon=icon)


doctest_pattern = re.compile(
    r'^.*(doc|test|stories).*/.*\.(txt|doctest)$')


class Language:
    """Supported Language types."""
    TEXT = object()
    PYTHON = object()
    DOCTEST = object()
    CSS = object()
    XML = object()
    XSLT = object()
    HTML = object()
    ZPT = object()
    DOCBOOK = object()

    XML_LIKE = (XML, XSLT, HTML, ZPT, DOCBOOK)

    mime_type_language = {
        'text/x-python': PYTHON,
        'text/css': CSS,
        'application/xml': XML,
        'text/html': HTML,
        'text/plain': TEXT,
        }

    def get_language(self, file_path):
        """Return the language for the source."""
        # Doctests can easilly be mistyped, so it must be checked first.
        if doctest_pattern.match(file_path):
            return Language.DOCTEST
        mime_type, encoding = mimetypes.guess_type(file_path)
        if mime_type.endswith('+xml'):
            return Language.XML
        if mime_type in Language.XML_LIKE:
            return Language.XML
        if mime_type in Language.mime_type_language:
            return Language.mime_type_language[mime_type]


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
        elif self.language is Language.doctest:
            DoctestReviewer(self.text, self.file_path, self._reporter).check()
        elif self.language is Language.css:
            CSSChecker(self.file_path, self.text, self._reporter).check()
        elif self.language in Language.XML_LIKE:
            XMLChecker(self.file_path, self.text, self._reporter).check()
        else:
            AnyTextChecker(self.file_path, self.text, self._reporter).check()
        self._reporter.file_lines_view.expand_all()


class AnyTextMixin:
    """Common checks for many checkers."""

    def check_conflicts(self, line_no, line):
        """Check that there are no merge conflict markers."""
        if line.startswith('<<<<<<<'):
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
            self.check_length(line_no, line)
            self.check_trailing_whitespace(line_no, line)
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
            root = ElementTree.parse(StringIO(text), parser)
        except ExpatError, error:
            if hasattr(error, 'code'):
                error_message = ErrorString(error.code)
                error_lineno = error.lineno - offset
            else:
                error_message, location = str(error).rsplit(':')
                error_lineno = int(location.split(',')[0].split()[1])- offset
            self.message(error_lineno, error_message, icon='error')
        for line_no, line in enumerate(self.text.splitlines()):
            self.check_trailing_whitespace(line_no, line)
            self.check_conflicts(line_no, line)


class CSSChecker(BaseChecker, AnyTextMixin):
    """Check XML documents."""

    message_pattern = re.compile(r'[^ ]+ (.*) \[(\d+):\d+: (.+)\]')

    def check(self):
        """Check the syntax of the CSS code."""
        if self.text == '' or not HAS_CSSUTILS:
            return
        # Suppress the default reports to stderr.
        cssutils.log._log = logging.getLogger('gdp')
        cssutils.log.raiseExceptions = False
        # Add a handler that will report data during parsing.
        cssutils.log.addHandler(ReporterHandler(self))
        cssutils.parseString(self.text)


class PythonChecker(BaseChecker):
    """Check python source code."""

    def check(self):
        """Check the syntax of the python code."""
        if self.text == '':
            return
        self.check_flakes()
        self.check_pep8()

    def check_flakes(self):
        """Check compilation and syntax."""
        try:
            tree = compiler.parse(self.text)
        except (SyntaxError, IndentationError), exc:
            (line_no, offset, line) = exc[1][1:]
            message = 'Could not compile offset %s: %s' % (
                offset, line.strip())
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
            pep8.Checker(self.file_path).check_all()
        finally:
            Checker.report_error = original_report_error


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


def check_sources(sources):
    for source in sources:
        file_path = os.path.normpath(source)
        language = Language.get_language(file_path)
        with open(file_path) as file_:
            text = file_.read()
        reporter = Reporter(Reporter.CONSOLE)
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
    check_sources(sources)


if __name__ == '__main__':
    sys.exit(main())
