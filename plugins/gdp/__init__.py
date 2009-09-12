# Copyright (C) 2009 - Curtis Hovey <sinzui.is at verizon.net>
# This software is licensed under the GNU General Public License version 2
# (see the file COPYING).
"""GDP Gedit Developer Plugins."""

__metaclass__ = type

__all__ = [
    'PluginMixin',
    ]


import mimetypes
import os

import gobject
import gtk


# Initialise the mimetypes for document type inspection.
mimetypes.init()


class GDPWindow:
    """Decorate a `GeditWindow` with GDP state"""

    def __init__(self, window, controller, plugin):
        self.window = window
        self.controller = controller
        self.ui_id = None
        if plugin.action_group_name is None:
            return
        self.action_group = gtk.ActionGroup(plugin.action_group_name)
        self.action_group.set_translation_domain('gedit')
        self.action_group.add_actions(plugin.actions(controller))
        manager = self.window.get_ui_manager()
        manager.insert_action_group(self.action_group, -1)
        self.ui_id = manager.add_ui_from_string(plugin.menu_xml)

    def deactivate(self):
        """Deactivate the plugin for the window."""
        if self.ui_id is None:
            return
        manager = self.window.get_ui_manager()
        manager.remove_ui(self.ui_id)
        manager.remove_action_group(self.action_group)
        manager.ensure_update()


class PluginMixin:
    """Provide common features to plugins"""

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
            jump_to = jump_to or 0
            self.window.create_tab_from_uri(uri, None, jump_to, False, False)
            self.window.get_active_view().scroll_to_cursor()

    def activate_open_doc(self, uri, jump_to=None):
        """Activate (or open) a document and jump to the line number."""
        self.open_doc(uri, jump_to)
        self.window.set_active_tab(self.window.get_tab_from_uri(uri))
        if jump_to is not None:
            self.window.get_active_document().goto_line(jump_to)
            self.window.get_active_view().scroll_to_cursor()

    @property
    def active_document(self):
        """The active document in the window."""
        return self.window.get_active_document()

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
    icon = model.get_value(piter, 1)
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
