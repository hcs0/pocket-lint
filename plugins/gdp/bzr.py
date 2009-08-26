# Copyright (C) 2009 - Curtis Hovey <sinzui.is at verizon.net>
"""Bazaar integration."""

from gettext import gettext as _


__all__  = [
    'open_changed_files',
    ]


class BzrProject:
    """View and manage a bazaar branch."""

    def __init__(self, window):
        self.window = window

    def open_changed_files(self, data):
        """Open modified and added files in the bzr branch."""
        pass
