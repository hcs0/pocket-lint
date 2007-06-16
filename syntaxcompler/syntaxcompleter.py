# Copyright (C) 2007 - Curtis Hovey <sinzui.is at verizon.net>
"""A syntax completer for document words and python symbols."""

import re

from gtk.gdk import (
    KEY_PRESS, CONTROL_MASK, SHIFT_MASK, keyval_from_name)

class SyntaxCompleter:
    """Suggest and complete words as they are typed."""
    separators = r'\W'

    def __init__(self):
        """Initialize the list of matching words."""
        # Each word has a key to order it
        self.keys = {}
        self.key_counter = 1
        self.reset()

    def reset(self):
        """Reset the word list and cycle state."""
        self.cycle = False
        self.words = []
        self.word_i = 0
        self.last_word = None

    def complete_word(self, view, event):
        """Suggest and complete the word at the cursor."""
        space = keyval_from_name('space')

        if (event.type == KEY_PRESS
            and event.keyval == space
            and event.state & SHIFT_MASK
            and event.state & CONTROL_MASK):

            # Parts of the following code were taken from the Completion
            # Plugin of Guillaume Chazarain found at 
            # http://guichaz.free.fr/gedit-completion
            buffer = view.get_buffer()
            iter_cursor = buffer.get_iter_at_mark(buffer.get_insert())
            iter_line = iter_cursor.copy()
            iter_word = iter_cursor.copy()

            iter_line.set_line_offset(0)
            line = buffer.get_text(iter_line, iter_cursor)

            if not self.cycle:
                self.words = []
                match = re.search("[\w.]+$", line)
                if match != None:
                    word = match.group()
                    #mime_type = gedit.Document.get_mime_type()
                    mime_type = 'text/python'
                    if mime_type.find('python') > -1:
                        self.words = self.get_all_symbols(word)
                    # set word to match only the fragment after a dot
                    # make the word match normal words
                    word = word.split('.')[-1]
                    self.words.extend(self.get_all_words(word, buffer))
#                 match = re.search("[^%s]+$" % self.separators, line)
#                 if match != None:
#                     word = match.group()
#                     self.words.extend(self.get_all_words(word, buffer))
                if not self.words:
                    return False

                self.line_index = buffer.get_iter_at_mark(
                    buffer.get_insert()).get_line_index() - len(word)
            if len(self.words) > 1:
                if self.cycle:
                    self.word_i += 1
                    if self.word_i >= len(self.words):
                        self.word_i = 0
                iter_word.set_line_index(self.line_index)
                buffer.delete(iter_word, iter_cursor)
                buffer.insert_at_cursor(self.words[self.word_i])
            elif len(self.words) == 1:
                if self.cycle:
                    self.reset()
                    return False
                iter_word.set_line_index(self.line_index)
                buffer.delete(iter_word, iter_cursor)
                buffer.insert_at_cursor(self.words[0])
            else:
                if self.cycle:
                    self.reset()
                    return False

            self.last_word = self.words[self.word_i]
            self.cycle = True
            return True
        elif ((event.type == KEY_PRESS)
                and ((event.keyval == keyval_from_name('Control_L'))
                or (event.keyval == keyval_from_name('Control_R')))):
            return False
        else:
            if self.cycle:
                self.update_key(self.last_word)
            self.reset()
            return False

    def get_key(self, word):
        """return the key to a list of matching words or 0."""
        if self.keys.has_key(word):
            return self.keys[word]
        else:
            return 0

    def update_key(self, word):
        """Add a word to the keys."""
        self.keys[word] = self.key_counter
        self.key_counter += 1

    def get_all_words(self, word, buffer):
        """Build the dictionary of known words in the file."""
        text = buffer.get_text(
            buffer.get_start_iter(), buffer.get_end_iter())
        words = []
        words = re.findall(
            "(?:\A|[%(sep)s])(%(word)s[^%(sep)s]+)" % {
                "sep": self.separators,
                "word": re.escape(word)},
            text)

        words[:] = frozenset(words)
        words.sort()
        words.sort(key=self.get_key, reverse=True)
        words.append(word)
        return words

    def get_all_symbols(self, s, imports=None):
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
