#!/usr/bin/python
# [Gedit Tool]
# Comment=Format Selections
# Name=Format selection
# Input=selection
# Applicability=all
# Shortcut=<Alt>slash
# Output=replace-selection

"""Gedit tools hack to do better selection work."""

import os
import re
from textwrap import wrap
import sys

import gobject
import gtk
from gtk import glade


class SelectionTasks(object):
    """Text processing tasks.

    Text passed through stdin is processed and sent to stdout.
    """
    def __init__(self, with_ui=True):
        """Create the window to select a task."""
        if with_ui:
            self.widgets = glade.XML('%s/task-selection.glade' %
                os.path.dirname(os.sys.argv[0]))
            callbacks = {'on_quit' : self.on_quit,
                         'on_run_task' : self.on_run_task,
                         'on_replace_quit' : self.on_replace_quit,
                         'on_replace' : self.on_replace,}
            self.widgets.signal_autoconnect(callbacks)
            self.window = self.widgets.get_widget('task_window')
            self.replace_dialog = self.widgets.get_widget('replace_dialog')
            self.tasks = self.init_task_list(
                self.widgets.get_widget('task_combobox'))

    def init_task_list(self, combobox):
        """Add all methods start with 'task_' to the task list.
        
        Return a dictionary of the description and the method of each task.
        """
        tasks = {}
        for method_name in dir(self):
            method = getattr(self, method_name)
            if callable(method) and method_name.startswith('task_'):
                tasks[method.__doc__] = method

        model = gtk.ListStore(gobject.TYPE_STRING)
        for task in sorted(tasks.keys()):
            model.append([task])
        combobox.set_model(model)
        text = gtk.CellRendererText()
        combobox.pack_start(text, False)
        combobox.add_attribute(text, 'text', 0)
        combobox.set_active(0)
        return tasks

    def on_quit(self, widget=None):
        """Quit the application."""
        if widget is not None and not os.sys.stdin.isatty():
            # The window was closed without running a task.
            # Return the input so that it can be restored to the document.
            for line in os.sys.stdin:
                os.sys.stdout.write(line)
        gtk.main_quit()

    def on_run_task(self, widget):
        """Run the selected task."""
        task_name = self.widgets.get_widget('task_combobox').get_active_text()
        self.tasks[task_name]()
        self.on_quit()

    # Methods named with 'task_' will be displayed in the combobox for
    # the user to select.
    def task_selection_to_one_line(self):
        """Convert the selection to one line."""
        lines = []
        for line in os.sys.stdin:
            lines.append(line.strip())
        long_line = ' ' + ' '.join(lines)
        os.sys.stdout.write(long_line.strip())

    def task_rewrap_list(self):
        """Rewrap list."""
        paras = []
        indent_re = re.compile('^( +[0-9*-]*\.*)')
        for line in os.sys.stdin:
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
        os.sys.stdout.write('\n'.join(paras))

    def getPadding(self, text):
        """Return the leading whitespace.

        Return '' if there is not leading whitespace.
        """
        leading_re = re.compile(r'^(\s+)')
        match = leading_re.match(text)
        if match:
            return match.group(1)
        else:
            return ''

    def wrap_text(self, text, width=72):
        """Wrap long lines."""
        padding = self.getPadding(text)
        width = width - len(padding)
        text = re.sub(r'\s+', ' ' , text.strip())
        lines = wrap(text, width)
        joiner = '\n%s' % padding
        paragraph = padding + joiner.join(lines)
        return paragraph

    def task_rewrap_paragraph(self):
        """Rewrap the paragraph."""
        text = os.sys.stdin.read()
        paragraph = self.wrap_text(text)
        os.sys.stdout.write(paragraph)

    def task_newline_ending(self):
        """Fix the selection's line endings."""
        lines = []
        for line in os.sys.stdin:
            lines.append(line.rstrip())
        text = '\n'.join(lines)
        os.sys.stdout.write(text)

    def _format_paragraph(self, paragraph, lines):
        """Rewrap the paragraph and normalize leading blank lines."""
        long_line = ' '.join(paragraph).strip()
        paragraph_lines = wrap(long_line, 72)
        # One blank line between blocks, except for headings, which
        # should have two leading blanks
        if len(lines) != 0 and long_line[0] == '=':
            paragraph_lines.insert(0, '')
        return paragraph_lines

    def task_quote_line(self):
        """Quote the selected text passage."""
        lines = []
        for line in os.sys.stdin:
            lines.append('> %s' % line)
        os.sys.stdout.write(''.join(lines))

    def task_sort_imports(self):
        """Sort python imports."""
        lines = []
        padding = None
        for line in os.sys.stdin:
            if padding is None:
                padding = self.getPadding(line)
            lines.append(line.strip())
        text = ' '.join(lines)
        imports = text.split(', ')
        imports = sorted(imports, key=str.lower)
        imports = [imp.strip() for imp in imports if imp != '']
        paragraph = self.wrap_text(padding + ', '.join(imports), width=78)
        os.sys.stdout.write(paragraph)

    def task_re_replace(self):
        """Replace each line using an re pattern."""
        self.replace_label_text = self.widgets.get_widget(
            'replace_label').get_text()
        self.replace_dialog.show()
        self.replace_dialog.run()

    def on_replace_quit(self, widget=None):
        """End the replacement, and restore the selection."""
        for line in os.sys.stdin:
            os.sys.stdout.write(line)

    def on_replace(self, widget=None):
        """replace."""
        pattern = self.widgets.get_widget('replace_pattern_entry').get_text()
        replacement = self.widgets.get_widget(
            'replace_replacement_entry').get_text()
        try:
            line_re = re.compile(pattern)
        except re.error:
            # Show a message that the pattern failed.
            message = 'The regular expression pattern has an error in it.'
            self.widgets.get_widget('replace_label').set_markup(
                '%s\n<b>%s</b>' % (self.replace_label_text, message))
            self.replace_dialog.run()
            return
        lines = []
        for line in os.sys.stdin:
            lines.append(line_re.sub(replacement, line))
        os.sys.stdout.write(''.join(lines))
        self.on_replace_quit()


if __name__ == '__main__':
    args = sys.argv
    if len(args) > 1 and '-q' == args[1]:
        selections = SelectionTasks(with_ui=False)
        selections.task_quote_line()
    else:
        ui = SelectionTasks()
        gtk.main()
    sys.exit(0)












