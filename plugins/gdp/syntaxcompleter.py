# Copyright (C) 2007-2009 - Curtis Hovey <sinzui.is at verizon.net>
# This software is licensed under the GNU General Public License version 2
# (see the file COPYING).
"""A syntax completer for document words and python symbols."""


__metaclass__ = type

__all__ = [
    'BaseSyntaxGenerator',
    'MarkupGenerator',
    'PythonSyntaxGenerator',
    'SyntaxModel',
    'SyntaxView',
    'SyntaxController',
    'TextGenerator',
    ]


import re
from keyword import kwlist
from xml.sax import saxutils

import gobject
import gtk
from gtksourceview2 import language_manager_get_default

try:
    from snippets.SnippetComplete import SnippetComplete, CompleteModel
except ImportError:
    # The Snippet plugin is not enabled, so the module is not in the path.
    message = _("The snippet plugin must be enabled first.")
    dialog = gtk.MessageDialog(
        type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_CLOSE,
        message_format=message)
    dialog.run()
    dialog.destroy()

from gdp import PluginMixin


lang_manager = language_manager_get_default()
doctest_language = lang_manager.get_language('doctest')

doctest_pattern = re.compile(
    r'^.*(doc|test|stories).*/.*\.(txt|doctest)$')


def get_word(document, word_pattern):
    """Return a 3-tuple of the word fragment before the cursor.

    The tuple contains the (word_fragment, start_iter, end_iter) to
    identify the prefix and its starting and end position in the
    document.
    """
    end = document.get_iter_at_mark(document.get_insert())
    start = end.copy()
    word = None

    # When the preceding character is not alphanumeric,
    # there is be no word before the cursor.
    start_char = start.copy()
    if start_char.backward_char():
        char = start_char.get_char()
        if not word_pattern.match(char):
            return (None, start, end)

    # GtkTextIter *_word_end() methods do not seek for '_' and '-', so
    # we need to walk backwards through the iter to locate the word end.
    count = 0
    peek = start.copy()
    while peek.backward_chars(1):
        if not word_pattern.match(peek.get_char()):
            break
        else:
            count += 1

    if count > 0:
        start.backward_chars(count)
        word = document.get_text(start, end)
    else:
        word = None

    return (word, start, end)


class BaseSyntaxGenerator:
    """An abstract class representing the source of a word prefix."""

    def __init__(self, document, prefix=None):
        """Create a new SyntaxGenerator.

        :param prefix: A `str`. The word prefix used to match words.
        :param document: `gedit.Document`. The source of words to search.
        """
        self._prefix = prefix
        self._document = document

    word_char = re.compile(r'[\w_]', re.I)

    @property
    def string_before_cursor(self):
        """Return the string that matches `word_char` before the cursor."""
        text, start_iter, end_iter = get_word(self._document, self.word_char)
        if text is None:
            text = ''
        return text

    def ensure_prefix(self, prefix):
        """Return the available prefix or an empty string."""
        if prefix:
            return prefix
        elif self._prefix:
            return self._prefix
        else:
            # Match all words in the text.
            return ''

    def get_words(self, prefix=None):
        """Return a 2-tuple of is_authoritative and unique `set` of words.

        :param prefix: A `str`. The word prefix used to match words.
        :return: a 2-tuple of is_authoritative and a set of words.
            is_authoritative is True when the set of words are the only words
            that can match the prefix. The words are a set of words.
        """
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
        return self._document.get_text(start_iter, end_iter)


class TextGenerator(BaseSyntaxGenerator):
    """Generate a list of words that match a given prefix for a document."""

    def get_words(self, prefix=None):
        """See `BaseSyntaxGenerator.get_words`.

        is_authoritative is always False because TextGenerator because it is
        not for a specific document Language.
        """
        prefix = self.ensure_prefix(prefix)
        is_authoritative = False
        if len(prefix) > 0:
            # Match words that are just the prefix too.
            conditional = r'*'
        else:
            conditional = r'+'
        pattern = r'\b(%s[\w-]%s)' % (re.escape(prefix), conditional)
        word_re = re.compile(pattern, re.I)
        words = word_re.findall(self.text)
        # Find the unique words that do not have pseudo m-dashed in them.
        words = set(word for word in words if '--' not in word)
        return is_authoritative, words


