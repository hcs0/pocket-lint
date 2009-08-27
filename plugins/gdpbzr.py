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
      <placeholder name="ProjectOpt1">
        <menuitem action="OpenUncommittedFiles"/>
        <menuitem action="OpenChangedFiledFromParent"/>
        <menuitem action="OpenChangedFiledToPush"/>
        <separator />
        <menuitem action="DiffUncommittedChanges"/>
      </placeholder>
    </menu>
  </menubar>
</ui>
"""

PROJECT_PATH = '/MenuBar/ProjectMenu/ProjectOpt1'


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
            ('OpenUncommittedFiles', None, _("Open _uncommitted files"), None,
                _("Open uncommitted in the bzr branch."),
                self.bzr.open_uncommitted_files),
            ('OpenChangedFiledFromParent', None, _("_Open diverged files"),
                '<Shift><Control>O',
                _("Open files that have diverged from the parent."),
                self.bzr.open_uncommitted_files),
            ('OpenChangedFiledToPush', None, _("_Open _unpushed files"),
                None, _("Open changed files that have not been pushed."),
                self.bzr.open_changed_files_to_push),
            ('DiffUncommittedChanges', None, _("_Diff uncommitted changes"),
                'F5', _("Create a diff of the uncommitted changes."),
                self.bzr.diff_uncommited_changes),
            ]

    tree_actions = [
        'OpenChangedFiledToPush',
        'OpenChangedFiledFromParent',
        'OpenUncommittedFiles',
        'DiffUncommittedChanges',
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
        self.bzr = BzrProject(gedit, window)
        self.bzr.set_working_tree()
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
        if self.window is window and self.bzr.working_tree is not None:
            return
        self.window = window
        self.bzr.window = window
        self.bzr.set_working_tree()
        if self.bzr.working_tree is None:
            self.toggle_tree_menus(False)
        else:
            self.toggle_tree_menus(True)

    def toggle_tree_menus(self, sensitive):
        """Enable or disable the menu items that require a working tree."""
        manager = self.window.get_ui_manager()
        for name in self.tree_actions:
            path = '%s/%s' % (PROJECT_PATH, name)
            manager.get_action(path).props.sensitive = sensitive
