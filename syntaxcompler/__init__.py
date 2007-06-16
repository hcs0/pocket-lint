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

from syntaxcompleter import SyntaxCompleter


class SyntaxCompleterPlugin(gedit.Plugin):
    """Automatically complete words from the list of words in the document."""
    handler_ids = []

    def __init__(self):
        """Initialize the plugin the whole Gedit application."""
        gedit.Plugin.__init__(self)

    def activate(self, window):
        """Activate the plugin in the current top-level window."""
        self.setup_syntax_completer(window.get_active_view())

    def deactivate(self, window):
        """deactivate the plugin in the current top-level window."""
        for (handler_id, view) in self.handler_ids:
            view.disconnect(handler_id)

    def update_ui(self, window):
        """Toggle the plugin's sensativity in the top-level window."""
        self.setup_syntax_completer( window.get_active_view())

    def setup_syntax_completer(self, view):
        """Setup the syntax completion in the view."""
        if type(view) != types.NoneType:
            if getattr(view, 'completion_instance', False) == False:
                setattr(view, 'completion_instance', SyntaxCompleter())
                handler_id = view.connect(
                    'key-press-event', view.completion_instance.complete_word)
                self.handler_ids.append((handler_id, view))
