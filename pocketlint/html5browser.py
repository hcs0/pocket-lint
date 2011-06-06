#!/usr/bin/python
"""A Web browser that can be driven by an application."""

__metaclass__ = type
__all__ = [
    'HTML5Command',
    'HTML5Browser',
    ]

import glib as GLib
import gtk as Gtk
import webkit as Webkit


class HTML5Command:
    """A representation of the status and result of a command."""
    STATUS_RUNNING = object()
    STATUS_COMPLETE = object()
    CODE_UNKNOWN = -1
    CODE_SUCCESS = 0
    CODE_FAIL = 1

    def __init__(self, status=STATUS_RUNNING, return_code=CODE_UNKNOWN,
                 content=None):
        self.status = status
        self.return_code = return_code
        self.content = content


class HTML5Browser(Webkit.WebView):
    """A browser that can be driven by an application."""

    def __init__(self, show_window=False):
        super(HTML5Browser, self).__init__()
        self.show_window = show_window
        self.browser_window = None
        self.script = None
        self.command = None
        self.listeners = {}

    def load_page(self, uri, timeout=5000):
        """Load a page and return the content."""
        self._setup_listening_operation(timeout)
        self.open(uri)
        Gtk.main()
        return self.command

    def run_script(self, script, timeout=5000):
        """Run a script and return the result."""
        self._setup_listening_operation(timeout)
        self.script = script
        self._connect('load-finished', self._on_script_load_finished)
        self.load_html_string(
            '<html><head></head><body></body></html>', 'file:///')
        Gtk.main()
        return self.command

    def _setup_listening_operation(self, timeout):
        """Setup a one-time listening operation for command's completion."""
        self._create_window()
        self.command = HTML5Command()
        self._connect(
            'status-bar-text-changed', self._on_status_bar_text_changed)
        GLib.timeout_add(timeout, self._on_timeout)

    def _create_window(self):
        """Create a window needed to render pages."""
        if self.browser_window is not None:
            return
        self.browser_window = Gtk.Window()
        self.browser_window.set_default_size(800, 600)
        self.browser_window.connect("destroy", self._on_quit)
        scrolled = Gtk.ScrolledWindow()
        scrolled.add(self)
        self.browser_window.add(scrolled)
        if self.show_window:
            self.browser_window.show_all()

    def _on_quit(self, widget=None):
        Gtk.main_quit()

    def _on_status_bar_text_changed(self, view, text):
        if text.startswith('::::'):
            self._disconnect('status-bar-text-changed')
            self.execute_script('window.status = "";')
            self.command.status = HTML5Command.STATUS_COMPLETE
            self.command.return_code = HTML5Command.CODE_SUCCESS
            self.command.content = text[4:]
            self._on_quit()

    def _on_script_load_finished(self, view, script):
        self._disconnect('load-finished')
        self.execute_script(self.script)
        self.script = None

    def _on_timeout(self):
        if self.command.status is not HTML5Command.STATUS_COMPLETE:
            self._disconnect()
            self.command.status = HTML5Command.STATUS_COMPLETE
            self.command.return_code = HTML5Command.CODE_FAIL
            self._on_quit()
        return False

    def _connect(self, signal, callback):
        self.listeners[signal] = self.connect(signal, callback)

    def _disconnect(self, signal=None):
        if signal is None:
            signals = self.listeners.keys()
        elif isinstance(signal, basestring):
            signals = [signal]
        for key in signals:
            self.disconnect(self.listeners[key])
            del self.listeners[key]


if __name__ == '__main__':
    browser = HTML5Browser(show_window=False)
    uri = (
        'file:///home/curtis/Work/launchpad/webkit-yuitest-love-1/lib'
        '/lp/app/javascript/tests/test_picker.html')
    page = browser.load_page(uri)
    print page.content
