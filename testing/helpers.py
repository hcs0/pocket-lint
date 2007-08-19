# Copyright (C) 2007 - Curtis Hovey <sinzui.is at verizon.net>
"""GDP test helpers functions for setting up date."""

__metaclass__ = type


__ALL__ = ['get_sourcebuffer',
           'get_mock',
           'proof',
           'SignalTester']


import inspect
import re

from gettext import gettext as _
import gtk
from gtksourceview import SourceBuffer, SourceLanguagesManager

import gedit
from gedit import Mock


def get_sourcebuffer(file_path, mime_type='text/plain'):
    """return a gtk.TextBuffer for the provided file_path."""
    language_manager = SourceLanguagesManager()
    language = language_manager.get_language_from_mime_type(mime_type)
    try:
        source_file = open(file_path)
        text = ''.join(source_file.readlines())
    except IOError:
        raise ValueError, _(u'%s cannot be read' % file_path)
    else:
        source_file.close()
    source_buffer = SourceBuffer()
    source_buffer.set_language(language)
    source_buffer.set_text(text)
    return source_buffer


def get_document(file_path, mime_type='text/plain'):
    """Return a gedit.Document for the provided file_path."""
    language_manager = SourceLanguagesManager()
    language = language_manager.get_language_from_mime_type(mime_type)
    try:
        source_file = open(file_path)
        text = ''.join(source_file.readlines())
    except IOError:
        raise ValueError, _(u'%s cannot be read' % file_path)
    else:
        source_file.close()
    doc = gedit.Document()
    doc.set_language(language)
    doc.set_text(text)
    return doc


def get_window(file_path, document=None):
    """Return a gedit.Window with the document loaded from file_path.
    
    If file_path is None and document is not None, the provided document
    will be used with the window.
    """
    if file_path:
        document = get_document(file_path)
    elif not document:
        document = gedit.Document()
    else:
        # Use the provided document.
        pass
    view = gedit.View(document)
    scrolled_window = gtk.ScrolledWindow()
    scrolled_window.add(view)
    view.set_size_request(300, 250)
    window = gedit.Window()
    window.add(scrolled_window)
    window.connect("destroy", gtk.main_quit)
    window.resize(300, 250)
    window.show_all()
    return window, view, document


def get_mock():
    """Return a mock gedit object.
    
    Store data in keys named after the class and the <class>_<methods>.
    """
    return Mock()


def AssertEquals(outcome, expected):
    """Print a string represenation of an outcome's value.
    
    When the outcome is not equal to the expected value, the
    expected value and the outcome are printed for verification.
    """
    _testAssertion(outcome, expected, '==')


def literal(value):
    """Print the literal value.
    
    Display None, string, and numbers as raw values. Objects are
    presented using repr()
    """
    print '%s' % value


_re_tokens = re.compile(r'[\w]+')


def proof(outcome):
    """Print True when the outcome of an expression evaluates to True.
    
    When the outcome is False, the values in the expression are
    printed for verification.
    """
    if outcome is True:
        print '%s' % outcome
        return

    # The outcome of the expression did not evaluate to True.
    # Go up 2 frames to the testrunner and get the source of the example.
    source = inspect.stack()[2][0].f_locals['example'].source
    # Remove 'proof(...)\n' to get the expression the testrunner evaluated.
    expression = source[6:-2]
    tokens = set(_re_tokens.findall(expression))
    for token in list(tokens):
        # Go up 1 frame to the doctest and use the value of the token
        # if it is a local variable.
        if token in inspect.stack()[1][0].f_locals:
            value = repr(inspect.stack()[1][0].f_locals[token])
            expression = expression.replace(token, value)
    print expression


class SignalTester(object):
    """A simple class for GSignal emission and reception testing.
    
    Signal emission testing:
    testee = Testee()
    signal_tester = SignalTester(['testee', 'data'])
    signal_id = view.connect('syntax-activated', signal_tester.receiver)
    testee.emitDataMethodOrFunction(data)
    assert signal_tester.testee is testee
    assert signal_tester.data == data
    
    target = targatEmitterClass()
    testee = Testee()
    Signal Reception testing:
    signal_tester = SignalTester()
    signal_tester.attachReceptionHarness(testee)
    testee.testeeConnect(
        testee, target, 'target_name', 'signal-name', testee.on_callback)
    signal_tester.emitter('signal-name', target, data)
    ... (tests)
    testee.testeeDisconnect(
        testee, target, 'target_name', 'signal_name')
    signal_tester.detachReceptionHarness(testee)
    """

    def __init__(self, attrs=None):
        """Create instance attributes from a list of names.
        
        The list of names are are used to create instance attributes that
        can be access by a controlling routine.
        """
        self.attrs = attrs
        if attrs:
            for name in attrs:
                self.__dict__[name] = None

    def receiver(self, *args):
        """A generic method for testing a signal is received.
        
        The arguments received are assigned to the list of attrs passed
        when the class was initialized. Order is very important. Example:
        handler_id = testee.connect('signal-sent', signal_tester.receiver)
        """
        for i, name in enumerate(self.attrs):
            self.__dict__[name] = args[i]

    def emitter(self, signal_name, target, *args):
        """A generic method for emitting a signal.
        
        The args are sent as the data when signal_name is emitted. Order
        is very important.
        """
        target.emit(signal_name, *args)

    @classmethod
    def attachReceptionHarness(cls, testee):
        """Attached the methods need for testing callbacks.
        
        To test that a callback receives and handles a signal correctly,
        a dictionary and two methods are added to the testee:
        signal_tester_signal_ids is a dictionary of the signal ids that
        are being tests. See testeeConnect and testeeDisconnect for their
        explaination.
        """
        testee.signal_tester_signal_ids = {}
        testee.testeeConnect = cls.testeeConnect
        testee.testeeDisconnect = cls.testeeDisconnect

    @classmethod
    def detachReceptionHarness(cls, testee):
        """Detached the methods need for testing callbacks.
        
        Remove the callback test harness.
        """
        if testee.signal_tester_signal_ids:
            del testee.signal_tester_signal_ids
        if testee.testeeConnect:
            del testee.testeeConnect
        if testee.testeeDisconnect:
            del testee.testeeDisconnect

    @classmethod
    def testeeConnect(cls, testee, target, target_name, signal_name, callback):
        """A generic method for connecting the testee to SignalTester.
        
        This method can be monkey patched to the testee to connect the
        code being tested to the test.
        """
        key = '%s_%s' % (target_name, signal_name)
        testee.signal_tester_signal_ids[key] = target.connect(
            signal_name, callback)

    @classmethod
    def testeeDisconnect(cls, testee, target, target_name, signal_name):
        """A generic method for disconnecting the testee from SignalTester.
        
        This method can be monkey patched to the testee to connect the
        code being tested to the test.
        """
        key = '%s_%s' % (target_name, signal_name)
        target.disconnect(testee.signal_tester_signal_ids[key])
        del testee.signal_tester_signal_ids[key]
