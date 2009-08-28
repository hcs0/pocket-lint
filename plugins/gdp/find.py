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

import gtk


mimetypes.init()


def find_matches(root_dir, file_pattern, match_pattern, substitution=None):
    """Iterate a summary of matching lines in a file."""
    match_re = re.compile(match_pattern)
    for file_path in find_files(root_dir, file_pattern=file_pattern):
        summary = extract_match(
            file_path, match_re, substitution=substitution)
        if summary:
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
                    yield file_path


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


class Finder:
    """Find and replace content in files."""

    def __init__(self, window):
        self.window = window
        self.widgets = gtk.glade.XML(
            '%s/gdp.glade' % os.path.dirname(__file__), root='find_panel')
        self.widgets.signal_autoconnect(self.glade_callbacks)
        self.find_panel = self.widgets.get_widget('find_panel')
        panel = window.get_bottom_panel()
        icon = gtk.image_new_from_stock(gtk.STOCK_FIND, gtk.ICON_SIZE_MENU)
        panel.add_item(self.find_panel, 'Find in files', icon)

    @property
    def glade_callbacks(self):
        """The dict of callbacks for the glade widgets."""
        return {
            'on_find_in_files' : self.on_find_in_files,
            }

    def show(self, data):
        """Show the finder pane."""
        panel = self.window.get_bottom_panel()
        panel.activate_item(self.find_panel)
        panel.props.visible = True

    def on_find_in_files(self, widget=None):
        """Find and present the matches."""
        text = self.widgets.get_widget(
            'match_pattern_combobox').get_active_text()
        is_re = self.widgets.get_widget('re_checkbox').get_active()
        if not is_re:
            text = re.escape(text)
        is_case = self.widgets.get_widget('match_case_checkbox').get_active()
        if not is_case:
            text = '(?i)%s' % text
        print "Looking for [%s] in %s:" % (text, '.')
        for summary in find_matches('.', '.', text, substitution=None):
            print "\n%(file_path)s" % summary
            for line in summary['lines']:
                print "    %(lineno)4s: %(text)s" % line


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
