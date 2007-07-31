# Copyright (C) 2007 - Curtis Hovey <sinzui.is at verizon.net>
"""GDP test helpers functions for setting up date."""

__metaclass__ = type


__ALL__ = ['get_sourcebuffer',
           'get_mock']


from gettext import gettext as _
from gtksourceview import SourceBuffer, SourceLanguagesManager

from gedit import Mock


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


def get_mock():
    """Return a mock gedit object.
    
    Store data in keys named after the class and the <class>_<methods>.
    """
    return Mock()
