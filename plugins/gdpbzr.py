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
    <menu action="ProjectMenu">
      <placeholder name="ProjectOpt1">
        <menuitem action="OpenUncommittedFiles"/>
        <menuitem action="OpenChangedFilesFromParent"/>
        <menuitem action="OpenChangedFilesToPush"/>
        <separator />
        <menuitem action="DiffUncommittedChanges"/>
        <menuitem action="DiffChangesFromParent"/>
        <menuitem action="DiffChangesToPush"/>
        <separator />
        <menuitem action="ShowInfo"/>
        <menuitem action="ShowStatus"/>
        <menuitem action="ShowConflicts"/>
        <separator />
        <menuitem action="ShowTags"/>
        <menuitem action="ShowAnnotations"/>
        <menuitem action="VisualiseBranch"/>
        <separator />
        <menuitem action="CommitChanges"/>
        <menuitem action="MergeChanges"/>
        <menuitem action="PushChanges"/>
      </placeholder>
    </menu>
  </menubar>
</ui>
"""

PROJECT_PATH = '/MenuBar/ProjectMenu/ProjectOpt1'


class BazaarProjectPlugin(gedit.Plugin):
    """Plugin for formatting code."""

    @property
    def _actions(self):
        """Return a list of action tuples.

        (name, stock_id, label, accelerator, tooltip, callback)
        """
        return  [
            ('ProjectMenu', None, _('_Project'), None, None, None),
            ('OpenUncommittedFiles', None, _("Open _uncommitted files"), None,
                _("Open uncommitted in the bzr branch."),
                self.bzr.open_uncommitted_files),
            ('OpenChangedFilesFromParent', None, _("_Open diverged files"),
                '<Shift><Control>O',
                _("Open files that have diverged from the parent."),
                self.bzr.open_changed_files_from_parent),
            ('OpenChangedFilesToPush', None, _("Open unpushed files"),
                None, _("Open changed files that have not been pushed."),
                self.bzr.open_changed_files_to_push),
            ('DiffUncommittedChanges', None, _("_Diff uncommitted changes"),
                'F5', _("Create a diff of the uncommitted changes."),
                self.bzr.diff_uncommited_changes),
            ('DiffChangesFromParent', None, _("Diff changes from _parent"),
                '<Shift>F5',
                 _("Create a diff of the changes from the parent tree."),
                self.bzr.diff_changes_from_parent),
            ('DiffChangesToPush', None, _("Diff changes to push"),
                None, _("Create a diff of the changes from the push tree."),
                self.bzr.diff_changes_to_push),
            ('ShowAnnotations', None, _("Show _annotations"),
                None, _("Show the revision annotations of the current file."),
                self.bzr.show_annotations),
            ('VisualiseBranch', None, _("_Visualise branch"),
                None, _("Graphically visualise this branch.."),
                self.bzr.visualise_branch),
            ('ShowInfo', None, _("Show _info"),
                None,
                _("Show information about the working tree, branch "
                  "or repository."),
                self.bzr.show_info),
            ('ShowStatus', None, _("Show _status"),
                None, _("Show the status of the working tree."),
                self.bzr.show_status),
            ('ShowConflicts', None, _("Show co_nflicts"),
                None, _("Show the conflicts in the working tree."),
                self.bzr.show_conflicts),
            ('ShowTags', None, _("Show _tags"),
                None, _("Show the tags in the branch."),
                self.bzr.show_tags),
            ('CommitChanges', None, _("_Commit changes"),
                '<Control><Alt><Super>C',
                _("Commit the changes in the working tree."),
                self.bzr.commit_changes),
            ('MergeChanges', None, _("_Merge changes"),
                None,
                _("Merge changes from another branch into the working tree."),
                self.bzr.merge_changes),
            ('PushChanges', None, _("_Push changes"),
                None, _("Push the changes in the working tree."),
                self.bzr.push_changes),
            ]

    tree_actions = [
        'OpenChangedFilesToPush',
        'OpenChangedFilesFromParent',
        'OpenUncommittedFiles',
        'DiffUncommittedChanges',
        'DiffChangesFromParent',
        'DiffChangesToPush',
        ]

    bzr_gtk_actions = [
        'CommitChanges',
        'MergeChanges',
        'PushChanges',
        'ShowAnnotations',
        'ShowConflicts',
        'ShowInfo',
        'ShowStatus',
        'ShowTags',
        'VisualiseBranch',
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
        manager.insert_action_group(self.action_group, -1)
        self.ui_id = manager.add_ui_from_string(menu_xml)
        menubar = manager.get_widget('/MenuBar')
        project_menu = manager.get_widget('/MenuBar/ProjectMenu')
        menubar.remove(project_menu)
        menubar.insert(project_menu, 5)

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
        if not self.bzr.has_bzr_gtk:
            sensitive = False
        for name in self.bzr_gtk_actions:
            path = '%s/%s' % (PROJECT_PATH, name)
            manager.get_action(path).props.sensitive = sensitive
