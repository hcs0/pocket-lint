#!/usr/bin/python

__metaclass__ = type
__all__ = [
    'HTML5Page',
    'HTML5Browser',
    ]

import glib as GLib
import gtk as Gtk
import webkit as Webkit


class HTML5Page:

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

    def __init__(self, show_window=False):
        super(HTML5Browser, self).__init__()
        self.show_window = show_window
        self.browser_window = None
        self.script = None
        self.page = None
        self.listeners = {}

    def load_page(self, uri, timeout=5000):
        self.create_window()
        self.page = HTML5Page()
        self._connect(
            'status-bar-text-changed', self._on_status_bar_text_changed)
        self.open(uri)
        GLib.timeout_add(timeout, self._on_timeout)
        Gtk.main()
        return self.page

    def run_script(self, source, timeout=5000):
        self.create_window()
        self.page = HTML5Page()
        self._connect(
            'status-bar-text-changed', self._on_status_bar_text_changed)
        self.script = source
        self._connect('load-finished', self.on_script_load_finished)
        GLib.timeout_add(timeout, self._on_timeout)
        self.load_html_string(
            '<html><head></head><body></body></html>', 'file:///')
        Gtk.main()
        return self.page

    def on_script_load_finished(self, view, script):
        self._disconnect('load-finished')
        self.execute_script(self.script)
        self.script = None

    def create_window(self):
        if self.browser_window is not None:
            return
        self.browser_window = Gtk.Window()
        self.browser_window.set_default_size(800, 600)
        self.browser_window.connect("destroy", self.on_quit)
        scrolled = Gtk.ScrolledWindow()
        scrolled.add(self)
        self.browser_window.add(scrolled)
        if self.show_window:
            self.browser_window.show_all()

    def on_quit(self, widget=None):
        Gtk.main_quit()

    def _on_status_bar_text_changed(self, view, text):
        if text.startswith('::::'):
            self._disconnect('status-bar-text-changed')
            self.execute_script('window.status = "";')
            self.page.status = HTML5Page.STATUS_COMPLETE
            self.page.return_code = HTML5Page.CODE_SUCCESS
            self.page.content = text[4:]
            self.on_quit()

    def _on_timeout(self):
        if self.page.status is not HTML5Page.STATUS_COMPLETE:
            self._disconnect()
            self.page.status = HTML5Page.STATUS_COMPLETE
            self.page.return_code = HTML5Page.CODE_FAIL
            self.on_quit()
        return False

    def _connect(self, signal, callback, *args):
        self.listeners[signal] = self.connect(signal, callback, *args)

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
        'file:///home/curtis/Work/launchpad/webkit-yuitest-love-0/lib'
        '/lp/app/javascript/tests/test_picker.html')
    page = browser.load_page(uri)
    print page.content
