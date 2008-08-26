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


import gedit
import gtk

#from gdp.find import FindController


ui_xml = """<ui>
  <menubar name="MenuBar">
    <menu name="SearchMenu" action="Search">
      <menuitem name="FindFiles" action="FindFiles"/>
    </menu>
  </menubar>
</ui>
"""


class FindPlugin(gedit.Plugin):
    """Find matching text in multiple files plugin."""
    # This is a new-style class that call and old-style __init__().
    # pylint: disable-msg=W0233

    def __init__(self):
        """Initialize the plugin the whole Gedit application."""
        gedit.Plugin.__init__(self)
        self.window = None

    def activate(self, window):
        """Activate the plugin in the current top-level window.

        Add 'Find in files' to the menu.
        """
        self.window = window
        self.action_group = gtk.ActionGroup("FindPluginActions")
        self.action_group.set_translation_domain('gedit')
        self.action_group.add_actions(
            [('FindFiles', None, _('Find i_n files...'),
             '<Control><Shift>f', _('Find in files'),
             self.on_find_files)])
        manager = self.window.get_ui_manager()
        manager.insert_action_group(self.action_group, -1)
        self.merge_id = manager.add_ui_from_string(ui_xml)

    def deactivate(self, window):
        """Deactivate the plugin in the current top-level window.

        Remove a 'Find in files' to the menu.
        """
        manager = self.window.get_ui_manager()
        manager.remove_ui(self.merge_id)
        manager.remove_action_group(self.action_group)
        manager.ensure_update()
        self.action_group = None
        self.window = None

    def update_ui(self, window):
        """Toggle the plugin's sensativity in the top-level window.

        'Find in files' is always active.
        """
        pass

    # Callbacks.

    def on_find_files(self, menu):
        """Show the 'find in files' pane."""

