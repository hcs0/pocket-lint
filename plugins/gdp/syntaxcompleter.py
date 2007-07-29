# Copyright (C) 2007 - Curtis Hovey <sinzui.is at verizon.net>
"""A syntax completer for document words and python symbols."""
# pylint: disable-msg=R0901, E0202


__metaclass__ = type

__all__ = ['BaseSyntaxGenerator',
           'SyntaxModel',
           'SyntaxComplete',
           'SyntaxController',
           'TextGenerator',]

import re
from xml.sax import saxutils

from gettext import gettext as _
import gobject
import gtk

from snippets.SnippetComplete import SnippetComplete, CompleteModel
from snippets.SnippetController import SnippetController


class BaseSyntaxGenerator(object):
    """An abstract class representing the source of a word prefix."""
    def __init__(self, prefix=None, text_buffer=None, file_path=None):
        """Create a new SyntaxGenerator."""
        self._prefix = prefix
        self._text_buffer = text_buffer
        self._file_path = file_path

    def getWords(self, prefix=None):
        """Return an orders list of words that match the prefix."""
        raise NotImplementedError

    @property
    def prefix(self):
        """The prefix use to match words to."""
        return self._prefix

    @property
    def file_path(self):
        """The path to the file that is the word source."""
        return self._file_path

    @property
    def buffer_text(self):
        """Return the text of the TextBuffer or None."""
        if not self._text_buffer:
            return None
        start_iter = self._text_buffer.get_start_iter()
        end_iter = self._text_buffer.get_end_iter()
        return self._text_buffer.get_text(start_iter , end_iter)


class TextGenerator(BaseSyntaxGenerator):
    """Generate a list of words that match a given prefix for a document."""
    def __init__(self, prefix=None, text_buffer=None, file_path=None):
        """Create a TextGenerator
        
        :prefix string: The word prefix used to locate complete words.
        :text_buffer gtk.TextBuffer: The source of words to search.
        :file_path string: The path to the file that contains the words to
                           search.
        """
        self._prefix = prefix
        self._text_buffer = text_buffer
        self._file_path = file_path
        if not self._text_buffer and self.file_path:
            self.file_path = self._file_path

    @property
    def prefix(self):
        """The prefix use to match words to."""
        return self._prefix

    def file_path(self):
        """The path to the file that is the source of this TextGenerator.
        
        Setting file_path will load the file into the text_buffer.
        """
        return self._file_path

    def _set_file_path(self, file_path):
        """See file_path."""
        self._file_path = file_path
        try:
            source_file = open(self._file_path)
            text = ''.join(source_file.readlines())
        except IOError:
            raise ValueError, _(u'%s cannot be read' % file_path)
        else:
            source_file.close()
        self._text_buffer = gtk.TextBuffer()
        self._text_buffer.set_text(text)

    file_path = property(
        fget=file_path, fset=_set_file_path, doc=file_path.__doc__)

    def getWords(self, prefix=None):
        """Return an orders list of words that match the prefix."""
        if not prefix and self._prefix:
            prefix = self._prefix
        else:
            # Match all words in the buffer_text.
            prefix = ""
        word_re = re.compile(r'\b(%s[\w-]+)' % re.escape(prefix), re.I)
        words = word_re.findall(self.buffer_text)
        # Find the unique words that do not have psuedo m-dashed in them.
        words[:] = set(word for word in words if '--' not in word)
        return words


# XXX sinzui 2007-07-18:
# Convert this to PythonSyntaxGenerator.
class PythonGenerator(BaseSyntaxGenerator):
    """Generate a list of words that match a given prefix for a Python."""
    def getWords(self, prefix=None):
        """Set the contextual completion of s (string of >= zero chars).

        If given, imports is a list of import statements to be executed first.
        """
        #import rpdb2; rpdb2.start_embedded_debugger('password')
        locald = {}
        if imports is not None:
            for stmt in imports:
                try:
                    exec stmt in globals(), locald
                except TypeError:
                    raise TypeError, "invalid type: %s" % stmt

        dots = s.split('.')
        if len(dots) == 1:
            keys = set()
            keys.update(locald.keys())
            keys.update(globals().keys())
            import __builtin__
            keys.update(dir(__builtin__))
            keys = list(keys)
            keys.sort()
            if s:
                return [k for k in keys if k.startswith(s)]
            else:
                return keys

        if len(dots) == 2:
            module = dots[0]
        else:
            module = '.'.join(dots[0:-1])

        try:
            symbol = eval(module, globals(), locald)
        except NameError:
            try:
                symbol = __import__(module, globals(), locald, [])
            except ImportError:
                return []

        suffix = dots[-1]
        return [k for k in dir(symbol) if k.startswith(suffix)]


