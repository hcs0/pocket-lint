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
    #handler_ids = []

    def __init__(self):
        """Initialize the plugin the whole Gedit application."""
        gedit.Plugin.__init__(self)
        self.window = None
        self.controller = None
        self.language = None
        # XXX Sinzui 2007-07-26:
        # I do not this this is needed.
        self.signal_ids = {}

    def activate(self, window):
        """Activate the plugin in the current top-level window.
        
        Add a SyntaxControler to every view.
        """
        self.window = window
        self.setup_syntax_completer(window)
        window.connect('tab-added', self.on_tab_added)
        for view in self.window.get_views():
            if isinstance(view, gedit.View) and not self.has_controller(view):
                view._syntax_controller = SyntaxController(self, view)

        self.update_ui()

    def deactivate(self, window):
        """Deactivate the plugin in the current top-level window.
        
        Remove the SyntaxControler from every view.
        """
        #for (handler_id, view) in self.handler_ids:
        #    view.disconnect(handler_id)
        for view in self.window.get_views():
            if isinstance(view, gedit.View) and self.has_controller(view):
                view._syntax_controller.stop()
                view._syntax_controller = None

        self.window = None
        self.controler = None
        self.language = None

    def update_ui(self, window):
        """Toggle the plugin's sensativity in the top-level window.
        
        Set the current controler and language.
        """
        #self.setup_syntax_completer(window)
        view = self.window.get_active_view()
        if not view or not self.has_controller(view):
            return

        controller = view._syntax_controller
        if controller != self.controller:
            self.controller = controller

        if self.controller:
            self.language = self.controller.language_id
        else:
            self.language = None

    def has_controller(self, view):
        """Return True when the view has a SyntaxControler."""
        return hasattr(view, '_syntax_controller') and view._snytax_controller

    # Callbacks    
    def on_tab_added(self, window, tab):
        """Create a new SyntaxController for this tab."""
        view = tab.get_view()
        if isinstance(view, gedit.View) and not self.has_controller(view):
            view._syntax_controller = SyntaxController(self, view)

    def accelerator_activated(self, keyval, mod):
        """Activate the SyntaxView when the accelerator is called."""
        return self.current_controller.accelerator_activate(keyval, mod)

    # These methods maintain compatability with SnippetController
    # in snippets.

    def language_changed(self, controller):
        """Maps ui_changed to parent class."""
        self.update_ui(self.window)

    # XXX sinzui 2007-07-26:
    # Factor this out
    def setup_syntax_completer(self, window):
        """Setup the syntax completion in the view."""
        view = window.get_active_view()
        if view is not None:
            if getattr(view, 'syntax_completer', False) == False:
                doc = window.get_active_document()
                if doc.get_language() is not None:
                    language = doc.get_language().get_id()
                else:
                    language = None
                setattr(view, 'syntax_completer', SyntaxCompleter(language))
                handler_id = view.connect(
                    'key-press-event', view.syntax_completer.complete)
                self.handler_ids.append((handler_id, view))
