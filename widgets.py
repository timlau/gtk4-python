#    Copyright (C) 2021 Tim Lauridsen < tla[at]rasmil.dk >
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to
#    the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

"""
Misc classes to build Gtk4 Applications in python 3.9

It takes some of the hassle away from building Gtk4 application in Python
So you can create an cool application, without all the boilerplate code

"""


import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio


def get_font_markup(fontdesc, text):
    return f'<span font_desc="{fontdesc}">{text}</span>'


class SearchBar:
    """ Wrapper for Gtk.Searchbar Gtk.SearchEntry"""

    def __init__(self, win = None):
        self.searchbar = Gtk.SearchBar()
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        box.set_spacing(10)
        # Add SearchEntry
        self.entry = Gtk.SearchEntry()
        self.entry.set_hexpand(True)
        box.append(self.entry)
        # Add Search Options button (Menu content need to be added)
        btn = Gtk.MenuButton()
        btn.set_icon_name('preferences-other-symbolic')
        self.search_options = btn
        box.append(btn)
        self.searchbar.set_child(box)
        # connect search entry to seach bar
        self.searchbar.connect_entry(self.entry)
        if win:
            # set key capture from main window, it will show searchbar, when you start typing
            self.searchbar.set_key_capture_widget(win)
        # show close button in search bar
        self.searchbar.set_show_close_button(True)
        # Set search mode to off by default
        self.searchbar.set_search_mode(False)

    @property
    def widget(self):
        """Return the root widget for this class"""
        return self.searchbar

    def connect(self, callback):
        """ Connect the search entry activate to an callback handler"""
        self.entry.connect('activate', callback)

    def set_search_mode(self, mode):
        """ Set the search mode (search bar is shown and active """
        self.searchbar.set_search_mode(mode)


class MenuButton:
    """
    Wrapper class for at Gtk.Menubutton with a menu defined
    in a Gtk.Builder xml string
    """

    def __init__(self, xml, name, icon_name='open-menu-symbolic'):
        builder = Gtk.Builder()
        builder.add_from_string(xml)
        menu = builder.get_object(name)
        self.widget = Gtk.MenuButton()
        self.widget.set_menu_model(menu)
        self.widget.set_icon_name(icon_name)


class Stack:
    """ Wrapper for Gtk.Stack with  with a StackSwitcher """

    def __init__(self):
        self.switcher = Gtk.StackSwitcher()
        self.stack = Gtk.Stack()
        self.switcher.set_stack(self.stack)
        self._pages = {}

    @property
    def widget(self):
        """Return the root widget for this class"""
        return self.stack

    def add_page(self, name, title, widget):
        page = self.stack.add_child(widget)
        page.set_name(name)
        page.set_title(title)
        self._pages[name] = page
        return page


class Window:
    """ Wrapper for Gtk.ApplicationWindow with a headerbar"""

    def __init__(self, app, title, width, height):
        self.app = app
        self.window = Gtk.ApplicationWindow(application=app)
        self.window.set_default_size(width, height)
        self.headerbar = Gtk.HeaderBar()
        self.window.set_titlebar(self.headerbar)
        label = Gtk.Label()
        label.set_text(title)
        self.headerbar.set_title_widget(label)

    @property
    def widget(self):
        """Return the root widget for this class"""
        return self.window

    def add_action(self, name, callback):
        """ Add an Action and connect to a callback """
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.window.add_action(action)