class MarkupGenerator(BaseSyntaxGenerator):
    """Generate a list of elements and attributes for a document."""

    word_char = re.compile(r'[^<>]')
    common_attrs = []

    INSIDE_ATTRIBUTES = 'INSIDE_ATTRIBUTES'
    INSIDE_CLOSE = 'INSIDE_CLOSE'
    INSIDE_OPEN = 'INSIDE_OPEN'
    OUTSIDE = 'OUTSIDE'

    def get_cursor_context(self):
        """Return the context of the cursor in relation to the last tag."""
        text, start_iter, end_iter = get_word(self._document, self.word_char)
        if not start_iter.backward_char():
            # The start was at the begining of the doc; no tags were found.
            return self.OUTSIDE
        char = start_iter.get_char()
        if char == '>':
            return self.OUTSIDE
        elif text and text.startswith('/'):
            return self.INSIDE_CLOSE
        elif text and ' ' in text:
            return self.INSIDE_ATTRIBUTES
        else:
            return self.INSIDE_OPEN

    def get_words(self, prefix=None):
        """See `BaseSyntaxGenerator.get_words`."""
        prefix = self.ensure_prefix(prefix)
        context = self.get_cursor_context()
        if context == self.OUTSIDE:
            # is_authoritative is false and there are no words because the
            # cursor is not in a tag to complete.
            return False, set()
        is_authoritative = True
        if context == self.INSIDE_OPEN:
            words = self._get_open_tags(prefix)
        elif context == self.INSIDE_ATTRIBUTES:
            words = self._get_attributes(prefix)
        else:
            words = self._get_close_tags(prefix)
        return is_authoritative, words

    def get_cardinality(self, prefix):
        if prefix:
            # Match words that are just the prefix too.
            return r'*'
        else:
            return r'+'

    def _get_open_tags(self, prefix):
        """Return all the tag names."""
        cardinality = self.get_cardinality(prefix)
        prefix = re.escape(prefix)
        pattern = r'<(%s[\w_.:-]%s)' % (prefix, cardinality)
        word_re = re.compile(pattern, re.I)
        words = word_re.findall(self.text)
        return set(words)

    def _get_attributes(self, prefix):
        pattern = r'<[\w_.:-]+ ([\w_.:-]*)=[^>]+>'
        attrs_re = re.compile(pattern, re.I)
        attr_clusters = attrs_re.findall(self.text)
        attrs = set(self.common_attrs)
        for attr_cluster in attr_clusters:
            attr_pairs = attr_cluster.split()
            for pair in attr_pairs:
                attr = pair.split('=')
                attrs.add(attr[0])
        if prefix:
            for attr in list(attrs):
                if not attr.startswith(prefix):
                    attrs.remove(attr)
        return attrs

    def _get_close_tags(self, prefix):
        """Return the tags that are still open before the cursor."""
        cardinality = self.get_cardinality(prefix)
        prefix = re.escape(prefix)
        # Get the text before the cursor.
        start_iter = self._document.get_start_iter()
        end_iter = self._document.get_iter_at_mark(
            self._document.get_insert())
        text = self._document.get_text(start_iter, end_iter)
        # Get all the open tags.
        open_pattern = r'<(%s[\w_.:-]%s)' % (prefix, cardinality)
        open_re = re.compile(open_pattern, re.I)
        open_tags = open_re.findall(text)
        # Get all the empty tags.
        empty_pattern = r'<(%s[\w_.:-]%s)[^>]*/>' % (prefix, cardinality)
        empty_re = re.compile(empty_pattern, re.I)
        empty_tags = empty_re.findall(text)
        # Get all the close tags.
        close_pattern = r'</(%s[\w_.:-]%s)' % (prefix, cardinality)
        close_re = re.compile(close_pattern, re.I)
        close_tags = close_re.findall(text)
        # Return only the tags that are still open.
        for tag in empty_tags:
            if tag in open_tags:
                open_tags.remove(tag)
        for tag in close_tags:
            if tag in open_tags:
                open_tags.remove(tag)
        return set(open_tags)


