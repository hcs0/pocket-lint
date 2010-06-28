# Copyright (C) 2009-2010 - Curtis Hovey <sinzui.is at verizon.net>
# This software is licensed under the MIT license (see the file COPYING).
"""Format text and code

This is vestigal and may be removed. It is not used at this time.
"""

__metatype__ = type

import re

import gconf
from textwrap import wrap

from formatdoctest import DoctestReviewer
from formatcheck import Reporter, UniversalChecker

__all__ = [
    'Formatter',
    ]


class Formatter:
    """Format Gedit Document and selection text."""

    def _get_bounded_text(self):
        """Return tuple of the bounds and formattable text.

        The bounds mark either the selection or the document.
        """
        document = self.active_document
        bounds = document.get_selection_bounds()
        if not bounds:
            bounds = (document.get_start_iter(), document.get_end_iter())
        text = document.get_text(*bounds)
        return bounds, text

    def _put_bounded_text(self, bounds, text):
        """Replace the current text between the bounds with the new text.

        This change is undoable.
        """
        document = self.active_document
        document.begin_user_action()
        document.place_cursor(bounds[0])
        document.delete(*bounds)
        document.insert_at_cursor(text)
        document.end_user_action()

    def _single_line(self, text):
        """Return the text as a single line.."""
        lines = [line.strip() for line in text.splitlines()]
        return ' '.join(lines)

    def single_line(self, data):
        """Format the text as a single line."""
        bounds, text = self._get_bounded_text()
        text = self._single_line(text)
        self._put_bounded_text(bounds, text)

    def newline_ending(self, data):
        """Fix the selection's line endings."""
        bounds, text = self._get_bounded_text()
        lines = [line.rstrip() for line in text.splitlines()]
        self._put_bounded_text(bounds, '\n'.join(lines))

    def tabs_to_spaces(self, data):
        """Fix the selection's line endings."""
        bounds, text = self._get_bounded_text()
        gconf_client = gconf.client_get_default()
        tab_size = gconf_client.get_int(
            '/apps/gedit-2/preferences/editor/tabs/tabs_size') or 4
        tab_spaces = ' ' * tab_size
        lines = [line.replace('\t', tab_spaces) for line in text.splitlines()]
        self._put_bounded_text(bounds, '\n'.join(lines))

    def quote_lines(self, data):
        """Quote the selected text passage."""
        bounds, text = self._get_bounded_text()
        lines = ['> %s' % line for line in text.splitlines()]
        self._put_bounded_text(bounds, '\n'.join(lines))

    def sort_imports(self, data):
        """Sort python imports."""
        bounds, text = self._get_bounded_text()
        padding = self._get_padding(text)
        line = self._single_line(text)
        imports = line.split(', ')
        imports = sorted(imports, key=str.lower)
        imports = [imp.strip() for imp in imports if imp != '']
        text = self._wrap_text(', '.join(imports), padding=padding)
        self._put_bounded_text(bounds, text)

    def wrap_selection_list(self, data):
        """Wrap long lines and preserve indentation."""
        # This should use the textwrap module.
        paras = []
        indent_re = re.compile('^( +[0-9*-]*\.*)')
        bounds, text = self._get_bounded_text()
        for line in text.splitlines():
            match = indent_re.match(line)
            if match is not None:
                symbol = match.group(1)
                # When there is not symbol in the indent, remove a space
                # because a space is automatically added for the symbol.
                if not symbol.replace(' ', ''):
                    symbol = symbol[0:-1]
            else:
                symbol = ''
            padding_size = len(symbol)
            padding = ' ' * padding_size
            run = 72 - padding_size
            new_lines = []
            new_line = [symbol]
            new_length = padding_size
            # ignore the symbol
            words = line.split()
            for word in words[1:]:
                # The space between the words is 1
                if new_length + 1 + len(word) > run:
                    new_lines.append(' '.join(new_line))
                    new_line = [padding]
                    new_length = padding_size
                new_line.append(word)
                new_length += 1 + len(word)
            new_lines.append(' '.join(new_line))
            paras.extend(new_lines)
        self._put_bounded_text(bounds, '\n'.join(paras))

    def _get_padding(self, text):
        """Return the leading whitespace.

        Return '' if there is not leading whitespace.
        """
        leading_re = re.compile(r'^(\s+)')
        match = leading_re.match(text)
        if match:
            return match.group(1)
        else:
            return ''

    def _wrap_text(self, text, width=78, padding=None):
        """Wrap long lines."""
        if padding is None:
            padding = self._get_padding(text)
        line = self._single_line(text)
        lines = wrap(
            line, width=width, initial_indent=padding,
            subsequent_indent=padding)
        paragraph = '\n'.join(lines)
        return paragraph

    def rewrap_text(self, data):
        """Rewrap the paragraph."""
        bounds, text = self._get_bounded_text()
        text = self._wrap_text(text)
        self._put_bounded_text(bounds, text)

    def reformat_css(self, data):
        """Reformat the CSS."""
        bounds, text = self._get_bounded_text()
        # Break the text into rules using the trailing brace; the last item
        # is not css.
        rules = text.split('}')
        trailing_text = rules.pop().strip()
        css = []
        for rule in rules:
            rule = rule.strip()
            selectors, properties = rule.split('{')
            css.append('%s {' % selectors.strip())
            for prop in properties.split(';'):
                if not prop:
                    # We always check after the last semicolon because it is
                    # a common mistake to forget it on the last property.
                    # This loop fixes the syntax if there is remaining text.
                    break
                prop = ': '.join(
                    [part.strip() for part in prop.split(':')])
                css.append('    %s;' % prop)
            css.append('    }')
        if trailing_text:
            # This could be a comment.
            css.append(trailing_text)
        self._put_bounded_text(bounds, '\n'.join(css))

    def reformat_doctest(self, data):
        """Reformat the doctest."""
        bounds, text = self._get_bounded_text()
        file_name = self.active_document.get_uri_for_display()
        reviewer = DoctestReviewer(text, file_name)
        new_text = reviewer.format()
        self._put_bounded_text(bounds, new_text)

    def _check_style(self, document):
        """Check the style and syntax of a document."""
        file_path = document.get_uri_for_display()
        language = document.get_language()
        if language is not None:
            language_id = language.get_id()
        else:
            language_id = 'text'
        start_iter = document.get_start_iter()
        end_iter = document.get_end_iter()
        text = document.get_text(start_iter, end_iter)
        reporter = Reporter(
            Reporter.FILE_LINES, treeview=self.file_lines_view)
        checker = UniversalChecker(
            file_path, text=text, language=language_id, reporter=reporter)
        checker.check()

    def check_style(self, data, documents=None):
        """Check the style and syntax of the active document."""
        if documents is None:
            documents = [self.active_document]
        for document in documents:
            self._check_style(document)
        model = self.file_lines_view.get_model()
        if model.get_iter_first() is None:
            model.append(
                None, ('No problems found', 'emblem-default', 0, None, None))

    def check_all_style(self, data):
        """Check the style and syntax of all open documents."""
        self.check_style(None, documents=self.window.get_documents())
