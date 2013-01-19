# Pyflakes is not ported to Pythong 3 yet.
class PyFlakesWarnings(object):
    def __init__(self, messages):
        self.message = messages

class PyFlakesChecker(object):
    """A fake for py3 that can run py2 in a sub-proc."""
    def __init__(self, tree, file_path='(none)'):
        return PyFlakesWarnings([])
