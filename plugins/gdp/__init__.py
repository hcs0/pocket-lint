"""GDP Gedit Developer Plugins."""

__metaclass__ = type

__all__ = [
    'PluginMixin',
    ]


import mimetypes
import os

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

    def open_doc(self, uri, jump_to=None):
        """Open document at uri if it can be, and is not already, opened."""
        if self.is_doc_open(uri):
            return
        mime_type, charset_ = mimetypes.guess_type(uri)
        if mime_type is None or 'text/' in mime_type:
            # This appears to be a file that gedit can open.
            encoding = self.utf8_encoding
            jump_to = jump_to or 0
            self.window.create_tab_from_uri(
                uri, encoding, jump_to, False, False)

    def activate_open_doc(self, uri, jump_to=None):
        """Activate (or open) a document and jump to the line number."""
        self.open_doc(uri, jump_to)
        self.window.set_active_tab(self.window.get_tab_from_uri(uri))
        if jump_to is not None:
            self.window.get_active_document().goto_line(jump_to)
            self.window.get_active_view().scroll_to_cursor()

    @property
    def text(self):
        """The text of the active gedit.Document or None."""
        document = self.window.get_active_document()
        start_iter = document.get_start_iter()
        end_iter = document.get_end_iter()
        return document.get_text(start_iter, end_iter)


def set_file_line(column, cell, model, piter):
    """Set the value as file or line information."""
    file_path = model.get_value(piter, 0)
    mime_type = model.get_value(piter, 1)
    line_no = model.get_value(piter, 2)
    text = model.get_value(piter, 3)
    if text is None:
        cell.props.text = file_path
    else:
        cell.props.text = '%4s:  %s' % (line_no, text)


def on_file_lines_row_activated(treeview, path, view_column, plugin):
    """Open the file and jump to the line."""
    treestore = treeview.get_model()
    piter = treestore.get_iter(path)
    base_dir = treestore.get_value(piter, 4)
    path = treestore.get_value(piter, 0)
    if base_dir is None or path is None:
        # There is not enough information to open a document.
        return
    uri = 'file://%s' % os.path.abspath(os.path.join(base_dir, path))
    line_no = treestore.get_value(piter, 2) - 1
    if line_no < 0:
        line_no = 0
    plugin.activate_open_doc(uri, jump_to=line_no)


def setup_file_lines_view(file_lines_view, plugin, column_title):
    """Setup a TreeView to displau files and their lines."""
    treestore = gtk.TreeStore(
        gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_INT,
        gobject.TYPE_STRING, gobject.TYPE_STRING)
    treestore.append(None, ('', None, 0, None, None))
    column = gtk.TreeViewColumn(column_title)
    cell = gtk.CellRendererPixbuf()
    cell.set_property('stock-size', gtk.ICON_SIZE_MENU)
    column.pack_start(cell, False)
    column.add_attribute(cell, 'icon-name', 1)
    cell = gtk.CellRendererText()
    column.pack_start(cell, False)
    column.set_cell_data_func(cell, set_file_line)
    file_lines_view.set_model(treestore)
    file_lines_view.append_column(column)
    file_lines_view.set_search_column(0)
    file_lines_view.connect(
        'row-activated', on_file_lines_row_activated, plugin)
