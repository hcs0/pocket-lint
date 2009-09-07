"""SyntaxCompleterPlugin enabled word and symbol completion."""
# Copyright (C) 2007-2009 - Curtis Hovey <sinzui.is at verizon.net>
# This software is licensed under the GNU General Public License version 2
# (see the file COPYING).

__metaclass__ = type

__all__ = [
    'SyntaxCompleterPlugin',
    ]

import gedit

from gdp import GDPWindow
from gdp.syntaxcompleter import SyntaxController


class SyntaxCompleterPlugin(gedit.Plugin):
    """Automatically complete words from the list of words in the document."""

    action_group_name = None

    def __init__(self):
        """Initialize the plugin the whole Gedit application."""
        gedit.Plugin.__init__(self)
        self.windows = {}

    def activate(self, window):
        """Activate the plugin in the current top-level window.

        Add a SyntaxControler to every view.
        """
        self.windows[window] = GDPWindow(
            window, SyntaxController(window), self)
        self.update_ui(window)

    def deactivate(self, window):
        """Deactivate the plugin in the current top-level window.

        Remove the SyntaxControler from every view.
        """
        self.windows[window].controller.deactivate()
        self.windows[window].deactivate()
        del self.windows[window]

    def update_ui(self, window):
        """Toggle the plugin's sensativity in the top-level window.

        Set the current controler.
        """
        view = window.get_active_view()
        if isinstance(view, gedit.View):
            self.windows[window].controller.set_view(view)
            self.windows[window].controller.correct_language(
                window.get_active_document())