class PythonSyntaxGenerator(BaseSyntaxGenerator):
    """Generate a list of Python symbols that match a given prefix."""

    word_char = re.compile(r'[\w_.]', re.I)

    def get_words(self, prefix=None):
        """See `BaseSyntaxGenerator.get_words`.

        :return: a 2-tuple of is_authoritative and a set of matching
            identifiers. is_authoritative is True when the prefix is a part
            of a dotted identifier.
        """
        prefix = self.ensure_prefix(prefix)
        is_authoritative = False
        if prefix == '':
            is_authoritative = True

        import __builtin__
        global_syms = dir(__builtin__)
        try:
            pyo = compile(self._get_parsable_text(), 'sc.py', 'exec')
        except SyntaxError:
            # This cannot be completed because of syntax errors.
            # Return
            self._document.emit('syntax-error-python')
            is_authoritative = False
            return is_authoritative, set()
        co_names = ('SIGNAL_RUN_LAST', 'TYPE_NONE', 'TYPE_PYOBJECT', 'object')
        local_syms = [name for name in pyo.co_names if name not in co_names]

        namespaces = self.string_before_cursor.split('.')
        if len(namespaces) == 1:
            # The identifier is scoped to this module (the document).
            symbols = set()
            symbols.update(local_syms)
            symbols.update(global_syms)
            symbols.update(kwlist)
            symbols = set(key for key in symbols
                          if key.startswith(prefix))
            return is_authoritative, symbols

        # Remove the prefix to create the module's full name.
        namespaces.pop()
        module_name = '.'.join(namespaces)
        locald = {}
        try:
            # Check this file first.
            module_ = eval(module_name, globals(), locald)
        except NameError:
            # Try a true import.
            try:
                module_ = __import__(module_name, globals(), locald, [])
            except ImportError:
                return is_authoritative, set()

        for symbol in namespaces[1:]:
            module_ = getattr(module_, symbol)
        is_authoritative = True
        symbols = set(symbol for symbol in dir(module_)
                      if symbol.startswith(prefix))
        return is_authoritative, symbols

    def _get_parsable_text(self):
        """Return the parsable text of the module.

        The line being edited may not be valid syntax, so the line is
        replaced with 'pass', or if it starts a block, it becomes 'if True:'
        """
        current_iter = self._document.get_iter_at_mark(
            self._document.get_insert())
        index = current_iter.get_line()
        text_lines = self.text.splitlines()
        if index + 1 == len(text_lines):
            # The current line is the last line. Add a fake line because
            # the compiler will require another line to follow a comment.
            text_lines.append('')
        current_indentation = self._get_indentation(text_lines[index])
        next_indentation = self._get_indentation(text_lines[index + 1])
        if len(next_indentation) > len(current_indentation):
            # Make this line compilable for the next block.
            text_lines[index] = current_indentation + 'if True:'
        else:
            # Comment-out this line so that it is not compiled.
            text_lines[index] = current_indentation + 'pass'
        return '\n'.join(text_lines)

    def _get_indentation(self, line):
        "Return the line's indentation"
        indentation_pattern = re.compile(r'^[ \t]*')
        match = indentation_pattern.match(line)
        if match:
            return match.group()
        # No match means the indentation is an empty string.
        return ''


class SyntaxModel(CompleteModel):
    """A model for managing multiple syntaxes.

    This model determine the words that can be inserted at the cursor.
    The model understands the free text in the document and the Python syntax.
    """
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

    def get_generator(self, document, prefix):
        """Return the specialized generator for document's language."""
        language_id = None
        if hasattr(document, 'get_language'):
            # How can we not get a document or language?
            language = document.get_language()
            if language is not None:
                language_id = language.get_id()
        if language_id == 'python':
            return PythonSyntaxGenerator(document, prefix=prefix)
        if language_id in ('xml', 'xslt', 'html', 'pt', 'mallard', 'docbook'):
            return MarkupGenerator(document, prefix=prefix)
        else:
            # The text generator is never returned because create_list will
            # use it in non-authoritative cases.
            return None

    def create_list(self, document, prefix):
        """Return a list of sorted and unique words for the provides source.

        :param document: A `gedit.Document`. The source document
        :param prefix: `A str`. The beginning of the word.
        """
        all_words = set()
        is_authoritative = False
        generator = self.get_generator(document, prefix)
        if generator:
            is_authoritative, words = generator.get_words()
            all_words |= words
        if not is_authoritative:
            is_authoritative, simple_words = TextGenerator(
                document, prefix=prefix).get_words()
            all_words |= simple_words
        return sorted(all_words, key=str.lower)

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
            path = (index, )
            self.row_changed(path, self.get_iter(path))

        if old_len > new_len:
            for index in range(old_len - 1, new_len - 1, -1):
                self.row_deleted((index, ))
        elif new_len > old_len:
            for index in range(old_len, new_len):
                path = (index, )
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
    gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))


class SyntaxController(PluginMixin):
    """This class manages the gedit.View's interaction with the SyntaxView."""

    def __init__(self, window):
        """Initialize the controller for the gedit.View."""
        self.signal_ids = {}
        self.view = None
        self.set_view(window.get_active_view())

    def deactivate(self):
        """Clean up resources before deactivation."""
        self.set_view(None)

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

    def _disconnectSignal(self, obj, signal):
        """Disconnect the signal from the provided object."""
        if signal in self.signal_ids:
            obj.disconnect(self.signal_ids[signal])
            del self.signal_ids[signal]

    def show_syntax_view(self, widget=None):
        """Show the SyntaxView widget."""
        if not self.view.get_editable():
            return
        document = self.view.get_buffer()
        (prefix, ignored, end) = self.get_word_prefix(document)
        syntax_view = SyntaxView(document, prefix, False)
        syntax_view.connect(
            'syntax-activated', self.on_syntaxview_row_activated)
        syntax_view.move(
            *self._calculate_syntax_view_position(syntax_view, end))
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
        return get_word(document, word_char)

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

    def correct_language(self, document):
        """Correct the language for ambuguous mime-types."""
        if not hasattr(document, 'get_language'):
            return
        file_path = document.get_uri_for_display()
        if doctest_pattern.match(file_path):
            document.set_language(doctest_language)

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

    def on_view_destroy(self, view):
        """Disconnect the controller."""
        self.deactivate()
