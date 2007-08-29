"""Test utilities."""

__metaclass__ = type

__all__ = ['Dummy',
           'SignalTester',
           'literal',
           'proof']

import inspect
import re


class Dummy(object):
    """A class for passing dummy data between the test and the testee."""

    # A dictionary to store data by <class>_<attribute> name
    data = {}

    def __new__(cls, *args, **kwargs):
        """Create a Singleton class."""
        if '_inst' not in vars(cls):
            cls._inst = super(Dummy, cls).__new__(cls, *args, **kwargs)
        return cls._inst

    def __getitem__(self, key):
        """Return the value of the key in Dummy."""
        return self.data[key]

    def __setitem__(self, key, val):
        """Set the value of the key in Dummy."""
        self.data[key] = val

    def __delitem__(self, key):
        """Delete the key and value from Dummy."""
        del self.data[key]

    def __contains__(self, key):
        """Return True when the key is present in Dummy."""
        return key in self.data

    def __len__(self):
        """Return number of items in Dummy."""
        return len(self.data)

    def __repr__(self):
        """Return the str representation of Dummy."""
        return repr(self.data)

    def get(self, key, default):
        """Return the value of the key in Dummy, or default."""
        return self.data.get(key, default)


class SignalTester(object):
    """A simple class for GSignal emission and reception testing.
    
    Signal emission testing:
    testee = Testee()
    signal_tester = SignalTester(['testee', 'data'])
    signal_id = signal_tester.connect('signal-name', signal_tester.receiver)
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
    def testeeConnect(
        cls, testee, target, target_name, signal_name, callback):
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

