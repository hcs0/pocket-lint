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

import gedit

from gdp.syntaxcompleter import SyntaxController


class SyntaxCompleterPlugin(gedit.Plugin):
    """Automatically complete words from the list of words in the document."""

    def __init__(self):
        """Initialize the plugin the whole Gedit application."""
        gedit.Plugin.__init__(self)
        self.window = None
        self.controller = None

    def activate(self, window):
        """Activate the plugin in the current top-level window.
        
        Add a SyntaxControler to every view.
        """
        self.window = window
        window.connect('tab-added', self.on_tab_added)
        for view in self.window.get_views():
            if isinstance(view, gedit.View) and not self.hasController(view):
                view._syntax_controller = SyntaxController(view)

        self.update_ui(window)

    def deactivate(self, window):
        """Deactivate the plugin in the current top-level window.
        
        Remove the SyntaxControler from every view.
        """
        for view in window.get_views():
            if isinstance(view, gedit.View) and self.hasController(view):
                view._syntax_controller.deactivate()
                view._syntax_controller = None
                del view._syntax_controller

        self.window = None
        self.controller = None

    def update_ui(self, window):
        """Toggle the plugin's sensativity in the top-level window.
        
        Set the current controler.
        """
        view = window.get_active_view()
        if isinstance(view, gedit.View) and self.hasController(view):
            self.controller = view._syntax_controller
        else:
            self.controller = None

    def hasController(self, view):
        """Return True when the view has a SyntaxControler."""
        return hasattr(view, '_syntax_controller') and view._syntax_controller

    # Callbacks    

    def on_tab_added(self, window, tab):
        """Create a new SyntaxController for this tab."""
        view = tab.get_view()
        if isinstance(view, gedit.View) and not self.hasController(view):
            view._syntax_controller = SyntaxController(view)
            self.update_ui(window)

