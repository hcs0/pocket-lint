"""SyntaxCompleterPlugin enabled word and symbol completion."""

# Copyright (C) 2007 - Curtis Hovey <sinzui.is at verizon.net>
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
