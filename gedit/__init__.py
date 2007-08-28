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



GEDIT_TAB_STATE_NORMAL = 'normal'
GEDIT_TAB_STATE_LOADING = 'loading'
GEDIT_TAB_STATE_REVERTING = 'reverting'
GEDIT_TAB_STATE_SAVING = 'saving'
GEDIT_TAB_STATE_PRINTING = 'printing'
GEDIT_TAB_STATE_PRINT_PREVIEWING = 'print-previewing'
GEDIT_TAB_STATE_SHOWING_PRINT_PREVIEW = 'showing-print-preview'
GEDIT_TAB_STATE_GENERIC_NOT_EDITABLE = 'generic-not-editable'
GEDIT_TAB_STATE_LOADING_ERROR = 'loading-error'
GEDIT_TAB_STATE_REVERTING_ERROR = 'reverting-error'
GEDIT_TAB_STATE_SAVING_ERROR = 'saving-error'
GEDIT_TAB_STATE_GENERIC_ERROR = 'generic-error'
GEDIT_TAB_STATE_CLOSING = 'closing'

def gedit_app_get_type():
    """A fake implementation of gedit_app_get_type."""
    key = '%s' % 'gedit_app_get_type'
    return Fake().data.get(key, None)

def app_get_default():
    """A fake implementation of app_get_default."""
    key = '%s' % 'app_get_default'
    return Fake().data.get(key, None)

def gedit_app_get_default():
    """A fake implementation of gedit_app_get_default."""
    key = '%s' % 'gedit_app_get_default'
    return Fake().data.get(key, None)

def document_error_quark():
    """A fake implementation of document_error_quark."""
    key = '%s' % 'document_error_quark'
    return Fake().data.get(key, None)

def gedit_document_get_type():
    """A fake implementation of gedit_document_get_type."""
    key = '%s' % 'gedit_document_get_type'
    return Fake().data.get(key, None)

def gedit_document_new():
    """A fake implementation of gedit_document_new."""
    key = '%s' % 'gedit_document_new'
    return Fake().data.get(key, None)

def gedit_encoding_get_type():
    """A fake implementation of gedit_encoding_get_type."""
    key = '%s' % 'gedit_encoding_get_type'
    return Fake().data.get(key, None)

def encoding_get_from_charset(charset):
    """A fake implementation of encoding_get_from_charset."""
    key = '%s' % 'encoding_get_from_charset'
    return Fake().data.get(key, None)

def gedit_encoding_get_from_charset(charset):
    """A fake implementation of gedit_encoding_get_from_charset."""
    key = '%s' % 'gedit_encoding_get_from_charset'
    return Fake().data.get(key, None)

def encoding_get_from_index(index):
    """A fake implementation of encoding_get_from_index."""
    key = '%s' % 'encoding_get_from_index'
    return Fake().data.get(key, None)

def gedit_encoding_get_from_index(index):
    """A fake implementation of gedit_encoding_get_from_index."""
    key = '%s' % 'gedit_encoding_get_from_index'
    return Fake().data.get(key, None)

def encoding_get_utf8():
    """A fake implementation of encoding_get_utf8."""
    key = '%s' % 'encoding_get_utf8'
    return Fake().data.get(key, None)

def gedit_encoding_get_utf8():
    """A fake implementation of gedit_encoding_get_utf8."""
    key = '%s' % 'gedit_encoding_get_utf8'
    return Fake().data.get(key, None)

def encoding_get_current():
    """A fake implementation of encoding_get_current."""
    key = '%s' % 'encoding_get_current'
    return Fake().data.get(key, None)

def gedit_encoding_get_current():
    """A fake implementation of gedit_encoding_get_current."""
    key = '%s' % 'gedit_encoding_get_current'
    return Fake().data.get(key, None)

def help_display(parent, file_name, link_id):
    """A fake implementation of help_display."""
    key = '%s' % 'help_display'
    return Fake().data.get(key, None)

def gedit_panel_get_type():
    """A fake implementation of gedit_panel_get_type."""
    key = '%s' % 'gedit_panel_get_type'
    return Fake().data.get(key, None)

def gedit_panel_new():
    """A fake implementation of gedit_panel_new."""
    key = '%s' % 'gedit_panel_new'
    return Fake().data.get(key, None)

