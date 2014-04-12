import os

try:
    import pep257
    # Shut up the linter.
    pep257
except ImportError:
    pep257 = None
from pocketlint.formatcheck import Language


class Plugin(object):
    """
    Base class for implementing pocket-lint plugins.

    You will need to define `check_all` if your linter needs whole content
    or `check_line` if you will check each line.

    Use `message` to add a message to reporter.
    """
    #: List of languages which can be checked using this plugin.
    languages = [Language.TEXT]
    #: Whether this plugin is enabled.
    enabled = True
    #: Path to current file that is checked.
    file_path = None
    #: Global options used by pocket-lint
    global_options = None

    def check(self, language, file_path, text, reporter, options):
        """
        Check code using this plugin.
        """
        if not self.enabled:
            return

        if language not in self.languages:
            return

        self._reporter = reporter
        self.global_options = options
        self.file_path = file_path

        self.check_all(text)

        for line_no, line in enumerate(text.splitlines()):
            self.check_line(line, line_no + 1)

    def check_all(self, text):
        """
        Check whole file content.
        """
        pass

    def check_line(self, line, line_no):
        """
        Check single line.
        """

    def message(self, line_no, message, icon=None):
        """
        Add a message to reporter.
        """
        self._reporter(
            line_no,
            message,
            icon=icon,
            base_dir=os.path.dirname(self.file_path),
            file_name=self.file_path,
            )


class PEP257Plugin(Plugin):
    """
    A plugin to check Python docstrings for PEP257.
    """

    languages = [Language.PYTHON]

    _default_options = {
        'ignore': ['D203', 'D204', 'D401'],
        }

    def __init__(self, options=None):
        if not options:
            options = self._default_options.copy()
        self._options = options
        self.enabled = pep257 != None
        self._checker = pep257.PEP257Checker()

    def check_all(self, text):
        """Pass all content to pep257 module."""
        results = self._checker.check_source(text, self.file_path)
        for error in results:
            if error.code in self._options['ignore']:
                continue
            self.message(error.line, error.message, icon='error')
