# Copyright (C) 2007 - Curtis Hovey <sinzui.is at verizon.net>
"""GDP test helpers functions for setting up date.

This module is larger than it appears. It represents the fake Gedit
classes, methods, and functions generated from the Gedit defs and
overrides.
"""

__metaclass__ = type


__ALL__ = ['get_window']


import gedit


def get_window(file_path):
    """Return a gedit.Window with the document loaded from file_path.
    
    If file_path is None and document is not None, the provided document
    will be used with the window.
    """
    window = gedit.app_get_default().create_window()
    view = window.get_active_view()
    document = window.get_active_document()
    if file_path:
        document.load(file_path, None, 0, False)
    window.show_all()
    return window, view, document

