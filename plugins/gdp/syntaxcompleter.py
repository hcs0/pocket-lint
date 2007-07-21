# Copyright (C) 2007 - Curtis Hovey <sinzui.is at verizon.net>
"""A syntax completer for document words and python symbols."""

__metaclass__ = type

__all__ = ['CompleteModel',
           'SyntaxComplete',
           'SyntaxControler']

import gobject
import gtk

from snippets.SnippetComplete import SnippetComplete


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

    def __init__(self, text_buffer, prefix=None, description_only=False):
        """Create, sort, and display the model."""
        gtk.GenericTreeModel.__init__(self)
        self.words = self.create_list(text_buffer, prefix)
        self.display_word = self.display_word_default
        self.do_filter = self.filter_word_default
        self.words.sort(lambda a, b: cmp(a.lower(), b.lower()))
        self.visible_words = list(self.word)

    def create_list(self, text_buffer, prefix):
        """Return a list of words for the provides sources.

        Sources is a dictionary of the GtkSourceView type and data. The type
        key must be a supported parser (text or Python). The data value may
        be string that is passed to the parser
        """
        words = []
        for datatype, data in sources:
            if 'python' == datatype:
                words.extend(parse_python(data, prefix))
            elif 'text' == datatype:
                words.extend(text_parser(data, prefix))
            else:
                raise ValueError, 'Unsupported datatype in sources.'
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


