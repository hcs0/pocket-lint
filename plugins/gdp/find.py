#!/usr/bin/python
"""Find in files and replace strings in many files."""

__metaclass__ = type

__all__ = [
    'extract_match',
    'find_files',
    'find_matches',
    'Finder',
    ]

import mimetypes
import os
import re
import sys
from optparse import OptionParser

import gobject
import gtk

from gdp import PluginMixin, setup_file_lines_view


def find_matches(root_dir, file_pattern, match_pattern, substitution=None):
    """Iterate a summary of matching lines in a file."""
    match_re = re.compile(match_pattern)
    for candidate in find_files(root_dir, file_pattern=file_pattern):
        file_path, mime_type = candidate
        summary = extract_match(
            file_path, match_re, substitution=substitution)
        if summary:
            summary['mime_type'] = mime_type
            yield summary


def find_files(root_dir, skip_dir_pattern='^[.]', file_pattern='.*'):
    """Iterate the matching files below a directory."""
    skip_dir_re = re.compile(r'^.*%s' % skip_dir_pattern)
    file_re = re.compile(r'^.*%s' % file_pattern)
    for path, subdirs, files in os.walk(root_dir):
        subdirs[:] = [dir_ for dir_ in subdirs
                      if skip_dir_re.match(dir_) is None]
        for file_ in files:
            file_path = os.path.join(path, file_)
            if os.path.islink(file_path):
                continue
            mime_type, encoding_ = mimetypes.guess_type(file_)
            if mime_type is None or 'text/' in mime_type:
                if file_re.match(file_path) is not None:
                    yield file_path, mime_type


def extract_match(file_path, match_re, substitution=None):
    """Return a summary of matches in a file."""
    lines = []
    content = []
    match = None
    file_ = open(file_path, 'r')
    try:
        for lineno, line in enumerate(file_):
            match = match_re.search(line)
            if match:
                lines.append(
                    {'lineno': lineno + 1, 'text': line.strip(),
                     'match': match})
                if substitution is not None:
                    line = match_re.sub(substitution, line)
            if substitution is not None:
                content.append(line)
    finally:
        file_.close()
    if lines:
        if substitution is not None:
            file_ = open(file_path, 'w')
            try:
                file_.write(''.join(content))
            finally:
                file_.close()
        return {'file_path': file_path, 'lines': lines}
    return None


