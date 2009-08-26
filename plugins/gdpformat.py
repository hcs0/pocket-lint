# Copyright (C) 2009 - Curtis Hovey <sinzui.is at verizon.net>
"""Text formatting features for the edit menu."""

__metaclass__ = type

__all__ = [
    'FormatPlugin',
    ]


from gettext import gettext as _

import gedit
import gtk

from gdp.format import Formatter


menu_xml = """
<ui>
  <menubar name="MenuBar">
    <menu name="EditMenu" action="Edit">
      <placeholder name="EditOps_6">
          <menu name="FormatMenu" action="Format">
            <menuitem name="RewrapText" action="RewrapText"/>
            <menuitem name="FixLineEnding" action="FixLineEnding"/>
            <menuitem name="QuoteLines" action="QuoteLines"/>
            <menuitem name="SortImports" action="SortImports"/>
            <menuitem name="SingleLine" action="SingleLine"/>
            <menuitem name="REReplace" action="REReplace"/>
          </menu>
      </placeholder>
    </menu>
  </menubar>
</ui>
"""


class FormatPlugin(gedit.Plugin):
    """Plugin for formatting code."""
    # This is a new-style class that call and old-style __init__().
    # pylint: disable-msg=W0233

    @property
    def _actions(self):
        """Return a list of action tuples.

        (name, stock_id, label, accelerator, tooltip, callback)
        """
        return  [
            ('Format', None, _('_Format'), None, None, None),
            ('RewrapText', None, _("Rewrap _text"), None,
                _("Rewrap the text to 78 characters."),
                self.formatter.rewrap_text),
            ('FixLineEnding', None, _("Fix _line endings"), None,
                _('Remove trailing whitespace and use newline endings.'),
                self.formatter.newline_ending),
            ('QuoteLines', None, _("_Quote lines"), None,
                _("Format the text as a quoted email."),
                self.formatter.quote_lines),
            ('SortImports', None, _("Sort _imports"), None,
                _('Sort and wrap imports.'),
                self.formatter.sort_imports),
            ('SingleLine', None, _("_Single line"), None,
                _("Format the text as a single line."),
                self.formatter.single_line),
            ('REReplace', None, _("Regular _expression line replace"), None,
                _("Reformat each line using a regular expression."),
                self.formatter.re_replace),
            ]

    def __init__(self):
        """Initialize the plugin the whole Gedit application."""
        gedit.Plugin.__init__(self)
        self.window = None

    def activate(self, window):
        """Activate the plugin in the current top-level window.

        Add 'Format' to the edit menu and create a Formatter.
        """
        self.window = window
        self.formatter = Formatter(window)
        self.action_group = gtk.ActionGroup("FormatActions")
        self.action_group.add_actions(self._actions)
        manager = self.window.get_ui_manager()
        manager.insert_action_group(self.action_group, 1)
        self.ui_id = manager.add_ui_from_string(menu_xml)

    def deactivate(self, window):
        """Deactivate the plugin in the current top-level window."""
        manager = self.window.get_ui_manager()
        manager.remove_ui(self.ui_id)
        manager.remove_action_group(self.action_group)
        manager.ensure_update()
        self.ui_id = None
        self.action_group = None
        self.formatter = None
        self.window = None

    def update_ui(self, window):
        """Toggle the plugin's sensativity in the top-level window.

        This plugin is always active.
        """
        pass

    # Callbacks.