class SyntaxControler(object):
    """."""

    def __init__(self):
        pass

    def env_get_selected_text(self, buf):
        bounds = buf.get_selection_bounds()
        if bounds:
            return buf.get_text(bounds[0], bounds[1])
        else:
            return ''

    def env_get_current_word(self, buf):
        start, end = buffer_word_boundary(buf)
        return buf.get_text(start, end)

    def env_get_filename(self, buf):
        uri = buf.get_uri()
        if uri:
            return buf.get_uri_for_display()
        else:
            return ''

    def env_get_basename(self, buf):
        uri = buf.get_uri()
        if uri:
            return os.path.basename(buf.get_uri_for_display())
        else:
            return ''

    def update_environment(self):
        buf = self.view.get_buffer()
        variables = {
            'GEDIT_SELECTED_TEXT': self.env_get_selected_text,
            'GEDIT_CURRENT_WORD': self.env_get_current_word,
            'GEDIT_FILENAME': self.env_get_filename,
            'GEDIT_BASENAME': self.env_get_basename}
        for var in variables:
            os.environ[var] = variables[var](buf)

    def run_word(self):
        if not self.view:
            return False
        buf = self.view.get_buffer()
        # get the word preceding the current insertion position
        (word, start, end) = self.get_tab_tag(buf)
        if not word:
            return self.skip_to_next_placeholder()
        snippets = SnippetsLibrary().from_tag(word, self.language_id)
        if snippets:
            if len(snippets) == 1:
                return self.apply_word(snippets[0], start, end)
            else:
                # Do the fancy completion dialog
                return self.show_completion(snippets)
        return self.skip_to_next_placeholder()

    def deactivate_word(self, snippet, force = False):
        buf = self.view.get_buffer()
        remove = []
        for tabstop in snippet[3]:
            if tabstop == -1:
                placeholders = snippet[3][-1]
            else:
                placeholders = [snippet[3][tabstop]]

            for placeholder in placeholders:
                if placeholder in self.placeholders:
                    if placeholder in self.update_placeholders:
                        placeholder.update_contents()
                        self.update_placeholders.remove(placeholder)
                    elif placeholder in self.jump_placeholders:
                        placeholder[0].leave()
                    remove.append(placeholder)
        for placeholder in remove:
            if placeholder == self.active_placeholder:
                self.active_placeholder = None
            self.placeholders.remove(placeholder)
            placeholder.remove(force)

        buf.delete_mark(snippet[0])
        buf.delete_mark(snippet[1])
        buf.delete_mark(snippet[2])
        self.active_words.remove(snippet)
        if len(self.active_words) == 0:
            self.last_word_removed()


    def move_completion_window(self, complete, x, y):
        """Moves the completion window to a suitable place

        It honors the hint given by x and y. It tries to position the window
        so it's always visible on the screen.
        """
        MARGIN = 15
        screen = self.view.get_screen()
        width = screen.get_width()
        height = screen.get_height()
        cw, ch = complete.get_size()
        if x + cw > width:
            x = width - cw - MARGIN
        elif x < MARGIN:
            x = MARGIN
        if y + ch > height:
            y = height - ch - MARGIN
        elif y < MARGIN:
            y = MARGIN
        complete.move(x, y)

    def show_completion(self, preset = None):
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
            # prefix
            (prefix, ignored, end) = self.get_tab_tag(buf)
        if not prefix:
            # If there is no prefix, than take the insertion point as the end
            end = buf.get_iter_at_mark(buf.get_insert())
        if not preset or len(preset) == 0:
            # There is no preset, find all the text words and the language
            # specific words
            nodes = SnippetsLibrary().get_words(None)
            if self.language_id:
                nodes += SnippetsLibrary().get_words(self.language_id)
            if prefix and len(prefix) == 1 and not prefix.isalnum():
                hasnodes = False
                for node in nodes:
                    if node['tag'] and node['tag'].startswith(prefix):
                        hasnodes = True
                        break
                if not hasnodes:
                    prefix = None
            complete = SnippetComplete(nodes, prefix, False)
        else:
            # There is a preset, so show that preset
            complete = SnippetComplete(preset, None, True)
        complete.connect('snippet-activated', self.on_complete_row_activated)
        rect = self.view.get_iter_location(end)
        win = self.view.get_window(gtk.TEXT_WINDOW_TEXT)
        (x, y) = self.view.buffer_to_window_coords(
            gtk.TEXT_WINDOW_TEXT, rect.x + rect.width, rect.y)
        (xor, yor) = win.get_origin()
        self.move_completion_window(complete, x + xor, y + yor)
        return complete.run()

    def update_word_contents(self):
        self.timeout_update_id = 0
        for placeholder in self.update_placeholders:
            placeholder.update_contents()
        for placeholder in self.jump_placeholders:
            self.goto_placeholder(placeholder[0], placeholder[1])
        del self.update_placeholders[:]
        del self.jump_placeholders[:]
        return False

    # Callbacks
    def on_view_destroy(self, view):
        self.stop()
        return

    def on_complete_row_activated(self, complete, snippet):
        buf = self.view.get_buffer()
        bounds = buf.get_selection_bounds()
        if bounds:
            self.apply_word(snippet.data, None, None)
        else:
            (ignored, start, end) = self.get_tab_tag(buf)
            self.apply_word(snippet.data, start, end)

    def on_buffer_cursor_moved(self, buf):
        piter = buf.get_iter_at_mark(buf.get_insert())
        # Check for all snippets if the cursor is outside its scope
        for snippet in list(self.active_words):
            if snippet[0].get_deleted() or snippet[1].get_deleted():
                self.deactivate(snippet)
            else:
                begin = buf.get_iter_at_mark(snippet[0])
                end = buf.get_iter_at_mark(snippet[1])
                if piter.compare(begin) < 0 or piter.compare(end) > 0:
                    # Oh no! Remove the snippet this instant!!
                    self.deactivate_word(snippet)
        current = self.current_placeholder()
        if current != self.active_placeholder:
            if self.active_placeholder:
                self.jump_placeholders.append(
                    (self.active_placeholder, current))
                if self.timeout_update_id != 0:
                    gobject.source_remove(self.timeout_update_id)
                self.timeout_update_id = gobject.timeout_add(
                    0, self.update_word_contents)

            self.active_placeholder = current

    def on_buffer_changed(self, buf):
        current = self.current_placeholder()
        if current:
            self.update_placeholders.append(current)
            if self.timeout_update_id != 0:
                gobject.source_remove(self.timeout_update_id)
            self.timeout_update_id = gobject.timeout_add(
                0, self.update_word_contents)

    def on_notify_language(self, buf, spec):
        self.update_language()

    def on_notify_editable(self, view, spec):
        self._set_view(view)

    def on_view_key_press(self, view, event):
        library = SnippetsLibrary()
        if (not (event.state & gdk.CONTROL_MASK)
            and not (event.state & gdk.MOD1_MASK)
            and  event.keyval in self.TAB_KEY_VAL):
            if not event.state & gdk.SHIFT_MASK:
                return self.run_word()
            else:
                return self.skip_to_previous_placeholder()
        elif ((event.state & gdk.CONTROL_MASK)
            and not (event.state & gdk.MOD1_MASK)
            and not (event.state & gdk.SHIFT_MASK)
            and event.keyval in self.SPACE_KEY_VAL):
            return self.show_completion()
        elif (not library.loaded
            and library.valid_accelerator(event.keyval, event.state)):
            library.ensure_files()
            library.ensure(self.language_id)
            self.accelerator_activate(
                event.keyval,
                event.state & gtk.accelerator_get_default_mod_mask())
        return False

