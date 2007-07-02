"""A mock implemetation of objects."""

import gobject
from gobject import *
import gtk
#from gtk import *
import gtk.gdk
from gtk.gdk import *
import gtksourceview
from gtksourceview import *
import gnome
from gnome import *

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
    """A mock implementation of gedit_app_get_type."""


def app_get_default():
    """A mock implementation of app_get_default."""


def gedit_app_get_default():
    """A mock implementation of gedit_app_get_default."""


def document_error_quark():
    """A mock implementation of document_error_quark."""


def gedit_document_get_type():
    """A mock implementation of gedit_document_get_type."""


def gedit_document_new():
    """A mock implementation of gedit_document_new."""


def gedit_encoding_get_type():
    """A mock implementation of gedit_encoding_get_type."""


def encoding_get_from_charset(charset):
    """A mock implementation of encoding_get_from_charset."""


def gedit_encoding_get_from_charset(charset):
    """A mock implementation of gedit_encoding_get_from_charset."""


def encoding_get_from_index(index):
    """A mock implementation of encoding_get_from_index."""


def gedit_encoding_get_from_index(index):
    """A mock implementation of gedit_encoding_get_from_index."""


def encoding_get_utf8():
    """A mock implementation of encoding_get_utf8."""


def gedit_encoding_get_utf8():
    """A mock implementation of gedit_encoding_get_utf8."""


def encoding_get_current():
    """A mock implementation of encoding_get_current."""


def gedit_encoding_get_current():
    """A mock implementation of gedit_encoding_get_current."""


def help_display(parent, file_name, link_id):
    """A mock implementation of help_display."""


def gedit_panel_get_type():
    """A mock implementation of gedit_panel_get_type."""


def gedit_panel_new():
    """A mock implementation of gedit_panel_new."""


def gedit_plugin_get_type():
    """A mock implementation of gedit_plugin_get_type."""


def gedit_tab_get_type():
    """A mock implementation of gedit_tab_get_type."""


def tab_get_from_document(doc):
    """A mock implementation of tab_get_from_document."""


def gedit_tab_get_from_document(doc):
    """A mock implementation of gedit_tab_get_from_document."""


def gedit_view_get_type():
    """A mock implementation of gedit_view_get_type."""


def gedit_view_new(doc):
    """A mock implementation of gedit_view_new."""


def gedit_window_get_type():
    """A mock implementation of gedit_window_get_type."""



class App(GObject):
    """A mock implementation of App."""

    def create_window(self, screen):
        """A mock implementation of create_window."""

    def get_windows(self):
        """A mock implementation of get_windows."""

    def get_active_window(self):
        """A mock implementation of get_active_window."""

    def get_documents(self):
        """A mock implementation of get_documents."""

    def get_views(self):
        """A mock implementation of get_views."""

    def get_lockdown(self):
        """A mock implementation of get_lockdown."""


class Document(SourceBuffer):
    """A mock implementation of Document."""

    def get_uri(self):
        """A mock implementation of get_uri."""

    def get_uri_for_display(self):
        """A mock implementation of get_uri_for_display."""

    def get_short_name_for_display(self):
        """A mock implementation of get_short_name_for_display."""

    def get_mime_type(self):
        """A mock implementation of get_mime_type."""

    def get_readonly(self):
        """A mock implementation of get_readonly."""

    def load(self, uri, encoding, line_pos, create):
        """A mock implementation of load."""

    def insert_file(self, _iter, uri, encoding):
        """A mock implementation of insert_file."""

    def load_cancel(self):
        """A mock implementation of load_cancel."""

    def save(self, flags):
        """A mock implementation of save."""

    def save_as(self, uri, encoding, flags):
        """A mock implementation of save_as."""

    def is_untouched(self):
        """A mock implementation of is_untouched."""

    def is_untitled(self):
        """A mock implementation of is_untitled."""

    def is_local(self):
        """A mock implementation of is_local."""

    def get_deleted(self):
        """A mock implementation of get_deleted."""

    def goto_line(self, line):
        """A mock implementation of goto_line."""

    def set_search_text(self, text, flags):
        """A mock implementation of set_search_text."""

    def get_search_text(self, flags):
        """A mock implementation of get_search_text."""

    def get_can_search_again(self):
        """A mock implementation of get_can_search_again."""

    def search_forward(self, start, end, match_start, match_end):
        """A mock implementation of search_forward."""

    def replace_all(self, find, replace, flags):
        """A mock implementation of replace_all."""

    def search_backward(self, start, end, match_start, match_end):
        """A mock implementation of search_backward."""

    def set_language(self, lang):
        """A mock implementation of set_language."""

    def get_language(self):
        """A mock implementation of get_language."""

    def get_encoding(self):
        """A mock implementation of get_encoding."""

    def set_enable_search_highlighting(self, enable):
        """A mock implementation of set_enable_search_highlighting."""

    def get_enable_search_highlighting(self):
        """A mock implementation of get_enable_search_highlighting."""


