"""Find matching text in multiple files."""

# Copyright (C) 2008 - Curtis Hovey <sinzui.is at verizon.net>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.

__metaclass__ = type

__all__ = [
    'FindPlugin',
    ]


from gettext import gettext as _

import gedit

from gdp import GDPWindow
from gdp.find import Finder


class FindPlugin(gedit.Plugin):
    """Find matching text in multiple files plugin."""
    # This is a new-style class that call and old-style __init__().
    # pylint: disable-msg=W0233

    action_group_name = 'GDPFindActions'
    menu_xml = """
        <ui>
          <menubar name="MenuBar">
            <menu name="SearchMenu" action='Search'>
              <menuitem action="FindFiles"/>
              <menuitem action="ReplaceFiles"/>
            </menu>
          </menubar>
        </ui>
        """

    @property
    def actions(self):
        """Return a list of action tuples.

        (name, stock_id, label, accelerator, tooltip, callback)
        """
        return [
            ('FindFiles', None, _('Find in files...'),
                '<Control><Shift>f', _('Fi_nd in files'),
                self.finder.show),
            ('ReplaceFiles', None, _('R_eplace in files...'),
                '<Control><Shift>h', _('Replace in files'),
                self.finder.show_replace),
            ]

    def __init__(self):
        """Initialize the plugin the whole Gedit application."""
        gedit.Plugin.__init__(self)
        self.windows = {}

    def activate(self, window):
        """Activate the plugin in the current top-level window.

        Add 'Find in files' to the menu.
        """
        self.windows[window]= GDPWindow(window)
        self.finder = Finder(gedit, window)
        self.windows[window].activate(self)

    def deactivate(self, window):
        """Deactivate the plugin in the current top-level window.

        Remove a 'Find in files' to the menu.
        """
        self.windows[window].deactivate()
        del self.windows[window]

    def update_ui(self, window):
        """Toggle the plugin's sensativity in the top-level window.

        'Find in files' is always active.
        """
        pass
