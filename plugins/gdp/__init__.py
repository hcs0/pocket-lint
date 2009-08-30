"""GDP Gedit Developer Plugins."""

__metaclass__ = type

__all__  = [
    'PluginMixin',
    ]


import mimetypes

import gobject
import gtk


class PluginMixin:
    """Provide common features to plugins"""

    def initialize(self, gedit):
        """Initialize the common plugin services"""
        self.gedit = gedit
        self.utf8_encoding = gedit.encoding_get_from_charset('UTF-8')
        mimetypes.init()

    def is_doc_open(self, uri):
        """Return True if the window already has a document opened for uri."""
        for doc in self.window.get_documents():
            if doc.get_uri() == uri:
                return True
        return False

    def open_doc(self, uri):
        """Open document at uri if it can be, and is not already, opened."""
        if self.is_doc_open(uri):
            return
        mime_type, charset_ = mimetypes.guess_type(uri)
        if mime_type is None or 'text/' in mime_type:
            # This appears to be a file that gedit can open.
            encoding = self.utf8_encoding
            self.window.create_tab_from_uri(uri, encoding, 0, False, False)


def set_file_line(column, cell, model, piter):
    """Set the value as file or line information."""
    file_path  = model.get_value(piter, 0)
    mime_type  = model.get_value(piter, 1)
    line_no = model.get_value(piter, 2)
    text = model.get_value(piter, 3)
    if line_no is None:
        cell.props.text = file_path
    else:
        cell.props.text = '%4s:  %s' % (line_no, text)


def setup_file_lines_view(match_view):
    """Setup a TreeView to displau files and their lines."""
    treestore = gtk.TreeStore(
        gobject.TYPE_STRING, gobject.TYPE_STRING,
        gobject.TYPE_STRING, gobject.TYPE_STRING)
    treestore.append(None, ('No matches', None, None, None))
    column = gtk.TreeViewColumn('Matches')
    cell = gtk.CellRendererPixbuf()
    cell.set_property('stock-size', gtk.ICON_SIZE_MENU)
    column.pack_start(cell, False)
    column.add_attribute(cell, 'icon-name', 1)
    cell = gtk.CellRendererText()
    column.pack_start(cell, False)
    column.set_cell_data_func(cell, set_file_line)
    match_view.set_model(treestore)
    match_view.append_column(column)
    match_view.set_search_column(0)
