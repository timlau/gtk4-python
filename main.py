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
Sample Python Gtk4 Application
"""
import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk
from widgets import Window, Stack, MenuButton, get_font_markup, SearchBar, IconSelector, TextSelector

# Gtk.Builder xml for the application menu
APP_MENU = """
<?xml version="1.0" encoding="UTF-8"?>
<interface>
<menu id='app-menu'>
  <section>
    <item>
      <attribute name='label' translatable='yes'>_New Stuff</attribute>
      <attribute name='action'>win.new</attribute>
    </item>
    <item>
      <attribute name='label' translatable='yes'>_About</attribute>
      <attribute name='action'>win.about</attribute>
    </item>
    <item>
      <attribute name='label' translatable='yes'>_Quit</attribute>
      <attribute name='action'>win.quit</attribute>
    </item>
  </section>
</menu>
</interface>
"""


class MyWindow(Window):

    def __init__(self, app, title, width, height):
        Window.__init__(self, app, title, height, width)
        # Add Menu Button to the titlebar (Right Side)
        menu = MenuButton(APP_MENU, 'app-menu')
        self.headerbar.pack_end(menu.widget)
        self.add_action('new', self.menu_handler)
        self.add_action('about', self.menu_handler)
        self.add_action('quit', self.menu_handler)

        # make a new title label and add it to the left.
        # So we kan place the stack switcher in the middle
        label = Gtk.Label()
        label.set_text(title)
        # add 2 chars indent on the label for better looks
        label.set_halign(Gtk.Align.END)
        label.set_width_chars(len(title)+2)
        self.headerbar.pack_start(label)
        # Main content box
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        # Search Bar
        self.search = SearchBar(self.window)
        content.append(self.search.widget)
        # search bar is active by default
        self.search.connect(self.on_search)

        # Stack
        self.stack = Stack()
        # Stack Page 1
        self.page1 = self.add_page_selector_icon('page1', 'Page 1')
        # Stack Page 2
        self.page2 = self.add_page_selector_text('page2', 'Page 2')
        # add stack switcher to center of titlebar
        self.headerbar.set_title_widget(self.stack.switcher)
        # Add stack to window
        content.append(self.stack.widget)
        # Add main content box to windows
        self.window.set_child(content)

    def add_page_selector_icon(self, name, title):
        """ Add a simple page with a centered Label to the stack"""
        # Content box for the page
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        # Add info selector
        selector = IconSelector()
        selector.add_row("row1", "dialog-information-symbolic")
        selector.add_row("row2", "software-update-available-symbolic")
        selector.add_row("row3", "drive-multidisk-symbolic")
        selector.add_row("row4", "insert-object-symbolic")
        selector.connect(self.on_select_page1)
        box.append(selector.widget)
        # Add a label with custom font in the center
        label = Gtk.Label()
        markup = get_font_markup('Noto Sans Regular 32', f'This is {title}')
        label.set_markup(markup)
        # fill the whole page, will make the Label centered.
        label.set_hexpand(True)
        label.set_vexpand(True)
        box.append(label)
        self.page1_label = label
        # Add the content box as a new page in the stack
        return self.stack.add_page(name, title, box)

    def add_page_selector_text(self, name, title):
        """ Add a simple page with a centered Label to the stack"""
        # Content box for the page
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        # Add info selector
        selector = TextSelector()
        selector.add_row("Orange", "Orange")
        selector.add_row("Apple", "Apple")
        selector.add_row("Water Melon", "Water Melon")
        selector.add_row("Lollypop", "Lollypop")
        selector.connect(self.on_select_page2)
        box.append(selector.widget)
        # Add a label with custom font in the center
        label = Gtk.Label()
        markup = get_font_markup('Noto Sans Regular 32', f'This is {title}')
        label.set_markup(markup)
        # fill the whole page, will make the Label centered.
        label.set_hexpand(True)
        label.set_vexpand(True)
        box.append(label)
        self.page2_label = label
        # Add the content box as a new page in the stack
        return self.stack.add_page(name, title, box)

    def menu_handler(self, action, state):
        """ Callback for  menu actions"""
        name = action.get_name()
        print(f'active : {name}')
        if name == 'quit':
            self.window.close()

    def on_search(self, widget):
        print(f'Searching for : {widget.get_text()}')

    def on_select_page1(self, name):
        print(f'on_select_page1 : {name}')
        markup = get_font_markup('Noto Sans Regular 32', f'{name} is selected')
        self.page1_label.set_markup(markup)

    def on_select_page2(self, name):
        print(f'on_select_page2 : {name}')
        markup = get_font_markup('Noto Sans Regular 32', f'{name} is selected')
        self.page2_label.set_markup(markup)


def on_activate(app):
    """
    Gtk.Application activate callback, called when application is run
    We use this to create the application window and show it
    """
    # Create the application windows
    win = MyWindow(app, "My Gtk4 Application", 800, 800)
    # Show the window (widget)
    Gtk.Widget.show(win.widget)


if __name__ == '__main__':
    # Create the main Gtk Application an connect the activate callback and run the application
    app = Gtk.Application(application_id='dk.rasmil.Example')
    app.connect('activate', on_activate)
    app.run(None)
