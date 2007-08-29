# Copyright (C) 2007 - Curtis Hovey <sinzui.is at verizon.net>
"""GDP test helpers functions for setting up date."""

__metaclass__ = type


__ALL__ = ['get_document',
           'get_sourcebuffer',
           'get_window']


from gettext import gettext as _
import gtk
from gtksourceview import SourceBuffer, SourceLanguagesManager

import gedit


def get_sourcebuffer(file_path, mime_type='text/plain'):
    """return a gtk.TextBuffer for the provided file_path."""
    language_manager = SourceLanguagesManager()
    language = language_manager.get_language_from_mime_type(mime_type)
    try:
        source_file = open(file_path)
        text = ''.join(source_file.readlines())
    except IOError:
        raise ValueError, _(u'%s cannot be read' % file_path)
    else:
        source_file.close()
    source_buffer = SourceBuffer()
    source_buffer.set_language(language)
    source_buffer.set_text(text)
    return source_buffer


def get_document(file_path, mime_type='text/plain'):
    """Return a gedit.Document for the provided file_path."""
    language_manager = SourceLanguagesManager()
    language = language_manager.get_language_from_mime_type(mime_type)
    try:
        source_file = open(file_path)
        text = ''.join(source_file.readlines())
    except IOError:
        raise ValueError, _(u'%s cannot be read' % file_path)
    else:
        source_file.close()
    doc = gedit.Document()
    doc.set_language(language)
    doc.set_text(text)
    return doc


def get_window(file_path, document=None):
    """Return a gedit.Window with the document loaded from file_path.
    
    If file_path is None and document is not None, the provided document
    will be used with the window.
    """
    if file_path:
        document = get_document(file_path)
    elif not document:
        document = gedit.Document()
    else:
        # Use the provided document.
        pass
    view = gedit.View(document)
    scrolled_window = gtk.ScrolledWindow()
    scrolled_window.add(view)
    view.set_size_request(300, 250)
    window = gedit.Window()
    window.add(scrolled_window)
    window.connect("destroy", gtk.main_quit)
    window.resize(300, 250)
    window.show_all()
    return window, view, document

