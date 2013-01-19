# Pyflakes is not ported to Pythong 3 yet.


class PyFlakesChecker(object):
    """A fake for py3 that can run py2 in a sub-proc."""
    def __init__(self, tree, filename='(none)'):
        self.messages = []