def gedit_plugin_get_type():
    """A fake implementation of gedit_plugin_get_type."""
    key = '%s' % 'gedit_plugin_get_type'
    return Fake().data.get(key, None)

def gedit_tab_get_type():
    """A fake implementation of gedit_tab_get_type."""
    key = '%s' % 'gedit_tab_get_type'
    return Fake().data.get(key, None)

def tab_get_from_document(doc):
    """A fake implementation of tab_get_from_document."""
    key = '%s' % 'tab_get_from_document'
    return Fake().data.get(key, None)

def gedit_tab_get_from_document(doc):
    """A fake implementation of gedit_tab_get_from_document."""
    key = '%s' % 'gedit_tab_get_from_document'
    return Fake().data.get(key, None)

def gedit_view_get_type():
    """A fake implementation of gedit_view_get_type."""
    key = '%s' % 'gedit_view_get_type'
    return Fake().data.get(key, None)

def gedit_view_new(doc):
    """A fake implementation of gedit_view_new."""
    key = '%s' % 'gedit_view_new'
    return Fake().data.get(key, None)

def gedit_window_get_type():
    """A fake implementation of gedit_window_get_type."""
    key = '%s' % 'gedit_window_get_type'
    return Fake().data.get(key, None)


class App(GObject):
    """A fake implementation of App."""


    def create_window(self, screen):
        """A fake implementation of create_window."""
        key = '%s_%s' % (self.__class__.__name__, 'create_window')
        return Fake().data.get(key, None)

    def get_windows(self):
        """A fake implementation of get_windows."""
        key = '%s_%s' % (self.__class__.__name__, 'get_windows')
        return Fake().data.get(key, None)

    def get_active_window(self):
        """A fake implementation of get_active_window."""
        key = '%s_%s' % (self.__class__.__name__, 'get_active_window')
        return Fake().data.get(key, None)

    def get_documents(self):
        """A fake implementation of get_documents."""
        key = '%s_%s' % (self.__class__.__name__, 'get_documents')
        return Fake().data.get(key, None)

    def get_views(self):
        """A fake implementation of get_views."""
        key = '%s_%s' % (self.__class__.__name__, 'get_views')
        return Fake().data.get(key, None)

    def get_lockdown(self):
        """A fake implementation of get_lockdown."""
        key = '%s_%s' % (self.__class__.__name__, 'get_lockdown')
        return Fake().data.get(key, None)


