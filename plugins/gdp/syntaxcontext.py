# Copyright (C) 2007 - Curtis Hovey <sinzui.is at verizon.net>
"""Context objects that represent a source of words.

A context may be used to build a list of words that relate to a term.
"""
# pylint: disable-msg=I0011, E0202, R0922

__metaclass__ = type

import re

from gettext import gettext as _

import gtk


class Context(object):
    """An abstract class representing the source of a word prefix."""
    def __init__(self, prefix=None, text_buffer=None, file_path=None):
        """Create a new Context."""
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


class TextContext(Context):
    """Generate a list of words that match a given prefix for a document."""
    def __init__(self, prefix=None, text_buffer=None, file_path=None):
        """Create a TextContext
        
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
        """The path to the file that is the source of this TextContext.
        
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
        assert prefix or self._prefix, _(u"A word prefix is required.")
        if not prefix:
            prefix = self.prefix
        word_re = r'\b(%s[\w-]+)' % re.escape(prefix)
        words = re.findall(word_re, self.buffer_text)
        # Find the unique words that do not have psuedo m-dashed in them.
        words[:] = set(word for word in words if '--' not in word)
        words.sort()
        words.append(prefix)
        return words        
