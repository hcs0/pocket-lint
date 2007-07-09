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
    """An abstract class representing the source of a word fragment."""
    def __init__(self, fragment=None, text_buffer=None, file_path=None):
        """Create a new Context."""
        self.fragment = fragment
        self._text_buffer = text_buffer
        self._file_path = file_path

    def getWords(self, fragment=None):
        """Return an orders list of words that match the fragment."""
        raise NotImplementedError

    @property
    def buffer_text(self):
        """Return the text of the TextBuffer."""
        assert self._text_buffer, _("text_buffer cannot be None.")
        start_iter = self._text_buffer.get_start_iter()
        end_iter = self._text_buffer.get_end_iter()
        return self._text_buffer.get_text(start_iter , end_iter)


class TextContext(Context):
    """Generate a list of words that match a given prefix for a document."""
    def __init__(self, fragment=None, text_buffer=None, file_path=None):
        """Create a TextContext
        
        :fragment string: The word fragment used to locate complete words.
        :text_buffer gtk.TextBuffer: The source of words to search.
        :file_path string: The path to the file that contains the words to
                           search.
        """
        self.fragment = fragment
        self._text_buffer = text_buffer
        self._file_path = file_path
        if not self._buffer and self.file_path:
            self.file_path = self._file_path

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
        self._textbuffer.set_text(text)

    file_path = property(
        fget=file_path, fset=_set_file_path, doc=file_path.__doc__)

    def getWords(self, fragment=None):
        """Return an orders list of words that match the fragment."""
        assert fragment or self._fragment, _(u"A word fragment is required.")
        if not fragment:
            fragment = self.fragment
        word_re = r'\b(%s[\w]+)' % re.escape(fragment)
        words = re.findall(word_re, self.buffer_text)
        words[:] = set(words)
        words.sort()
        words.append(fragment)
        return words        
