# Copyright (C) 2009 - Curtis Hovey <sinzui.is at verizon.net>
"""Text formatting features for the edit menu."""

__metaclass__ = type

__all__ = [
    'FormatPlugin',
    ]


from gettext import gettext as _

import gedit

from gdp import GDPWindow
from gdp.format import Formatter


class FormatPlugin(gedit.Plugin):
    """Plugin for formatting code."""

    action_group_name = 'GDPFormatActions'
    menu_xml = """
        <ui>
          <menubar name="MenuBar">
            <menu name='EditMenu' action='Edit'>
              <placeholder name="GEPEdit1">
                  <menu action="GDPFormatMenu">
                    <menuitem action="RewrapText"/>
                    <menuitem action="FixLineEnding"/>
                    <menuitem action="TabsToSpaces"/>
                    <menuitem action="QuoteLines"/>
                    <menuitem action="SortImports"/>
                    <menuitem action="SingleLine"/>
                    <menuitem action="REReplace"/>
                    <menuitem action="ReformatDoctest"/>
                  </menu>
              </placeholder>
            </menu>
            <menu name='ToolsMenu' action='Tools'>
              <placeholder name="GDPTools1">
                <menuitem action="CheckProblems"/>
              </placeholder>
            </menu>
          </menubar>
        </ui>
        """

    @property
    def actions(self):
        """Return a list of action tuples.

        (name, stock_id, label, accelerator, tooltip, callback)
        """
        return  [
            ('GDPFormatMenu', None, _('_Format'), None, None, None),
            ('RewrapText', None, _("Rewrap _text"), None,
                _("Rewrap the text to 78 characters."),
                self.formatter.rewrap_text),
            ('FixLineEnding', None, _("Fix _line endings"), None,
                _('Remove trailing whitespace and use newline endings.'),
                self.formatter.newline_ending),
            ('TabsToSpaces', None, _("Convert t_abs to spaces"), None,
                _('Convert tabs to spaces using the preferred tab size.'),
                self.formatter.tabs_to_spaces),
            ('QuoteLines', None, _("_Quote lines"), '<Alt>Q',
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
            ('ReformatDoctest', None, _("Reformat _doctest"), None,
                _("Reformat the doctest."),
                self.formatter.reformat_doctest),
            ('CheckProblems', None, _("C_heck syntax and style"), 'F3',
                _("Check syntax and style problems."),
                self.formatter.check_style),
            ]

    def __init__(self):
        """Initialize the plugin the whole Gedit application."""
        gedit.Plugin.__init__(self)
        self.windows = {}

    def activate(self, window):
        """Activate the plugin in the current top-level window.

        Add 'Format' to the edit menu and create a Formatter.
        """
        self.windows[window] = GDPWindow(window)
        self.formatter = Formatter(window)
        self.windows[window].activate(self)

    def deactivate(self, window):
        """Deactivate the plugin in the current top-level window."""
        self.windows[window].deactivate()
        del self.windows[window]

    def update_ui(self, window):
        """Toggle the plugin's sensativity in the top-level window.

        This plugin is always active.
        """
        pass
