# Copyright (C) 2007 - Curtis Hovey <sinzui.is at verizon.net>
"""A syntax completer for document words and python symbols."""


__metaclass__ = type

__all__ = [
    'BaseSyntaxGenerator',
    'SyntaxModel',
    'SyntaxView',
    'SyntaxController',
    'TextGenerator',
    ]


import re
from xml.sax import saxutils

from gettext import gettext as _
import gobject
import gtk
from gtk import gdk

from snippets.SnippetComplete import SnippetComplete, CompleteModel


class BaseSyntaxGenerator:
    """An abstract class representing the source of a word prefix."""

    def __init__(self, document, prefix=None):
        """Create a new SyntaxGenerator.

        :param prefix: A `str`. The word prefix used to locate complete words.
        :param document: `gedit.Document`. The source of words to search.
        """
        self._prefix = prefix
        self._document = document

    def get_words(self, prefix=None):
        """An unique `set` of words that match the prefix."""
        raise NotImplementedError

    @property
    def prefix(self):
        """The prefix use to match words to."""
        return self._prefix

    @property
    def file_path(self):
        """The path to the file that is the word source."""
        return self._document.get_uri()

    @property
    def text(self):
        """The text of the gedit.Document or None."""
        if not self._document:
            return None
        start_iter = self._document.get_start_iter()
        end_iter = self._document.get_end_iter()
        return self._document.get_text(start_iter , end_iter)


class TextGenerator(BaseSyntaxGenerator):
    """Generate a list of words that match a given prefix for a document."""

    def get_words(self, prefix=None):
        """See `BaseSyntaxGenerator.get_words`.

        :return: A set of words that match the prefix.
        """
        if not prefix and self._prefix:
            prefix = self._prefix
        else:
            # Match all words in the text.
            prefix = ''

        if len(prefix) > 0:
            # Match words that are just the prefix too.
            conditional = r'*'
        else:
            conditional = r'+'
        pattern = r'\b(%s[\w-]%s)' % (re.escape(prefix), conditional)
        word_re = re.compile(pattern, re.I)
        words = word_re.findall(self.text)
        # Find the unique words that do not have psuedo m-dashed in them.
        words = set(word for word in words if '--' not in word)
        return words


class PythonSyntaxGenerator(BaseSyntaxGenerator):
    """Generate a list of Python symbols that match a given prefix."""

    def get_words(self, prefix=None):
        """See `BaseSyntaxGenerator.get_words`.

        :return: A set of matching indentifiers.
        """
        if not prefix and self._prefix:
            prefix = self._prefix
        else:
            # Match all words in the text.
            prefix = ''

        locald = {}
        dots = prefix.split('.')
        if len(dots) == 1:
            symbols = set()
            symbols.update(locald.keys())
            symbols.update(globals().keys())
            import __builtin__
            symbols.update(dir(__builtin__))
            symbols = [key for key in symbols if key.startswith(prefix)]
            return set(symbols)

        if len(dots) == 2:
            module = dots[0]
        else:
            module = '.'.join(dots[0:-1])

        try:
            # Check this file first.
            symbol = eval(module, globals(), locald)
        except NameError:
            # Try a true import.
            try:
                symbol = __import__(module, globals(), locald, [])
            except ImportError:
                return set()

        suffix = dots[-1]
        symbols = [key for key in dir(symbol) if key.startswith(suffix)]
        return set(symbols)