class Document(SourceBuffer):
    """A fake implementation of Document."""


    def get_uri(self):
        """A fake implementation of get_uri."""
        key = '%s_%s' % (self.__class__.__name__, 'get_uri')
        return Fake().data.get(key, None)

    def get_uri_for_display(self):
        """A fake implementation of get_uri_for_display."""
        key = '%s_%s' % (self.__class__.__name__, 'get_uri_for_display')
        return Fake().data.get(key, None)

    def get_short_name_for_display(self):
        """A fake implementation of get_short_name_for_display."""
        key = '%s_%s' % (self.__class__.__name__, 'get_short_name_for_display')
        return Fake().data.get(key, None)

    def get_mime_type(self):
        """A fake implementation of get_mime_type."""
        key = '%s_%s' % (self.__class__.__name__, 'get_mime_type')
        return Fake().data.get(key, None)

    def get_readonly(self):
        """A fake implementation of get_readonly."""
        key = '%s_%s' % (self.__class__.__name__, 'get_readonly')
        return Fake().data.get(key, None)

    def load(self, uri, encoding, line_pos, create):
        """A fake implementation of load."""
        key = '%s_%s' % (self.__class__.__name__, 'load')
        return Fake().data.get(key, None)

    def insert_file(self, _iter, uri, encoding):
        """A fake implementation of insert_file."""
        key = '%s_%s' % (self.__class__.__name__, 'insert_file')
        return Fake().data.get(key, None)

    def load_cancel(self):
        """A fake implementation of load_cancel."""
        key = '%s_%s' % (self.__class__.__name__, 'load_cancel')
        return Fake().data.get(key, None)

    def save(self, flags):
        """A fake implementation of save."""
        key = '%s_%s' % (self.__class__.__name__, 'save')
        return Fake().data.get(key, None)

    def save_as(self, uri, encoding, flags):
        """A fake implementation of save_as."""
        key = '%s_%s' % (self.__class__.__name__, 'save_as')
        return Fake().data.get(key, None)

    def is_untouched(self):
        """A fake implementation of is_untouched."""
        key = '%s_%s' % (self.__class__.__name__, 'is_untouched')
        return Fake().data.get(key, None)

    def is_untitled(self):
        """A fake implementation of is_untitled."""
        key = '%s_%s' % (self.__class__.__name__, 'is_untitled')
        return Fake().data.get(key, None)

    def is_local(self):
        """A fake implementation of is_local."""
        key = '%s_%s' % (self.__class__.__name__, 'is_local')
        return Fake().data.get(key, None)

    def get_deleted(self):
        """A fake implementation of get_deleted."""
        key = '%s_%s' % (self.__class__.__name__, 'get_deleted')
        return Fake().data.get(key, None)

    def goto_line(self, line):
        """A fake implementation of goto_line."""
        key = '%s_%s' % (self.__class__.__name__, 'goto_line')
        return Fake().data.get(key, None)

    def set_search_text(self, text, flags):
        """A fake implementation of set_search_text."""
        key = '%s_%s' % (self.__class__.__name__, 'set_search_text')
        return Fake().data.get(key, None)

    def get_search_text(self, flags):
        """A fake implementation of get_search_text."""
        key = '%s_%s' % (self.__class__.__name__, 'get_search_text')
        return Fake().data.get(key, None)

    def get_can_search_again(self):
        """A fake implementation of get_can_search_again."""
        key = '%s_%s' % (self.__class__.__name__, 'get_can_search_again')
        return Fake().data.get(key, None)

    def search_forward(self, start, end, match_start, match_end):
        """A fake implementation of search_forward."""
        key = '%s_%s' % (self.__class__.__name__, 'search_forward')
        return Fake().data.get(key, None)

    def replace_all(self, find, replace, flags):
        """A fake implementation of replace_all."""
        key = '%s_%s' % (self.__class__.__name__, 'replace_all')
        return Fake().data.get(key, None)

    def search_backward(self, start, end, match_start, match_end):
        """A fake implementation of search_backward."""
        key = '%s_%s' % (self.__class__.__name__, 'search_backward')
        return Fake().data.get(key, None)

    def set_language(self, lang):
        """A fake implementation of set_language."""
        key = '%s_%s' % (self.__class__.__name__, 'set_language')
        return Fake().data.get(key, None)

    def get_language(self):
        """A fake implementation of get_language."""
        key = '%s_%s' % (self.__class__.__name__, 'get_language')
        return Fake().data.get(key, None)

    def get_encoding(self):
        """A fake implementation of get_encoding."""
        key = '%s_%s' % (self.__class__.__name__, 'get_encoding')
        return Fake().data.get(key, None)

    def set_enable_search_highlighting(self, enable):
        """A fake implementation of set_enable_search_highlighting."""
        key = '%s_%s' % (self.__class__.__name__, 'set_enable_search_highlighting')
        return Fake().data.get(key, None)

    def get_enable_search_highlighting(self):
        """A fake implementation of get_enable_search_highlighting."""
        key = '%s_%s' % (self.__class__.__name__, 'get_enable_search_highlighting')
        return Fake().data.get(key, None)


class Panel(gtk.VBox):
    """A fake implementation of Panel."""


    def add_item(self, item, name, image):
        """A fake implementation of add_item."""
        key = '%s_%s' % (self.__class__.__name__, 'add_item')
        return Fake().data.get(key, None)

    def add_item_with_stock_icon(self, item, name, stock_id):
        """A fake implementation of add_item_with_stock_icon."""
        key = '%s_%s' % (self.__class__.__name__, 'add_item_with_stock_icon')
        return Fake().data.get(key, None)

    def remove_item(self, item):
        """A fake implementation of remove_item."""
        key = '%s_%s' % (self.__class__.__name__, 'remove_item')
        return Fake().data.get(key, None)

    def activate_item(self, item):
        """A fake implementation of activate_item."""
        key = '%s_%s' % (self.__class__.__name__, 'activate_item')
        return Fake().data.get(key, None)

    def item_is_active(self, item):
        """A fake implementation of item_is_active."""
        key = '%s_%s' % (self.__class__.__name__, 'item_is_active')
        return Fake().data.get(key, None)

    def get_orientation(self):
        """A fake implementation of get_orientation."""
        key = '%s_%s' % (self.__class__.__name__, 'get_orientation')
        return Fake().data.get(key, None)

    def get_n_items(self):
        """A fake implementation of get_n_items."""
        key = '%s_%s' % (self.__class__.__name__, 'get_n_items')
        return Fake().data.get(key, None)


