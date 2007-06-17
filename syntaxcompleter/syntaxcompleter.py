# Copyright (C) 2007 - Curtis Hovey <sinzui.is at verizon.net>
"""A syntax completer for document words and python symbols."""

import re

from gtk.gdk import (
    KEY_PRESS, CONTROL_MASK, SHIFT_MASK, keyval_from_name)

class SyntaxCompleter:
    """Suggest and complete words as they are typed."""

    def __init__(self, language):
        """Initialize the list of matching words."""
        self.langauge = language
        self.sort_keys = {}
        self.sort_key_counter = 1
        self.reset()

    def reset(self):
        """Reset the word list."""
        self.words = []
        self.word_i = 0
        self.last_word = None

    def complete(self, view, event):
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
            iter_word = iter_cursor.copy()
            iter_line = iter_cursor.copy()
            iter_line.set_line_offset(0)
            line = buffer.get_text(iter_line, iter_cursor)

            if not self.words:
                text = buffer.get_text(
                    buffer.get_start_iter(), buffer.get_end_iter())
                word, self.words = self.getWords(line, text)
                if not self.words:
                    return False
                self.line_index = iter_cursor.get_line_index() - len(word)

            iter_word.set_line_index(self.line_index)
            buffer.delete(iter_word, iter_cursor)
            buffer.insert_at_cursor(self.words[self.word_i])
            self.last_word = self.words[self.word_i]
            self.word_i += 1
            if self.word_i >= len(self.words):
                self.word_i = 0
            return True
        else:
            self.updateSortKey(self.last_word)
            self.reset()
            return False

    def getWords(self, line, text):
        """Return touple of the word and the list of matches at the cursor.
        
        The last word in the list is the word at the cursor.
        """
        words = []
        match = re.search("[\w.]+$", line)
        if match != None:
            word = match.group()
            if self.langauge == "Python":
                words = self.getMatchingSymbols(word)
            # set word to match only the fragment after a dot
            # make the word match normal words
            word = word.split('.')[-1]
            words.extend(self.getMatchingWords(word, text))
        return (word, words)

    def getMatchingWords(self, word, text):
        """Build the dictionary of known words in the file."""
        words = []
        words = re.findall(r'\b(%s[\w]+)' % re.escape(word), text)
        words[:] = frozenset(words)
        words.sort()
        words.sort(key=self.getSortKey, reverse=True)
        words.append(word)
        return words

    def getSortKey(self, word):
        """return the word's key for list sorting."""
        if self.sort_keys.has_key(word):
            return self.sort_keys[word]
        else:
            return 0

    def updateSortKey(self, word):
        """Increment word's key for list sorting."""
        self.sort_keys[word] = self.sort_key_counter
        self.sort_key_counter += 1

    def getMatchingSymbols(self, s, imports=None):
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
