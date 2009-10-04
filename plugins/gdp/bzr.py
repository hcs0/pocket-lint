# Copyright (C) 2009 - Curtis Hovey <sinzui.is at verizon.net>
# This software is licensed under the GNU General Public License version 2
# (see the file COPYING).
"""Bazaar integration."""

import os
from StringIO import StringIO

import gtk

from bzrlib import workingtree
from bzrlib.branch import Branch
from bzrlib.errors import NotBranchError, NoWorkingTree
from bzrlib.revisionspec import RevisionSpec

try:
    from bzrlib.plugin import load_plugins
    load_plugins()
    from bzrlib.plugins.gtk.annotate.config import GAnnotateConfig
    from bzrlib.plugins.gtk.commit import CommitDialog
    from bzrlib.plugins.gtk.conflicts import ConflictsDialog
    from bzrlib.plugins.gtk.dialog import error_dialog
    from bzrlib.plugins.gtk.initialize import InitDialog
    from bzrlib.plugins.gtk.merge import MergeDialog
    from bzrlib.plugins.gtk.push import PushDialog
    from bzrlib.plugins.gtk.status import StatusWindow
    HAS_BZR_GTK = True
except ImportError:
    HAS_BZR_GTK = False

from gdp import PluginMixin


__all__ = [
    'BzrProject',
    ]