class Plugin(GObject):
    """A fake implementation of Plugin."""


    def activate(self, window):
        """A fake implementation of activate."""
        key = '%s_%s' % (self.__class__.__name__, 'activate')
        return Fake().data.get(key, None)

    def deactivate(self, window):
        """A fake implementation of deactivate."""
        key = '%s_%s' % (self.__class__.__name__, 'deactivate')
        return Fake().data.get(key, None)

    def update_ui(self, window):
        """A fake implementation of update_ui."""
        key = '%s_%s' % (self.__class__.__name__, 'update_ui')
        return Fake().data.get(key, None)

    def is_configurable(self):
        """A fake implementation of is_configurable."""
        key = '%s_%s' % (self.__class__.__name__, 'is_configurable')
        return Fake().data.get(key, None)

    def create_configure_dialog(self):
        """A fake implementation of create_configure_dialog."""
        key = '%s_%s' % (self.__class__.__name__, 'create_configure_dialog')
        return Fake().data.get(key, None)


class Statusbar(gtk.Statusbar):
    """A fake implementation of Statusbar."""


    def flash_message(self, context_id, message):
        """A fake implementation of flash_message."""
        key = '%s_%s' % (self.__class__.__name__, 'flash_message')
        return Fake().data.get(key, None)


class Tab(gtk.VBox):
    """A fake implementation of Tab."""


    def get_view(self):
        """A fake implementation of get_view."""
        key = '%s_%s' % (self.__class__.__name__, 'get_view')
        return Fake().data.get(key, None)

    def get_document(self):
        """A fake implementation of get_document."""
        key = '%s_%s' % (self.__class__.__name__, 'get_document')
        return Fake().data.get(key, None)

    def get_state(self):
        """A fake implementation of get_state."""
        key = '%s_%s' % (self.__class__.__name__, 'get_state')
        return Fake().data.get(key, None)

    def set_auto_save_enabled(self, enable):
        """A fake implementation of set_auto_save_enabled."""
        key = '%s_%s' % (self.__class__.__name__, 'set_auto_save_enabled')
        return Fake().data.get(key, None)

    def get_auto_save_enabled(self):
        """A fake implementation of get_auto_save_enabled."""
        key = '%s_%s' % (self.__class__.__name__, 'get_auto_save_enabled')
        return Fake().data.get(key, None)

    def set_auto_save_interval(self, interval):
        """A fake implementation of set_auto_save_interval."""
        key = '%s_%s' % (self.__class__.__name__, 'set_auto_save_interval')
        return Fake().data.get(key, None)

    def get_auto_save_interval(self):
        """A fake implementation of get_auto_save_interval."""
        key = '%s_%s' % (self.__class__.__name__, 'get_auto_save_interval')
        return Fake().data.get(key, None)


class View(SourceView):
    """A fake implementation of View."""


    def cut_clipboard(self):
        """A fake implementation of cut_clipboard."""
        key = '%s_%s' % (self.__class__.__name__, 'cut_clipboard')
        return Fake().data.get(key, None)

    def copy_clipboard(self):
        """A fake implementation of copy_clipboard."""
        key = '%s_%s' % (self.__class__.__name__, 'copy_clipboard')
        return Fake().data.get(key, None)

    def paste_clipboard(self):
        """A fake implementation of paste_clipboard."""
        key = '%s_%s' % (self.__class__.__name__, 'paste_clipboard')
        return Fake().data.get(key, None)

    def delete_selection(self):
        """A fake implementation of delete_selection."""
        key = '%s_%s' % (self.__class__.__name__, 'delete_selection')
        return Fake().data.get(key, None)

    def select_all(self):
        """A fake implementation of select_all."""
        key = '%s_%s' % (self.__class__.__name__, 'select_all')
        return Fake().data.get(key, None)

    def scroll_to_cursor(self):
        """A fake implementation of scroll_to_cursor."""
        key = '%s_%s' % (self.__class__.__name__, 'scroll_to_cursor')
        return Fake().data.get(key, None)

    def set_colors(self, _def, backgroud, text, selection, sel_text):
        """A fake implementation of set_colors."""
        key = '%s_%s' % (self.__class__.__name__, 'set_colors')
        return Fake().data.get(key, None)

    def set_font(self, _def, font_name):
        """A fake implementation of set_font."""
        key = '%s_%s' % (self.__class__.__name__, 'set_font')
        return Fake().data.get(key, None)


