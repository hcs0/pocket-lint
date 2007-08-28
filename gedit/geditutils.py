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



def uri_has_writable_scheme(uri):
    """A fake implementation of uri_has_writable_scheme."""
    key = '%s' % 'uri_has_writable_scheme'
    return Fake().data.get(key, None)

def uri_has_file_scheme(uri):
    """A fake implementation of uri_has_file_scheme."""
    key = '%s' % 'uri_has_file_scheme'
    return Fake().data.get(key, None)

def uri_exists(text_uri):
    """A fake implementation of uri_exists."""
    key = '%s' % 'uri_exists'
    return Fake().data.get(key, None)

def uri_is_valid(uri):
    """A fake implementation of uri_is_valid."""
    key = '%s' % 'uri_is_valid'
    return Fake().data.get(key, None)

def uri_get_dirname(uri):
    """A fake implementation of uri_get_dirname."""
    key = '%s' % 'uri_get_dirname'
    return Fake().data.get(key, None)

def menu_position_under_widget(menu, x, y, push_in, user_data):
    """A fake implementation of menu_position_under_widget."""
    key = '%s' % 'menu_position_under_widget'
    return Fake().data.get(key, None)

def menu_position_under_tree_view(menu, x, y, push_in, user_data):
    """A fake implementation of menu_position_under_tree_view."""
    key = '%s' % 'menu_position_under_tree_view'
    return Fake().data.get(key, None)
