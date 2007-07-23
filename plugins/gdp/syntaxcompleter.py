# Copyright (C) 2007 - Curtis Hovey <sinzui.is at verizon.net>
"""A syntax completer for document words and python symbols."""
# pylint: disable-msg=R0901


__metaclass__ = type

__all__ = ['CompleteModel',
           'SyntaxComplete',
           'SyntaxControler']

import gobject
import gtk

from snippets.SnippetComplete import SnippetComplete
from snippets.SnippetController import SnippetController

from gdp.syntaxmodels import TextModel

# XXX sinzui 2007-07-18:
# Push this function into syntaxmodels.
def getMatchingSymbols(s, imports=None):
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

    dots = s.split(".")
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


class CompleteModel(gtk.GenericTreeModel):
    """A model for managing multiple syntaxes.

    This model determine the words that can be inserted at the cursor. 
    The model understands the free text in the document and the Python syntax.
    """

    def __init__(self, sources, prefix=None, description_only=False):
        """Create, sort, and display the model.
        
        The sources parameter is a tuple of mime_type, file_path, and
        text_buffer.
        """
        mime_type, file_path, text_buffer = sources
        gtk.GenericTreeModel.__init__(self)
        self.words = self.create_list(
            mime_type, file_path, text_buffer, prefix)
        self.display_word = self.display_word_default
        self.do_filter = self.filter_word_default
        self.words.sort(lambda a, b: cmp(a.lower(), b.lower()))
        self.visible_words = list(self.words)

    @property
    def nodes(self):
        """Return the all the words in the model.
        
        This properties name is used to mape words to node for the
        parent class.
        """
        return self.words

    def create_list(self, mime_type, file_path, text_buffer, prefix):
        """Return a list of words for the provides sources.

        Sources is a dictionary of the GtkSourceView type and data. The type
        key must be a supported parser (text or Python). The data value may
        be string that is passed to the parser
        """
        words = []
        if 'python' in mime_type:
            pass #words.extend(parse_python(text_buffer, fileprefix))
        else:
            # We use assume the buffer is text/plain.
            syntax_model = TextModel(prefix=prefix, text_buffer=text_buffer)
            words.extend(syntax_model.getWords())
        return words

    def display_word_default(self, word):
        """Return the word escaped for Pango display."""
        return markup_escape(word)

    def filter_word_default(self, prefix):
        """Show only the words that start with the prefix."""
        new = []
        prefix = prefix.lower()
        for word in self.words:
            if word.lower().startswith(prefix):
                new.append(word)
        self.filter_word_process(new)

    def filter_word_process(self, new):
        """Show the words in the new list."""
        old = self.visible_words
        oldlen = len(old)

        self.visible_words = new
        newlen = len(new)

        for index in range(0, min(newlen, oldlen)):
            path = (index,)
            self.row_changed(path, self.get_iter(path))

        if oldlen > newlen:
            for index in range(oldlen - 1, newlen - 1, -1):
                self.row_deleted((index,))
        elif newlen > oldlen:
            for index in range(oldlen, newlen):
                path = (index,)
                self.row_inserted(path, self.get_iter(path))

    def get_word(self, path):
        """Return the word at the provided path."""
        return on_get_iter(path)

    def on_get_flags(self):
        """Return the gtk.TreeModel flags."""
        return gtk.TREE_MODEL_LIST_ONLY

    def on_get_n_columns(self):
        """Return the number of columns."""
        len(self.column_types)

    def on_get_column_type(self, index):
        """Return the column type of column at the index."""
        return self.column_types[index]

    def on_get_iter(self, path):
        """Return the word at the path."""
        try:
            return self.visible_words[path[0]]
        except IndexError:
            return None

    def on_get_path(self, rowref):
        """Return the path to the rowref."""
        return self.visible_words.index(rowref)

    def on_get_value(self, rowref, column):
        """Return the value of the column at the rowref."""
        if column == 0:
            return self.display_word(rowref)
        elif column == 1:
            # The rowref is the raw word.
            return rowref
        else:
            raise ValueError, "The column index does not exist."

    def on_iter_next(self, rowref):
        """Return the next word."""
        try:
            next = self.visible_words.index(rowref) + 1
        except ValueError:
            next = 0

        try:
            return self.visible_words[next]
        except IndexError:
            return None

    def on_iter_children(self, parent):
        """Return the first word, or None.

         Return None when parent evaluates to True because lists do not have
         parent nodes.
         """
        if parent:
            return None
        else:
            return self.visible_words[0]

    def on_iter_has_child(self, rowref):
        """Return False.

        Lists do not have child nodes.
        """
        return False

    def on_iter_n_children(self, rowref):
        """Return the number of visible words.

        Return 0 when rowref evaluates to True becauses lists to not have
        child nodes.
        """
        if rowref:
            return 0
        return len(self.visible_words)

    def on_iter_nth_child(self, parent, n):
        """Return the n visible word.

        Return None when parent evaluates to True because lists do not have
        parent nodes.
        """
        if parent:
            return None

        try:
            return self.visible_words[n]
        except IndexError:
            return None

    def on_iter_parent(self, child):
        """Return None becauses lists to not have parent nodes."""
        return None


class SyntaxComplete(SnippetComplete):
    """A widget for selecting the word to insert at the cursor.

    This widget extends the Gedit Snippet module to complete the word
    using the syntax of the document.
    """

    def snippet_activated(self, word):
        """See snippets.syntaxcompleter.SnippetComplete

        Signal that the word (snippet) was selected.
        """
        self.emit('syntax-activated', word)
        self.destroy()


gobject.signal_new(
    'syntax-activated', SyntaxComplete, gobject.SIGNAL_RUN_LAST,
    gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))


class SyntaxControler(SnippetController):
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