class Window(gtk.Window):
    """A fake implementation of Window."""


    def create_tab(self, jump_to):
        """A fake implementation of create_tab."""
        key = '%s_%s' % (self.__class__.__name__, 'create_tab')
        return Fake().data.get(key, None)

    def create_tab_from_uri(self, uri, encoding, line_pos, create, jump_to):
        """A fake implementation of create_tab_from_uri."""
        key = '%s_%s' % (self.__class__.__name__, 'create_tab_from_uri')
        return Fake().data.get(key, None)

    def close_tab(self, tab):
        """A fake implementation of close_tab."""
        key = '%s_%s' % (self.__class__.__name__, 'close_tab')
        return Fake().data.get(key, None)

    def close_tabs(self, tabs):
        """A fake implementation of close_tabs."""
        key = '%s_%s' % (self.__class__.__name__, 'close_tabs')
        return Fake().data.get(key, None)

    def close_all_tabs(self):
        """A fake implementation of close_all_tabs."""
        key = '%s_%s' % (self.__class__.__name__, 'close_all_tabs')
        return Fake().data.get(key, None)

    def get_active_tab(self):
        """A fake implementation of get_active_tab."""
        key = '%s_%s' % (self.__class__.__name__, 'get_active_tab')
        return Fake().data.get(key, None)

    def set_active_tab(self, tab):
        """A fake implementation of set_active_tab."""
        key = '%s_%s' % (self.__class__.__name__, 'set_active_tab')
        return Fake().data.get(key, None)

    def get_active_view(self):
        """A fake implementation of get_active_view."""
        key = '%s_%s' % (self.__class__.__name__, 'get_active_view')
        return Fake().data.get(key, None)

    def get_active_document(self):
        """A fake implementation of get_active_document."""
        key = '%s_%s' % (self.__class__.__name__, 'get_active_document')
        return Fake().data.get(key, None)

    def get_documents(self):
        """A fake implementation of get_documents."""
        key = '%s_%s' % (self.__class__.__name__, 'get_documents')
        return Fake().data.get(key, None)

    def get_unsaved_documents(self):
        """A fake implementation of get_unsaved_documents."""
        key = '%s_%s' % (self.__class__.__name__, 'get_unsaved_documents')
        return Fake().data.get(key, None)

    def get_views(self):
        """A fake implementation of get_views."""
        key = '%s_%s' % (self.__class__.__name__, 'get_views')
        return Fake().data.get(key, None)

    def get_group(self):
        """A fake implementation of get_group."""
        key = '%s_%s' % (self.__class__.__name__, 'get_group')
        return Fake().data.get(key, None)

    def get_side_panel(self):
        """A fake implementation of get_side_panel."""
        key = '%s_%s' % (self.__class__.__name__, 'get_side_panel')
        return Fake().data.get(key, None)

    def get_bottom_panel(self):
        """A fake implementation of get_bottom_panel."""
        key = '%s_%s' % (self.__class__.__name__, 'get_bottom_panel')
        return Fake().data.get(key, None)

    def get_statusbar(self):
        """A fake implementation of get_statusbar."""
        key = '%s_%s' % (self.__class__.__name__, 'get_statusbar')
        return Fake().data.get(key, None)

    def get_ui_manager(self):
        """A fake implementation of get_ui_manager."""
        key = '%s_%s' % (self.__class__.__name__, 'get_ui_manager')
        return Fake().data.get(key, None)

    def get_state(self):
        """A fake implementation of get_state."""
        key = '%s_%s' % (self.__class__.__name__, 'get_state')
        return Fake().data.get(key, None)

    def get_tab_from_uri(self, uri):
        """A fake implementation of get_tab_from_uri."""
        key = '%s_%s' % (self.__class__.__name__, 'get_tab_from_uri')
        return Fake().data.get(key, None)