class BzrProject(PluginMixin):
    """View and manage a bazaar branch."""

    def __init__(self, window, working_tree=None):
        self.window = window
        self.working_tree = working_tree or self.set_working_tree()

    @property
    def has_bzr_gtk(self):
        """Is bzr-gtk available?"""
        return HAS_BZR_GTK

    def set_working_tree(self):
        """Return the working tree for the working directory or document"""
        doc = self.active_document
        if doc is None:
            self.working_tree = None
            return
        file_path = doc.get_uri_for_display()
        if file_path is None:
            cwd = os.getcwd()
        else:
            cwd = os.path.dirname(file_path)
        try:
            working_tree, relpath = workingtree.WorkingTree.open_containing(
                cwd)
            self.working_tree = working_tree
            self.relpath = relpath
        except (NotBranchError, NoWorkingTree):
            self.working_tree = None

    def _get_branch_revision_tree(self, uri):
        """Return a branch tree for a revision."""
        if uri is None:
            return None
        revision = RevisionSpec.from_string('branch:%s' % uri)
        return revision.as_tree(self.working_tree.branch)

    @property
    def _push_tree(self):
        """The push location tree."""
        return self._get_branch_revision_tree(
            self.working_tree.branch.get_push_location())

    @property
    def _parent_tree(self):
        """The parent location tree."""
        return self._get_branch_revision_tree(
            self.working_tree.branch.get_parent())

    def open_changed_files(self, other_tree):
        """Open files in the bzr branch."""
        if other_tree is None:
            return
        try:
            self.working_tree.lock_read()
            other_tree.lock_read()
            changes = self.working_tree.iter_changes(
                other_tree, False, None,
                require_versioned=False, want_unversioned=False)
            for change in changes:
                # change is: (file_id, paths, content_change, versioned,
                #             parent_id, name, kind, executable)
                # paths is (previous_path, current_path)
                tree_file_path = change[1][1]
                if tree_file_path is None:
                    continue
                base_dir = self.working_tree.basedir
                uri = 'file://%s' % os.path.join(base_dir, tree_file_path)
                self.open_doc(uri)
        finally:
            self.working_tree.unlock()
            other_tree.unlock()

    def open_uncommitted_files(self, data):
        """Open modified and added files in the bzr branch."""
        self.open_changed_files(self.working_tree.basis_tree())

    def open_changed_files_to_push(self, data):
        """Open the changed files in the branch that not been pushed."""
        self.open_changed_files(self._push_tree)

    def open_changed_files_from_parent(self, data):
        """Open the changed files that diverged from the parent branch."""
        self.open_changed_files(self._parent_tree)

    @property
    def diff_file_path(self):
        """The path of the diff file."""
        return os.path.join(self.working_tree.basedir, '_diff.diff')

    def _diff_tree(self, another_tree):
        """Diff the working tree against an anoter tree."""
        if another_tree is None:
            return
        from bzrlib.plugins.gtk.diff import DiffWindow
        window = DiffWindow()
        window.set_diff("Working Tree", self.working_tree, another_tree)
        window.props.title = "Diff branch - gedit"
        window.show()
        with open(self.diff_file_path, 'w') as diff_file:
            diff_buffer = window.diff.diff_view.buffer
            start_iter = diff_buffer.get_start_iter()
            end_iter = diff_buffer.get_end_iter()
            diff_file.write(diff_buffer.get_text(start_iter, end_iter))

    def diff_uncommited_changes(self, data):
        """Create a diff of uncommitted changes."""
        self._diff_tree(self.working_tree.basis_tree())

    def diff_changes_from_parent(self, data):
        """Create a diff of changes from the parent tree."""
        self._diff_tree(self._parent_tree)

    def diff_changes_to_push(self, data):
        """Create a diff of changes to the push tree."""
        self._diff_tree(self._push_tree)

    def commit_changes(self, data):
        """Commit the changes in the working tree."""
        try:
            self.working_tree.lock_write()
            dialog = CommitDialog(self.working_tree, self.window)
            dialog.props.title = "Commit changes - gedit"
            response = dialog.run()
            if response != gtk.RESPONSE_NONE:
                dialog.hide()
                dialog.destroy()
        finally:
            self.working_tree.unlock()

    def show_info(self, data):
        """Show information about the working tree, branch or repository."""
        # XXX sinzui 2009-10-03 bug 107169: seahorse dbus often fails to
        # connect on a cold system. This should not kill the module.
        from bzrlib.plugins.gtk.olive.info import InfoDialog
        dialog = InfoDialog(self.working_tree.branch)
        dialog.display()
        dialog.window.run()

    def show_status(self, data):
        """Show the status of the working tree."""
        base_dir = self.working_tree.basedir
        window = StatusWindow(self.working_tree, base_dir, None)
        window.props.title = "Branch status - gedit"
        window.show()

    def show_conflicts(self, data):
        """Show the merge, revert, or pull conflicts in the working tree."""
        dialog = ConflictsDialog(self.working_tree)
        dialog.props.title = "Branch conflicts - gedit"
        response = dialog.run()
        dialog.hide()
        dialog.destroy()

    def show_missing(self, data):
        """Show unmerged/unpulled revisions between two branches."""
        from bzrlib.plugins.gtk.missing import MissingWindow
        parent_location = self.working_tree.branch.get_parent()
        if parent_location is None:
            message = _("Nothing to do; this branch does not have a parent.")
            dialog = gtk.MessageDialog(
                type=gtk.MESSAGE_INFO, buttons=gtk.BUTTONS_CLOSE,
                message_format=message)
            dialog.run()
            dialog.destroy()
            return
        parent_branch = Branch.open_containing(parent_location)[0]
        self.working_tree.branch.lock_read()
        try:
            parent_branch.lock_read()
            try:
                window = MissingWindow(
                    self.working_tree.branch, parent_branch)
                window.run()
            finally:
                parent_branch.unlock()
        finally:
            self.working_tree.branch.unlock()

    def show_tags(self, data):
        """Show the tags in the branch."""
        # XXX sinzui 2009-10-03 bug 107169: seahorse dbus often fails to
        # connect on a cold system. This should not kill the module.
        from bzrlib.plugins.gtk.tags import TagsWindow
        window = TagsWindow(self.working_tree.branch, self.window)
        window.props.title = "Branch tags - gedit"
        window.show()

    def show_annotations(self, data):
        """Show the annotated revisions of the file."""
        document = self.window.get_active_document()
        file_path = document.get_uri_for_display()
        if file_path is None:
            return
        base_dir = self.working_tree.basedir
        file_path = file_path.replace(base_dir, '')
        file_id = self.working_tree.path2id(file_path)
        if file_id is None:
            return
        # XXX sinzui 2009-10-03 bug 107169: seahorse dbus often fails to
        # connect on a cold system. This should not kill the module.
        from bzrlib.plugins.gtk.annotate.gannotate import GAnnotateWindow
        window = GAnnotateWindow(parent=self.window)
        window.props.title = "Annotate (" + file_path +") - gedit"
        GAnnotateConfig(window)
        window.show()
        branch = self.working_tree.branch

        def destroy_window(window):
            branch.unlock()
            self.working_tree.unlock()

        window.connect("destroy", destroy_window)
        branch.lock_read()
        self.working_tree.lock_read()
        window.annotate(self.working_tree, branch, file_id)

    def visualise_branch(self, data):
        """Visualise the tree."""
        limit = None
        branch = self.working_tree.branch
        revisions = [branch.last_revision()]
        # XXX sinzui 2009-10-03 bug 107169: seahorse dbus often fails to
        # connect on a cold system. This should not kill the module.
        from bzrlib.plugins.gtk.viz import BranchWindow
        window = BranchWindow(branch, revisions, limit)
        window.props.title = "Visualise branch - gedit"
        window.show()

    def merge_changes(self, data):
        """Merge changes from another branch into te working tree."""
        branch = self.working_tree.branch
        old_tree = branch.repository.revision_tree(branch.last_revision())
        delta = self.working_tree.changes_from(old_tree)
        if (len(delta.added) or len(delta.removed)
            or len(delta.renamed) or len(delta.modified)):
            error_dialog(
                _('There are local changes in the branch'),
                 _('Commit or revert the changes before merging.'))
        else:
            parent_branch_path = branch.get_parent()
            dialog = MergeDialog(
                self.working_tree, self.relpath, parent_branch_path)
            dialog.props.title = "Merge changes - gedit"
            response = dialog.run()
            dialog.destroy()

    def push_changes(self, data):
        """Push the changes in the working tree."""
        branch = self.working_tree.branch
        dialog = PushDialog(branch.repository, branch.last_revision(), branch)
        response = dialog.run()
        dialog.hide()
        dialog.destroy()

    def send_merge(self, data):
        """Mail or create a merge-directive for submitting changes."""
        from bzrlib.plugins.gtk.mergedirective import SendMergeDirectiveDialog
        branch = self.working_tree.branch
        dialog = SendMergeDirectiveDialog(branch)
        dialog.props.title = "Send merge directive - gedit"
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            directive_file = StringIO()
            directive_file.writelines(dialog.get_merge_directive().to_lines())
            mail_client = branch.get_config().get_mail_client()
            mail_client.compose_merge_request(
                dialog.get_mail_to(), "[MERGE]", directive_file.getvalue())
        dialog.hide()
        dialog.destroy()

    def initialise_branch(self, data):
        """Make a directory into a versioned branch."""
        dialog = InitDialog(os.path.abspath(os.path.curdir))
        dialog.props.title = "Initialize branch - gedit"
        response = dialog.run()
        dialog.hide()
        dialog.destroy()

    def branch_branch(self, data):
        """Create a new branch that is a copy of an existing branch."""
        # XXX sinzui 2009-10-03 bug 107169: seahorse dbus often fails to
        # connect on a cold system. This should not kill the module.
        from bzrlib.plugins.gtk.branch import BranchDialog
        dialog = BranchDialog('')
        dialog.props.title = "Branch branch - gedit"
        response = dialog.run()
        dialog.hide()
        dialog.destroy()

    def checkout_branch(self, data):
        """Create a new checkout of an existing branch."""
        # XXX sinzui 2009-10-03 bug 107169: seahorse dbus often fails to
        # connect on a cold system. This should not kill the module.
        from bzrlib.plugins.gtk.checkout import CheckoutDialog
        dialog = CheckoutDialog('')
        dialog.props.title = "Checkout branch - gedit"
        response = dialog.run()
        dialog.hide()
        dialog.destroy()

    def preferences(self, data):
        """Bazaar preferences."""
        from bzrlib.plugins.gtk.preferences import PreferencesWindow
        dialog = PreferencesWindow()
        dialog.props.title = "Bazaar preferences - gedit"
        response = dialog.run()
        dialog.hide()
        dialog.destroy()
