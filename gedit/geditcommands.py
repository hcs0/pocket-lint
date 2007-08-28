"""A fake implemetation of objects."""

import gobject
from gobject import *
import gtk
import gtk.gdk
from gtk.gdk import *
import gtksourceview
from gtksourceview import *
import gnome
from gnome import *



class Fake(object):
    """A class for passing fake data between the test and the testee."""

    # A dictionary to store data by <class>_<attribute> name
    data = {}

    def __new__(cls, *args, **kwargs):
        """Create a Singleton class."""
        if '_inst' not in vars(cls):
            cls._inst = super(Fake, cls).__new__(cls, *args, **kwargs)
        return cls._inst



def load_uri(window, uri, encoding, line_pos):
    """A fake implementation of load_uri."""
    key = '%s' % 'load_uri'
    return Fake().data.get(key, None)

def load_uris(window, uris, encoding, line_pos):
    """A fake implementation of load_uris."""
    key = '%s' % 'load_uris'
    return Fake().data.get(key, None)
