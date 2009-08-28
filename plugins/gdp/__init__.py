"""GDP Gedit Developer Plugins."""

__metaclass__ = type

__all__  = [
    'PluginMixin',
    ]

import mimetypes


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
