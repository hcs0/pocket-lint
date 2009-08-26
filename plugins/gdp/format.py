# Copyright (C) 2009 - Curtis Hovey <sinzui.is at verizon.net>
"""Format text and code"""

import os
import re

from textwrap import wrap
from gettext import gettext as _
from gtk import glade


class Formatter:
    """Format Gedit Document and selection text."""

    def __init__(self, window):
        self.window = window
        widgets = glade.XML('%s/gdp.glade' % os.path.dirname(__file__))
        widgets.signal_autoconnect(self.glade_callbacks)
        self.replace_dialog = widgets.get_widget('replace_dialog')
        self.replace_label = widgets.get_widget('replace_label')
        self.replace_label_text = self.replace_label.get_text()
        self.replace_pattern_entry = widgets.get_widget(
            'replace_pattern_entry')
        self.replace_replacement_entry = widgets.get_widget(
            'replace_replacement_entry')


    @property
    def glade_callbacks(self):
        """The dict of callbacks for the glade widgets."""
        return {
            'on_replace_quit' : self.on_replace_quit,
            'on_replace' : self.on_replace,
            }


    def _get_bounded_text(self):
        """Return tuple of the bounds and formattable text.

        The bounds mark either the selection or the document.
        """
        document = self.window.get_active_document()
        bounds = document.get_selection_bounds()
        if not bounds:
            bounds = (document.get_start_iter(), document.get_end_iter())
        text = document.get_text(*bounds)
        return bounds, text

    def _put_bounded_text(self, bounds, text):
        """Replace the current text between the bounds with the new text.

        This change is undoable.
        """
        document = self.window.get_active_document()
        document.begin_user_action()
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

    def quote_lines(self, data):
        """Quote the selected text passage."""
        bounds, text = self._get_bounded_text()
        lines = ['> %s' % line for line in text.splitlines()]
        self._put_bounded_text(bounds, '\n'.join(lines))

    def sort_imports(self, data):
        """Sort python imports."""
        bounds, text = self._get_bounded_text()
        padding = self._getPadding(text)
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

    def _getPadding(self, text):
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
            padding = self._getPadding(text)
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

    def re_replace(self, data):
        """Replace each line using an re pattern."""
        self.replace_dialog.show()
        self.replace_dialog.run()

    def on_replace_quit(self, widget=None):
        """End the replacement, hide he dialog."""
        self.replace_dialog.hide()

    def on_replace(self, widget=None):
        """replace each line of text."""
        pattern = self.replace_pattern_entry.get_text()
        replacement = self.replace_replacement_entry.get_text()
        try:
            line_re = re.compile(pattern)
        except re.error:
            # Show a message that the pattern failed.
            message = _("The regular expression pattern has an error in it.")
            self.replace_label.set_markup(
                '%s\n<b>%s</b>' % (self.replace_label_text, message))
            self.replace_dialog.run()
            return
        bounds, text = self._get_bounded_text()
        lines = [line_re.sub(replacement, line) for line in text.splitlines()]
        self._put_bounded_text(bounds, '\n'.join(lines))
        self.on_replace_quit()

