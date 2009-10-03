# Copyright (C) 2009 - Curtis Hovey <sinzui.is at verizon.net>
# This software is licensed under the GNU General Public License version 2
# (see the file COPYING).
"""Bazaar project management and integration."""

__metaclass__ = type

__all__ = [
    'BazaarProjectPlugin',
    ]

from gettext import gettext as _

import gobject
import gedit

from gdp import GDPWindow
from gdp.bzr import BzrProject


gobject.signal_new(
    'bzr-branch-open', gedit.Window, gobject.SIGNAL_RUN_LAST,
    gobject.TYPE_NONE, (gobject.TYPE_STRING, ))


class BazaarProjectPlugin(gedit.Plugin):
    """Plugin for formatting code."""

    action_group_name = 'GDPProjectActions'
    menu_path = '/MenuBar/ProjectMenu/ProjectOps_1'
    menu_xml = """
        <ui>
          <menubar name="MenuBar">
            <menu action="ProjectMenu">
              <placeholder name="ProjectOps_1">
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
                <menuitem action="SendMerge"/>
                <separator />
                <menuitem action="InitBranch"/>
                <menuitem action="BranchBranch"/>
                <menuitem action="CheckoutBranch"/>
                <separator />
                <menuitem action="Preferences"/>
              </placeholder>
            </menu>
          </menubar>
        </ui>
        """

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
        'SendMerge',
        'ShowAnnotations',
        'ShowConflicts',
        'ShowInfo',
        'ShowStatus',
        'ShowTags',
        'VisualiseBranch',
        ]

    def actions(self, bzr):
        """Return a list of action tuples.

        (name, stock_id, label, accelerator, tooltip, callback)
        """
        return  [
            ('ProjectMenu', None, _('_Project'), None, None, None),
            ('OpenUncommittedFiles', None, _("Open _uncommitted files"), None,
                _("Open uncommitted in the bzr branch."),
                bzr.open_uncommitted_files),
            ('OpenChangedFilesFromParent', None, _("_Open diverged files"),
                '<Shift><Control>O',
                _("Open files that have diverged from the parent."),
                bzr.open_changed_files_from_parent),
            ('OpenChangedFilesToPush', None, _("Open unpushed files"),
                None, _("Open changed files that have not been pushed."),
                bzr.open_changed_files_to_push),
            ('DiffUncommittedChanges', None, _("_Diff uncommitted changes"),
                'F5', _("Create a diff of the uncommitted changes."),
                bzr.diff_uncommited_changes),
            ('DiffChangesFromParent', None, _("Diff changes from _parent"),
                '<Shift>F5',
                 _("Create a diff of the changes from the parent tree."),
                bzr.diff_changes_from_parent),
            ('DiffChangesToPush', None, _("Diff changes to push"),
                None, _("Create a diff of the changes from the push tree."),
                bzr.diff_changes_to_push),
            ('ShowAnnotations', None, _("Show _annotations"),
                None, _("Show the revision annotations of the current file."),
                bzr.show_annotations),
            ('VisualiseBranch', None, _("_Visualise branch"),
                None, _("Graphically visualise this branch.."),
                bzr.visualise_branch),
            ('ShowInfo', None, _("Show _info"),
                None,
                _("Show information about the working tree, branch "
                  "or repository."),
                bzr.show_info),
            ('ShowStatus', None, _("Show _status"),
                None, _("Show the status of the working tree."),
                bzr.show_status),
            ('ShowConflicts', None, _("Show co_nflicts"),
                None, _("Show the conflicts in the working tree."),
                bzr.show_conflicts),
            ('ShowTags', None, _("Show _tags"),
                None, _("Show the tags in the branch."),
                bzr.show_tags),
            ('CommitChanges', None, _("_Commit changes"),
                '<Control><Alt><Super>C',
                _("Commit the changes in the working tree."),
                bzr.commit_changes),
            ('MergeChanges', None, _("_Merge changes"),
                None,
                _("Merge changes from another branch into the working tree."),
                bzr.merge_changes),
            ('PushChanges', None, _("_Push changes"),
                None, _("Push the changes in the working tree."),
                bzr.push_changes),
            ('SendMerge', None, _("_Send merge directive"),
                None,
                _("Mail or create a merge-directive for submitting changes."),
                bzr.send_merge),

            ('InitBranch', None, _("_Initialise branch"),
                None, _("Make a directory into a versioned branch."),
                bzr.initialise_branch),
            ('BranchBranch', None, _("_Branch branch"),
                None, _("Create a new branch that is a copy of an "
                         "existing branch."), bzr.branch_branch),
            ('CheckoutBranch', None, _("_Checkout branch"),
                None, _("Create a new checkout of an existing branch."),
                bzr.checkout_branch),
            ('Preferences', None, _("_Preferences"),
                None, _("Set your global bazaar preferences."),
                bzr.preferences),
            ]

    def __init__(self):
        """Initialize the plugin for the Gedit application."""
        gedit.Plugin.__init__(self)
        self.windows = {}

    def activate(self, window):
        """Activate the plugin in the current top-level window.

        Add 'Project' to the main menu and create a BzrProject.
        """
        self.windows[window] = GDPWindow(window, BzrProject(window), self)
        # Moved the menu to a less surprising position.
        manager = window.get_ui_manager()
        menubar = manager.get_widget('/MenuBar')
        project_menu = manager.get_widget('/MenuBar/ProjectMenu')
        menubar.remove(project_menu)
        menubar.insert(project_menu, 5)

    def deactivate(self, window):
        """Deactivate the plugin in the current top-level window."""
        self.windows[window].deactivate()
        del self.windows[window]

    def update_ui(self, window):
        """Toggle the plugin's sensativity in the top-level window."""
        gdp_window = self.windows[window]
        gdp_window.controller.set_working_tree()
        if gdp_window.controller.working_tree is None:
            self.toggle_tree_menus(gdp_window, False)
        else:
            self.toggle_tree_menus(gdp_window, True)
            gdp_window.window.emit(
                'bzr-branch-open', gdp_window.controller.working_tree.basedir)

    def toggle_tree_menus(self, gdp_window, sensitive):
        """Enable or disable the menu items that require a working tree."""
        manager = gdp_window.window.get_ui_manager()
        for name in self.tree_actions:
            path = '%s/%s' % (self.menu_path, name)
            manager.get_action(path).props.sensitive = sensitive
        if not gdp_window.controller.has_bzr_gtk:
            sensitive = False
        for name in self.bzr_gtk_actions:
            path = '%s/%s' % (self.menu_path, name)
            manager.get_action(path).props.sensitive = sensitive
