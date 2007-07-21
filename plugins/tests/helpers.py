# Copyright (C) 2007 - Curtis Hovey <sinzui.is at verizon.net>
"""GDP test helpers functions for setting up date."""

__metaclass__ = type


__ALL__ = ['get_gtk_textbuffer']


import gtk


def get_gtk_textbuffer(file_path):
    """return a gtk.TextBuffer for the provided file_path."""
    try:
        source_file = open(file_path)
        text = ''.join(source_file.readlines())
    except IOError:
        raise ValueError, _(u'%s cannot be read' % file_path)
    else:
        source_file.close()
    text_buffer = gtk.TextBuffer()
    text_buffer.set_text(text)
    return text_buffer

