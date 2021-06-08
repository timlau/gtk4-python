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
import time

import gi

gi.require_version("Gtk", "4.0")
gi.require_version('Polkit', '1.0')

from gi.repository import Gtk, Polkit
from widgets import Window, Stack, MenuButton, get_font_markup, SearchBar, IconSelector, TextSelector


# Get an GPermission object from PolKit to use with Gtk.LockButton
def get_permision(action_id='org.freedesktop.accounts.user-administration'):
    prem = Polkit.Permission.new_sync(action_id, None, None)
    # print(prem.acquire())
    return prem


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

    def __init__(self, app, title, width, height, css):
        Window.__init__(self, app, title, height, width, css)
        self.revealer = None
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
        label.set_width_chars(len(title) + 2)
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
        # Stack Page 3
        self.page3 = self.add_page_misc('page3', 'Page 3')
        # add stack switcher to center of titlebar
        self.headerbar.set_title_widget(self.stack.switcher)
        # Add stack to window
        content.append(self.stack.widget)
        # Add main content box to windows
        self.window.set_child(content)

    def add_page_selector_icon(self, name, title):
        """ Add a page with a icon selector to the stack"""
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
        """ Add a page with a text selector to the stack"""
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

    def add_page_misc(self, name, title):
        """ Add a page with a text selector to the stack"""
        # Content box for the page
        frame = Gtk.Frame()
        # Set Frame Margins
        frame.set_margin_top(15)
        frame.set_margin_start(15)
        frame.set_margin_end(15)
        frame.set_margin_bottom(15)

        # Left/Right Paned
        # Orientation is the ways the separator is moving, not the way it is facing
        # So HORIZONTAL split in Left/Right and VERTICAL split in Top/Down
        self.left_right_paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        # Left Side
        left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        left_box.set_vexpand(True)
        left_box.set_spacing(5)
        left_label = Gtk.Label.new("LEFT")
        left_label.set_valign(Gtk.Align.START)
        left_label.set_halign(Gtk.Align.START)
        left_box.append(left_label)
        # Add Progress Bar
        progress = Gtk.ProgressBar()
        progress.set_fraction(.75)
        left_box.append(progress)
        # Add Scale
        scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 5)
        scale.set_value(25)
        left_box.append(scale)
        # sepatator
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        left_box.append(separator)
        self.left_right_paned.set_start_child(left_box)
        self.left_right_paned.set_shrink_start_child(False)  # Can't shrink
        # Right Side
        right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        right_label = Gtk.Label.new("RIGHT")
        right_label.set_valign(Gtk.Align.START)
        right_label.set_halign(Gtk.Align.START)
        right_box.append(right_label)
        # Some bottoms
        lock_btn = Gtk.LockButton.new(get_permision())
        right_box.append(lock_btn)
        # TexkView
        text = Gtk.TextView.new()
        # Set the default width
        text.set_size_request(150, -1)
        # Set Wrap Mode to word
        text.set_wrap_mode(Gtk.WrapMode.WORD)
        # Add some text
        txt = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras vitae leo ac magna lobortis maximus. ' \
              'Etiam eleifend, libero a pulvinar ornare, justo nunc porta velit, ut sodales mi est feugiat tellus. '
        text.get_buffer().set_text(txt)
        right_box.append(text)
        # Add Switches
        for txt in ['Reveal', 'Yet Another Option']:
            grid = Gtk.Grid()
            grid.set_column_spacing(30)
            grid.insert_row(0)
            grid.insert_column(0)
            grid.insert_column(1)
            grid.insert_column(2)
            grid.set_row_homogeneous(True)
            label = Gtk.Label.new(txt)
            label.set_hexpand(True)
            label.set_xalign(0.0)
            label.set_valign(Gtk.Align.CENTER)
            switch = Gtk.Switch()
            if txt == "Reveal":
                switch.connect('state-set', self.on_switch_activate)
                switch.set_state(True)
            grid.attach(label, 0, 1, 2, 1)
            grid.attach(switch, 2, 1, 1, 1)
            right_box.append(grid)
        # Some bottoms
        lock_btn = Gtk.LockButton.new()
        right_box.append(lock_btn)
        # Add the box to paned
        self.left_right_paned.set_end_child(right_box)
        self.left_right_paned.set_shrink_end_child(False)  # Can't shrink
        # Top/Down Paned
        self.top_botton_paned = Gtk.Paned(orientation=Gtk.Orientation.VERTICAL)
        # Top
        self.top_botton_paned.set_start_child(self.left_right_paned)
        self.top_botton_paned.set_shrink_start_child(False)
        # Bottom
        self.bottom_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.bottom_box.set_vexpand(False)
        # Add a label with custom font in the center
        label = Gtk.Label()
        markup = get_font_markup('Noto Sans Regular 24', f'This page is styled using main.css')
        label.set_markup(markup)
        # fill the whole page, will make the Label centered.
        label.set_halign(Gtk.Align.CENTER)
        label.set_vexpand(False)
        self.bottom_box.append(label)
        label = Gtk.Label()
        markup = get_font_markup('Noto Sans Regular 18', f'UGLY AS HELL, but shows how it is working')
        label.set_markup(markup)
        # fill the whole page, will make the Label centered.
        label.set_halign(Gtk.Align.CENTER)
        label.set_vexpand(False)
        self.bottom_box.append(label)
        # Revealer
        self.revealer = Gtk.Revealer()
        self.revealer.set_valign(Gtk.Align.END)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        label = Gtk.Label.new("This is a revlealer")
        box.append(label)
        self.revealer.set_child(box)
        self.revealer.set_transition_type(Gtk.RevealerTransitionType.CROSSFADE)
        self.revealer.set_transition_duration(200)
        self.revealer.set_reveal_child(True)
        self.bottom_box.append(self.revealer)
        self.top_botton_paned.set_end_child(self.bottom_box)
        self.top_botton_paned.set_shrink_end_child(False)  # Can't shrink
        frame.set_child(self.top_botton_paned)
        self.page3_label = label
        # add custom styling to widgets
        self.add_custom_styling(frame)
        # Add the content box as a new page in the stack
        return self.stack.add_page(name, title, frame)

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

    def on_switch_activate(self, widget, state):
        if self.revealer:
            self.revealer.set_reveal_child(state)
            time.sleep(.5)
            self.top_botton_paned.set_position(1000)


def on_activate(app):
    """
    Gtk.Application activate callback, called when application is run
    We use this to create the application window and show it
    """
    # Create the application windows
    win = MyWindow(app, "My Gtk4 Application", 800, 800, css='main.css')
    # Show the window (widget)
    Gtk.Widget.show(win.widget)


if __name__ == '__main__':
    # Create the main Gtk Application an connect the activate callback and run the application
    app = Gtk.Application(application_id='dk.rasmil.Example')
    app.connect('activate', on_activate)
    app.run(None)
