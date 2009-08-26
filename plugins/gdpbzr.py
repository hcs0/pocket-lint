# Copyright (C) 2009 - Curtis Hovey <sinzui.is at verizon.net>
"""Bazaar project management and integration."""

__metaclass__ = type

__all__ = [
    'BazaarProjectPlugin',
    ]


from gettext import gettext as _

import gedit
import gtk

from gdp.bzr import BzrProject


menu_xml = """
<ui>
  <menubar name="MenuBar">
    <menu name="ProjectMenu" action="Project">
      <placeholder name="ProjectOps_1">
        <menuitem name="OpenChangedFiles" action="OpenChangedFiles"/>
      </placeholder>
    </menu>
  </menubar>
</ui>
"""


class BazaarProjectPlugin(gedit.Plugin):
    """Plugin for formatting code."""
    # This is a new-style class that call and old-style __init__().
    # pylint: disable-msg=W0233

    @property
    def _actions(self):
        """Return a list of action tuples.

        (name, stock_id, label, accelerator, tooltip, callback)
        """
        return  [
            ('Project', None, _('_Project'), None, None, None),
            ('OpenChangedFiles', None, _("_Open changed files"), None,
                _("Open modified and add files in the bzr branch"),
                self.bzr.open_changed_files),
            ]

    def __init__(self):
        """Initialize the plugin the whole Gedit application."""
        gedit.Plugin.__init__(self)
        self.window = None

    def activate(self, window):
        """Activate the plugin in the current top-level window.

        Add 'Project' to the main menu and create a BzrProject.
        """
        self.window = window
        self.bzr = BzrProject(window)
        self.action_group = gtk.ActionGroup("ProjectActions")
        self.action_group.add_actions(self._actions)
        manager = self.window.get_ui_manager()
        manager.insert_action_group(self.action_group, 2)
        self.ui_id = manager.add_ui_from_string(menu_xml)

    def deactivate(self, window):
        """Deactivate the plugin in the current top-level window."""
        manager = self.window.get_ui_manager()
        manager.remove_ui(self.ui_id)
        manager.remove_action_group(self.action_group)
        manager.ensure_update()
        self.ui_id = None
        self.action_group = None
        self.bzr = None
        self.window = None

    def update_ui(self, window):
        """Toggle the plugin's sensativity in the top-level window."""
        pass

    # Callbacks.