class SyntaxModel(CompleteModel):
    """A model for managing multiple syntaxes.

    This model determine the words that can be inserted at the cursor. 
    The model understands the free text in the document and the Python syntax.
    """
    column_types = (str, str)

    def __init__(self, sources, prefix=None, description_only=False):
        """Create, sort, and display the model.
        
        The sources parameter is a tuple of mime_type, file_path, and
        text_buffer.
        """
        file_path, source_buffer = sources
        gtk.GenericTreeModel.__init__(self)
        self.words = self.create_list(file_path, source_buffer, prefix)
        self.words.sort(lambda a, b: cmp(a.lower(), b.lower()))
        self.visible_words = list(self.words)

    def create_list(self, file_path, source_buffer, prefix):
        """Return a list of words for the provides sources.

        Sources is a dictionary of the GtkSourceView type and data. The type
        key must be a supported parser (text or Python). The data value may
        be string that is passed to the parser
        """
        language = source_buffer.get_language()
        if language:
            mime_types = language.get_mime_types()
        else:
            mime_types = ['text/plain']
        words = []
        if 'python' in mime_types:
            pass #words.extend(parse_python(text_buffer, fileprefix))
        else:
            # We use assume the buffer is text/plain.
            syntax_generator = TextGenerator(
                prefix=prefix, text_buffer=source_buffer)
            words.extend(syntax_generator.getWords())
        return words

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
        self._filter_model(new_words)

    def _filter_model(self, new_words):
        """Update the tree rows to match the new words."""
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

    @property
    def display_snippet(self):
        """Maps display_word to the parent class."""
        return self.display_word

    @property
    def do_filter(self):
        """Maps filter_words to the parent class."""
        return self.filter_words


class SyntaxComplete(SnippetComplete):
    """A widget for selecting the word to insert at the cursor.

    This widget extends the Gedit Snippet module to complete the word
    using the syntax of the document.
    """
    def __init__(self, nodes, prefix=None, description_only=False):
        """Initialize the syntax completer."""
        # Replace the snippets.CompleteModel with the SyntaxModel
        # import SyntaxModel as CompleteModel
        CompleteModel = SyntaxModel
        super(SyntaxComplete, self).__init__(
            nodes=noes, prefix=prefix, description_only=description_only)

    def snippet_activated(self, word):
        """See snippets.syntaxcompleter.SnippetComplete

        Signal that the word (snippet) was selected.
        """
        self.emit('syntax-activated', word)
        self.destroy()


gobject.signal_new(
    'syntax-activated', SyntaxComplete, gobject.SIGNAL_RUN_LAST,
    gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))


class SyntaxController(SnippetController):
    """This class manages the interaction ofthe completion window."""

    def run_word(self):
        """Retrieve the words and the cursor and show the sytaxt widget."""
        if not self.view:
            return False
        buf = self.view.get_buffer()
        # get the word preceding the current insertion position
        (word, start, end) = self.get_tab_tag(buf)
        return self.show_completion(word)

    def deactivate_word(self, snippet, force=False):
        """SyntaxControler does not support snippets."""
        pass

    def show_completion(self, preset=None):
        """Show completion, shows a completion dialog in the view.

        If preset is not None then a completion dialog is shown with the
        snippets in the preset list. Otherwise it will try to find the word
        preceding the current cursor position. If such a word is found, it
        is taken as a  tab trigger prefix so that only snippets with a tab
        trigger prefixed with the word are in the list. If no such word can
        be found than all snippets are shown.
        """
        buf = self.view.get_buffer()
        bounds = buf.get_selection_bounds()
        prefix = None

        if not bounds and not preset:
            # When there is no text selected and no preset present, find the
            # prefix.
            (prefix, ignored, end) = self.get_tab_tag(buf)
        if not prefix:
            # If there is no prefix, than take the insertion point as the end.
            end = buf.get_iter_at_mark(buf.get_insert())

        # XXX sinzui 2007-07-22
        # We need to create the sources touple in place of nodes
        if len(buf.SourceLanguage.get_mime_types):
            mime_type = buf.SourceLanguage.get_mime_types[0]
        else:
            mime_type = 'text/plain'
        file_path = self.env_get_filename(buf)
        sources = (mime_type, file_path, buf)
        complete = SyntaxComplete(sources, prefix, False)

        complete.connect('syntax-activated', self.on_complete_row_activated)
        rect = self.view.get_iter_location(end)
        win = self.view.get_window(gtk.TEXT_WINDOW_TEXT)
        (x, y) = self.view.buffer_to_window_coords(
            gtk.TEXT_WINDOW_TEXT, rect.x + rect.width, rect.y)
        (xor, yor) = win.get_origin()
        self.move_completion_window(complete, x + xor, y + yor)
        return complete.run()

    def update_word_contents(self):
        """SyntaxController does not support snippets."""
        return False

    def on_complete_row_activated(self, complete, word):
        """Insert the word into the buffer."""
        buf = self.view.get_buffer()
        bounds = buf.get_selection_bounds()
        if bounds:
            self.apply_word(word, None, None)
        else:
            (ignored, start, end) = self.get_tab_tag(buf)
            self.apply_word(word, start, end)

    def on_buffer_cursor_moved(self, buf):
        """SyntaxControler does not support snippets."""
        self.deactivate_word(self.active_words)

    def on_view_key_press(self, view, event):
        """Show the completion widget."""
        if ((event.state & gdk.CONTROL_MASK)
            and (event.state & gdk.SHIFT_MASK)
            and not (event.state & gdk.MOD1_MASK)
            and event.keyval in self.SPACE_KEY_VAL):
            return self.show_completion()


if __name__ == '__main__':
    from tests.helpers import get_sourcebuffer
    sources = (None, get_sourcebuffer('plugins/gdp/data/snark12.txt'))
    model = SyntaxModel(sources, prefix='b')
    import rpdb2; rpdb2.start_embedded_debugger('password')
    print model.get_n_columns()

