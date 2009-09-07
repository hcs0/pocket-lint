# Copyright (C) 2007-2009 - Curtis Hovey <sinzui.is at verizon.net>
# This software is licensed under the GNU General Public License version 2
# (see the file COPYING).
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
    if file_path:
        window.get_child().remove_page(0)
        window.create_tab_from_uri(file_path, None, 0, False, True)
    view = window.get_active_view()
    document = window.get_active_document()
    window.show_all()
    return window, view, document