class Panel(gtk.VBox):
    """A mock implementation of Panel."""

    def add_item(self, item, name, image):
        """A mock implementation of add_item."""

    def add_item_with_stock_icon(self, item, name, stock_id):
        """A mock implementation of add_item_with_stock_icon."""

    def remove_item(self, item):
        """A mock implementation of remove_item."""

    def activate_item(self, item):
        """A mock implementation of activate_item."""

    def item_is_active(self, item):
        """A mock implementation of item_is_active."""

    def get_orientation(self):
        """A mock implementation of get_orientation."""

    def get_n_items(self):
        """A mock implementation of get_n_items."""


class Plugin(GObject):
    """A mock implementation of Plugin."""

    def activate(self, window):
        """A mock implementation of activate."""

    def deactivate(self, window):
        """A mock implementation of deactivate."""

    def update_ui(self, window):
        """A mock implementation of update_ui."""

    def is_configurable(self):
        """A mock implementation of is_configurable."""

    def create_configure_dialog(self):
        """A mock implementation of create_configure_dialog."""


class Statusbar(gtk.Statusbar):
    """A mock implementation of Statusbar."""

    def flash_message(self, context_id, message):
        """A mock implementation of flash_message."""


class Tab(gtk.VBox):
    """A mock implementation of Tab."""

    def get_view(self):
        """A mock implementation of get_view."""

    def get_document(self):
        """A mock implementation of get_document."""

    def get_state(self):
        """A mock implementation of get_state."""

    def set_auto_save_enabled(self, enable):
        """A mock implementation of set_auto_save_enabled."""

    def get_auto_save_enabled(self):
        """A mock implementation of get_auto_save_enabled."""

    def set_auto_save_interval(self, interval):
        """A mock implementation of set_auto_save_interval."""

    def get_auto_save_interval(self):
        """A mock implementation of get_auto_save_interval."""


class View(SourceView):
    """A mock implementation of View."""

    def cut_clipboard(self):
        """A mock implementation of cut_clipboard."""

    def copy_clipboard(self):
        """A mock implementation of copy_clipboard."""

    def paste_clipboard(self):
        """A mock implementation of paste_clipboard."""

    def delete_selection(self):
        """A mock implementation of delete_selection."""

    def select_all(self):
        """A mock implementation of select_all."""

    def scroll_to_cursor(self):
        """A mock implementation of scroll_to_cursor."""

    def set_colors(self, _def, backgroud, text, selection, sel_text):
        """A mock implementation of set_colors."""

    def set_font(self, _def, font_name):
        """A mock implementation of set_font."""


class Window(gtk.Window):
    """A mock implementation of Window."""

    def create_tab(self, jump_to):
        """A mock implementation of create_tab."""

    def create_tab_from_uri(self, uri, encoding, line_pos, create, jump_to):
        """A mock implementation of create_tab_from_uri."""

    def close_tab(self, tab):
        """A mock implementation of close_tab."""

    def close_tabs(self, tabs):
        """A mock implementation of close_tabs."""

    def close_all_tabs(self):
        """A mock implementation of close_all_tabs."""

    def get_active_tab(self):
        """A mock implementation of get_active_tab."""

    def set_active_tab(self, tab):
        """A mock implementation of set_active_tab."""

    def get_active_view(self):
        """A mock implementation of get_active_view."""

    def get_active_document(self):
        """A mock implementation of get_active_document."""

    def get_documents(self):
        """A mock implementation of get_documents."""

    def get_unsaved_documents(self):
        """A mock implementation of get_unsaved_documents."""

    def get_views(self):
        """A mock implementation of get_views."""

    def get_group(self):
        """A mock implementation of get_group."""

    def get_side_panel(self):
        """A mock implementation of get_side_panel."""

    def get_bottom_panel(self):
        """A mock implementation of get_bottom_panel."""

    def get_statusbar(self):
        """A mock implementation of get_statusbar."""

    def get_ui_manager(self):
        """A mock implementation of get_ui_manager."""

    def get_state(self):
        """A mock implementation of get_state."""

    def get_tab_from_uri(self, uri):
        """A mock implementation of get_tab_from_uri."""
