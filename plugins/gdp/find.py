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

from gdp import PluginMixin


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
                    {'lineno' : lineno + 1, 'text' : line.strip(),
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
        return {'file_path' : file_path, 'lines' : lines}
    return None


def set_file_line(column, cell, model, piter):
    """Set the value as file or line information."""
    file_path  = model.get_value(piter, 0)
    mime_type  = model.get_value(piter, 1)
    line_no = model.get_value(piter, 2)
    text = model.get_value(piter, 3)
    if line_no is None:
        cell.props.text = file_path
    else:
        cell.props.text = '%4s  %s' % (line_no, text)


class Finder(PluginMixin):
    """Find and replace content in files."""

    def __init__(self, gedit, window):
        self.initialize(gedit)
        self.window = window
        self.widgets = gtk.glade.XML(
            '%s/gdp.glade' % os.path.dirname(__file__), root='find_panel')
        self.setup_widgets()
        self.find_panel = self.widgets.get_widget('find_panel')
        panel = window.get_bottom_panel()
        icon = gtk.image_new_from_stock(gtk.STOCK_FIND, gtk.ICON_SIZE_MENU)
        panel.add_item(self.find_panel, 'Find in files', icon)

    def setup_widgets(self):
        """Setup the widgets with default data."""
        self.widgets.signal_autoconnect(self.glade_callbacks)
        liststore = gtk.ListStore(gobject.TYPE_STRING)
        liststore.set_sort_column_id(0, gtk.SORT_ASCENDING)
        combobox = self.widgets.get_widget('match_pattern_combobox')
        combobox.set_model(liststore)
        # Glade setup the first column from string.
        combobox.set_text_column(0)
        treestore = gtk.TreeStore(
            gobject.TYPE_STRING, gobject.TYPE_STRING,
            gobject.TYPE_STRING, gobject.TYPE_STRING)
        treestore.append(None, ('No matches', None, None, None))
        self.column = gtk.TreeViewColumn('Matches')
        cell = gtk.CellRendererText()
        self.column.pack_start(cell, False)
        #self.column.add_attribute(cell, 'text', 0)
        self.column.set_cell_data_func(cell, set_file_line)
        match_view = self.widgets.get_widget('match_view')
        match_view.set_model(treestore)
        match_view.append_column(self.column)
        match_view.set_search_column(0)


    @property
    def glade_callbacks(self):
        """The dict of callbacks for the glade widgets."""
        return {
            'on_find_in_files' : self.on_find_in_files,
            }

    def update_match_text(self, combobox, text):
        """Update the match text combobox."""
        is_unique = True
        for row in iter(combobox.get_model()):
            if row[0] == text:
                is_unique = False
                break
        if is_unique:
            combobox.append_text(text)

    def show(self, data):
        """Show the finder pane."""
        panel = self.window.get_bottom_panel()
        panel.activate_item(self.find_panel)
        panel.props.visible = True

    def on_find_in_files(self, widget=None):
        """Find and present the matches."""
        combobox = self.widgets.get_widget('match_pattern_combobox')
        text = combobox.get_active_text()
        self.update_match_text(combobox, text)
        match_view = self.widgets.get_widget('match_view')
        treestore = match_view.get_model()
        treestore.clear()
        self.column.props.title = "Matches for [%s] in %s" % (
            text, os.path.abspath('.'))
        if not self.widgets.get_widget('re_checkbox').get_active():
            text = re.escape(text)
        if not self.widgets.get_widget('match_case_checkbox').get_active():
            text = '(?i)%s' % text
        for summary in find_matches('.', '.', text, substitution=None):
            piter = treestore.append(None, (
                summary['file_path'], summary['mime_type'], None, None))
            for line in summary['lines']:
                treestore.append(
                    piter, (
                        summary['file_path'], summary['mime_type'],
                        line['lineno'], line['text']))


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
