"""Test utilities."""

__metaclass__ = type


class Dummy(object):
    """A class for passing dummy data between the test and the testee."""

    # A dictionary to store data by <class>_<attribute> name
    data = {}

    def __new__(cls, *args, **kwargs):
        """Create a Singleton class."""
        if '_inst' not in vars(cls):
            cls._inst = super(Dummy, cls).__new__(cls, *args, **kwargs)
        return cls._inst

    def __getitem__(cls, key):
        """Return the value of the key in Dummy."""
        return cls.data[key]

    def __setitem__(cls, key, val):
        """Set the value of the key in Dummy."""
        cls.data[key] = val

    def __delitem__(cls, key):
        """Delete the key and value from Dummy."""
        del cls.data[key]

    def __contains__(cls, key):
        """Return True when the key is present in Dummy."""
        return name in cls.data[key]

    def __len__(cls):
        """Return number of items in Dummy."""
        return len(cls.data)

    def __repr__(cls):
        """Return the str representation of Dummy."""
        return repr(cls.data)

    def get(cls, key, default):
        """Return the value of the key in Dummy, or default."""
        return cls.data.get(key, default)