class SyntaxModel(CompleteModel):
    """A model for managing multiple syntaxes.

    This model determine the words that can be inserted at the cursor.
    The model understands the free text in the document and the Python syntax.
    """
    # The class intentionally skips CompleteModel.__init__().
    # pylint: disable-msg=W0233

    column_types = (str, str)

    def __init__(self, document, prefix=None, description_only=False):
        """Create, sort, and display the model.

        :param document: A `gedit.Document`.
        :param prefix: A `str`. The optional prefix that words begin with.
        :param description_only: Not used.
        """
        gtk.GenericTreeModel.__init__(self)
        # Words is a unique list, or else CompleteModel.on_iter_next() enters
        # an infinite loop.
        self.words = self.create_list(document, prefix)
        self.visible_words = self.words
        # Map this classes methods to the parent class
        self.display_snippet = self.display_word
        self.do_filter = self.filter_words

    def create_list(self, document, prefix):
        """Return a list of sorted and unique words for the provides source.

        :param document: A `gedit.Document`. The source document
        :param prefix: `A str`. The begining of the word.
        """
        if hasattr(document, 'get_language'):
            language = document.get_language()
        else:
            # How can we not get a document?
            language = None

        words = set()
        if language and language.get_id() == 'python':
            words |= PythonSyntaxGenerator(document, prefix=prefix).get_words()
        words |= TextGenerator(document, prefix=prefix).get_words()
        return sorted(words, key=str.lower)

    def display_word(self, word):
        """Return the word escaped for Pango display."""
        return saxutils.escape(word)

    def filter_words(self, prefix):
        """Show only the words that start with the prefix."""
        new_words = []
        prefix = prefix.lower()
        for word in self.words:
            if word.lower().startswith(prefix):
                new_words.append(word)

        old_words = self.visible_words
        old_len = len(old_words)

        self.visible_words = new_words
        new_len = len(new_words)

        for index in range(0, min(new_len, old_len)):
            path = (index,)
            self.row_changed(path, self.get_iter(path))

        if old_len > new_len:
            for index in range(old_len - 1, new_len - 1, -1):
                self.row_deleted((index,))
        elif new_len > old_len:
            for index in range(old_len, new_len):
                path = (index,)
                self.row_inserted(path, self.get_iter(path))

    def get_word(self, path):
        """Return the word at the provided path."""
        try:
            return self.visible_nodes[path[0]]
        except IndexError:
            return None

    def on_get_n_columns(self):
        """Return the number of columns.

        This method is broken in the parent class.
        """
        # XXX sinzui 2008-06-08 gnome-bug=537248:
        # This method can be removed when this bug is fixed in GNOME.
        return len(self.column_types)

    # These properties maintain compatability with CompleteModel
    # and SnippetComplete in snippets.

    @property
    def nodes(self):
        """Maps words to the parent class."""
        return self.words

    @property
    def visible_nodes(self):
        """Maps visible_words to the parent class."""
        return self.visible_words


class SyntaxView(SnippetComplete):
    """A widget for selecting the word to insert at the cursor.

    This widget extends the Gedit Snippet module to complete the word
    using the vocabulary of the document.
    """

    def __init__(self, document, prefix=None, description_only=False):
        """Initialize the syntax view widget.

        :param document: A `gedit.Document`.
        :param prefix: A `str` that each word begins with.
        :param description_only: Not used.
        """
        self.snippet_activated = self.syntax_activated

        # Replace the snippets.SnippetComplete.CompleteModel
        # with the SyntaxModel.
        from snippets import SnippetComplete
        self.old_model = SnippetComplete.CompleteModel
        SnippetComplete.CompleteModel = SyntaxModel
        super(SyntaxView, self).__init__(
            nodes=document, prefix=prefix, description_only=description_only)

    def syntax_activated(self, word):
        """Signal that the word (snippet) was selected."""
        self.emit('syntax-activated', word)
        self.destroy()

    def destroy(self):
        """Restore the parent's model."""
        from snippets import SnippetComplete
        SnippetComplete.CompleteModel = self.old_model
        super(SyntaxView, self).destroy()


gobject.signal_new(
    'syntax-activated', SyntaxView, gobject.SIGNAL_RUN_LAST,
    gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))


