import gedit

from gdp.lint import LintInstance

class LintPlugin (gedit.Plugin):
    """Pylint integration class."""
    def __init__(self):
        self._instances = {}
        super(LintPlugin, self).__init__ ()

    def activate(self, window):
        self._instances[window] = LintInstance (self, window)

    def deactivate(self, window):
        if self._instances.has_key(window):
            self._instances[window].deactivate()
            del self._instances[window]

    def update_ui(self, window):
        if self._instances.has_key(window):
            self._instances[window].update_ui()
