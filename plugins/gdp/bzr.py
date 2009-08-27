# Copyright (C) 2009 - Curtis Hovey <sinzui.is at verizon.net>
"""Bazaar integration."""

import mimetypes
import os

from bzrlib import workingtree


__all__  = [
    'open_changed_files',
    ]


class BzrProject:
    """View and manage a bazaar branch."""

    def __init__(self, gedit, window):
        self.gedit = gedit
        self.window = window
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

    def get_working_tree(self):
        """Return the working tree for the working directory or document"""
        file_path = self.window.get_active_document().get_uri_for_display()
        if file_path is None:
            cwd = os.getcwd()
        else:
            cwd = os.path.dirname(file_path)
        working_tree, relpath = workingtree.WorkingTree.open_containing(cwd)
        return working_tree

    def open_changed_files(self, data):
        """Open modified and added files in the bzr branch."""
        # This should read the browser root or use current doc.
        working_tree = self.get_working_tree()
        base_dir = working_tree.basedir
        basis_tree = working_tree.basis_tree()
        try:
            working_tree.lock_read()
            basis_tree.lock_read()
            changes = working_tree.iter_changes(basis_tree, False, None,
                require_versioned=False, want_unversioned=False)
        finally:
            working_tree.unlock()
            basis_tree.unlock()
        for change in changes:
            # change is: (file_id, paths, content_change, versioned,
            #             parent_id, name, kind, executable)
            # paths is (previous_path, current_path)
            tree_file_path = change[1][1]
            uri = 'file://%s' % os.path.join(base_dir, tree_file_path)
            self.open_doc(uri)