class SyntaxController(object):
    """This class manages the gedit.View's interaction with the SyntaxView."""

    def __init__(self, view):
        """Initialize the controller for the gedit.View."""
        self.signal_ids = {}
        self.view = None
        self.set_view(view)

    def set_view(self, view, is_reset=False):
        """Set the view to be controlled.

        Installs signal handlers for the view. Calling document.get_uri()
        self.set_view(None) will effectively remove all the control from
        the current view. when is_reset is True, the current view's
        signals will be reset.
        """
        if view is self.view and not is_reset:
            return

        if self.view:
            # Unregister the current view before assigning the new one.
            self._disconnectSignal(self.view, 'destroy')
            self._disconnectSignal(self.view, 'notify::editable')
            self._disconnectSignal(self.view, 'key-press-event')

        self.view = view
        if view is not None:
            self.signal_ids['destroy'] = view.connect(
                'destroy', self.on_view_destroy)
            self.signal_ids['notify::editable'] = view.connect(
                'notify::editable', self.on_notify_editable)
            if view.get_editable():
                self.signal_ids['key-press-event'] = view.connect(
                    'key_press_event', self.on_view_key_press)

    def _disconnectSignal(self, obj, signal):
        """Disconnect the signal from the provided object."""
        if signal in self.signal_ids:
            obj.disconnect(self.signal_ids[signal])
            del self.signal_ids[signal]

    def show_syntax_view(self):
        """Show the SyntaxView widget."""
        document = self.view.get_buffer()
        (prefix, ignored, end) = self.get_word_prefix(document)
        syntax_view = SyntaxView(document, prefix, False)
        syntax_view.connect(
            'syntax-activated', self.on_syntaxview_row_activated)
        syntax_view.move(*self._calculate_syntax_view_position(syntax_view, end))
        if syntax_view.run():
            return syntax_view
        else:
            return None

    def _calculate_syntax_view_position(self, syntax_view, end):
        """Return the (x, y) coordinate to position the syntax_view

        The x and y coordinate will align the SyntaxView with the cursor
        when there is space to display it. Otherwise, it returns a
        coordinate to fit the SyntaxView to the bottom right of the
        screen.
        """

        def sane_x_or_y(ordinate, screen_length, view_length):
            """Return a x or y ordinate that is visible on the screen."""
            MARGIN = 15
            if ordinate + view_length > screen_length:
                return view_length - MARGIN
            elif ordinate < MARGIN:
                return MARGIN
            else:
                return ordinate

        rect = self.view.get_iter_location(end)
        (x, y) = self.view.buffer_to_window_coords(
            gtk.TEXT_WINDOW_TEXT, rect.x + rect.width, rect.y)
        (xor, yor) = self.view.get_window(gtk.TEXT_WINDOW_TEXT).get_origin()
        screen = self.view.get_screen()
        syntax_view_width, syntax_view_height = syntax_view.get_size()
        x = sane_x_or_y(x + xor, screen.get_width(), syntax_view_width)
        y = sane_x_or_y(y + yor, screen.get_height(), syntax_view_height)
        return (x, y)

    def get_word_prefix(self, document):
        """Return a 3-tuple of the word fragment before the cursor.
        
        The tuple contains the (word_fragement, start_iter, end_iter) to
        identify the prefix and its starting and end position in the 
        document.
        """
        word_char = re.compile(r'[\w_-]', re.I)
        end = document.get_iter_at_mark(document.get_insert())
        start = end.copy()
        word = None

        # When the preceding character is not alphanumeric,
        # there is be no word before the cursor.
        start_char = start.copy()
        if start_char.backward_char():
            char = start_char.get_char()
            if not word_char.match(char):
                return (None, start, end)

        # GtkTextIter *_word_end() methods do not seek for '_' and '-', so
        # we need to walk backwards through the iter to locate the word end.
        count = 0
        peek = start.copy()
        while peek.backward_chars(1):
            if not word_char.match(peek.get_char()):
                break
            else:
                count += 1

        if count > 0:
            start.backward_chars(count)
            word = document.get_text(start, end)
        else:
            word = None

        return (word, start, end)

    def insert_word(self, word, start=None):
        """Return True when the word is inserted into the Document.
        
        The word cannot be None or an empty string.
        """
        assert word, "The word cannot be None or an empty string."
        document = self.view.get_buffer()
        if start:
            document.delete(
                start, document.get_iter_at_mark(document.get_insert()))
        document.insert_at_cursor(word)

    def deactivate(self):
        """Deactivate the controller; detach the view."""
        self.set_view(None)

    # Callbacks

    def on_syntaxview_row_activated(self, syntax_view, word):
        """Insert the word into the Document."""
        if not word:
            return
        document = self.view.get_buffer()
        (ignored, start, end_) = self.get_word_prefix(document)
        self.insert_word(word, start)

    def on_notify_editable(self, view, param_spec):
        """Update the controller when the view editable state changes.
        
        This method is ultimately responsible for enabling and disabling
        the SyntaxView widget for syntax completion.
        """
        self.set_view(view, True)

    def on_view_key_press(self, view, event):
        """Show the SyntaxView widget when Control-Shift-Space is pressed."""
        state = gdk.CONTROL_MASK | gdk.SHIFT_MASK
        if event.state == state and event.keyval in (gtk.keysyms.space, ):
            self.show_syntax_view()

    def on_view_destroy(self, view):
        """Disconnect the controller."""
        self.deactivate()