class Finder(PluginMixin):
    """Find and replace content in files."""

    WORKING_DIRECTORY = '<Working Directory>'
    CURRENT_FILE= '<Current File>'
    ANY_FILE = '<Any Text File>'

    def __init__(self, window):
        self.window = window
        self.widgets = gtk.Builder()
        self.widgets.add_from_file(
            '%s/find.ui' % os.path.dirname(__file__))
        self.setup_widgets()
        self.find_panel = self.widgets.get_object('find_panel')
        panel = window.get_bottom_panel()
        icon = gtk.image_new_from_stock(gtk.STOCK_FIND, gtk.ICON_SIZE_MENU)
        panel.add_item(self.find_panel, 'Find in files', icon)

    def setup_widgets(self):
        """Setup the widgets with default data."""
        self.widgets.connect_signals(self.ui_callbacks)
        self.pattern_comboentry = self.widgets.get_object(
            'pattern_comboentry')
        self.setup_comboentry(self.pattern_comboentry)
        self.path_comboentry = self.widgets.get_object('path_comboentry')
        self.setup_comboentry(self.path_comboentry, os.getcwd())
        self.update_comboentry(self.path_comboentry, self.CURRENT_FILE)
        self.file_comboentry = self.widgets.get_object('file_comboentry')
        self.setup_comboentry(self.file_comboentry, self.ANY_FILE)
        self.substitution_comboentry = self.widgets.get_object(
            'substitution_comboentry')
        self.setup_comboentry(self.substitution_comboentry)
        self.file_lines_view = self.widgets.get_object('file_lines_view')
        setup_file_lines_view(self.file_lines_view, self, 'Matches')

    def setup_comboentry(self, comboentry, default=None):
        liststore = gtk.ListStore(gobject.TYPE_STRING)
        liststore.set_sort_column_id(0, gtk.SORT_ASCENDING)
        comboentry.set_model(liststore)
        comboentry.set_text_column(0)
        if default is not None:
            self.update_comboentry(comboentry, default)

    def update_comboentry(self, comboentry, text):
        """Update the match text combobox."""
        is_unique = True
        for row in iter(comboentry.get_model()):
            if row[0] == text:
                is_unique = False
                break
        if is_unique:
            comboentry.append_text(text)

    @property
    def ui_callbacks(self):
        """The dict of callbacks for the ui widgets."""
        return {
            'on_find_in_files': self.on_find_in_files,
            'on_replace_in_files': self.on_replace_in_files,
            }

    def show(self, data):
        """Show the finder pane."""
        panel = self.window.get_bottom_panel()
        panel.activate_item(self.find_panel)
        panel.props.visible = True

    def show_replace(self, data):
        """Show the finder pane and expand replace."""
        self.show(None)
        self.widgets.get_object('actions').activate()

    @property
    def path(self):
        """The base directory to traverse set by the user."""
        path_ = self.path_comboentry.get_active_text()
        if path_ in (self.WORKING_DIRECTORY, '', None):
            path_ = '.'
        elif path_ == self.CURRENT_FILE:
            document = self.active_document
            path_ = os.path.dirname(document.get_uri_for_display())
        return path_

    @property
    def file_pattern(self):
        """The pattern to match the file name with."""
        pattern = self.file_comboentry.get_active_text()
        if pattern in (self.ANY_FILE, '', None):
            pattern = '.'
        if self.path_comboentry.get_active_text() == self.CURRENT_FILE:
            document = self.active_document
            pattern = os.path.basename(document.get_uri_for_display())
        return pattern

    def on_find_in_files(self, widget=None, substitution=None):
        """Find and present the matches."""
        pattern = self.pattern_comboentry.get_active_text()
        self.update_comboentry(self.pattern_comboentry, pattern)
        treestore = self.file_lines_view.get_model()
        treestore.clear()
        base_dir = os.path.abspath(self.path)
        self.file_lines_view.get_column(0).props.title = (
            "Matches for [%s] in %s" % (pattern, base_dir))
        if not self.widgets.get_object('re_checkbox').get_active():
            pattern = re.escape(pattern)
        if not self.widgets.get_object('match_case_checkbox').get_active():
            pattern = '(?i)%s' % pattern
        for summary in find_matches(
            self.path, self.file_pattern, pattern, substitution=substitution):
            file_path = summary['file_path']
            mime_type = summary['mime_type']
            if mime_type is None:
                mime_type = 'gnome-mime-text'
            else:
                # mime_type = 'gnome-mime-%s' % mime_type.replace('/', '-')
                mime_type = 'gnome-mime-text'
            piter = treestore.append(
                None, (file_path, mime_type, 0, None, base_dir))
            if substitution is None:
                icon = 'stock_mail-forward'
            else:
                icon = 'stock_mail-reply'
            for line in summary['lines']:
                treestore.append(piter,
                    (file_path, icon, line['lineno'], line['text'],
                     base_dir))
        if treestore.get_iter_first() is None:
            treestore.append(
                None,
                ('No matches found', 'stock_dialog-info', 0, None, None))

    def on_replace_in_files(self, widget=None):
        """Find, replace, and present the matches."""
        substitution = self.substitution_comboentry.get_active_text() or ''
        self.update_comboentry(self.substitution_comboentry, substitution)
        self.on_find_in_files(substitution=substitution)


def get_option_parser():
    """Return the option parser for this program."""
    usage = "usage: %prog [options] root_dir file_pattern match"
    parser = OptionParser(usage=usage)
    parser.add_option(
        "-s", "--substitution", dest="substitution",
        help="The substitution string (may contain \\[0-9] match groups).")
    parser.set_defaults(substitution=None)
    return parser


def main(argv=None):
    """Run the command line operations."""
    if argv is None:
        argv = sys.argv
    parser = get_option_parser()
    (options, args) = parser.parse_args(args=argv[1:])

    root_dir = args[0]
    file_pattern = args[1]
    match_pattern = args[2]
    substitution = options.substitution
    print "Looking for [%s] in files like %s under %s:" % (
        match_pattern, file_pattern, root_dir)
    for summary in find_matches(
        root_dir, file_pattern, match_pattern, substitution=substitution):
        print "\n%(file_path)s" % summary
        for line in summary['lines']:
            print "    %(lineno)4s: %(text)s" % line


if __name__ == '__main__':
    sys.exit(main())
