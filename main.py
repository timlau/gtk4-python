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

from gi.repository import Gtk, Polkit, GObject, Gio
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


class MyFactory(Gtk.ListItemFactory):
    def __init__(self):
        super(MyFactory, self).__init__()
        print(self.__dict__)



class ListElem(GObject.GObject):

    def __init__(self, name: str, state: bool):
        super(ListElem, self).__init__()
        self.name = name
        self.state = state


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
        self.page1 = self.setup_page_one('page1', 'Page 1')
        # Stack Page 2
        self.page2 = self.setup_page_two('page2', 'Page 2')
        # Stack Page 3
        self.page3 = self.setup_page_three('page3', 'Page 3')
        # Stack Page 4
        self.page4 = self.setup_page_four('page4', 'Page 4')
        # Stack Page 5
        self.page5 = self.setup_page_five('page5', 'Page 5')
        # add stack switcher to center of titlebar
        self.headerbar.set_title_widget(self.stack.switcher)
        # Add stack to window
        content.append(self.stack.widget)
        # Add main content box to windows
        self.window.set_child(content)

    def setup_page_one(self, name, title):
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

    def setup_page_two(self, name, title):
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

    def setup_page_three(self, name, title):
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

    def setup_page_four(self, name, title):
        """ Add a page with a text selector to the stack"""
        # Content box for the page
        frame = Gtk.Frame()
        # Set Frame Margins
        frame.set_margin_top(15)
        frame.set_margin_start(15)
        frame.set_margin_end(15)
        frame.set_margin_bottom(15)

        # Content box for the page
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        # Add a label with custom font in the center
        label = Gtk.Label()
        markup = get_font_markup('Noto Sans Regular 20', f'This is {title}')
        label.set_markup(markup)
        label.set_valign(Gtk.Align.START)
        content.append(label)
        # Output label to write stuff
        label = Gtk.Label()
        label.set_margin_top(20)
        label.set_margin_start(20)
        label.set_hexpand(True)
        label.set_halign(Gtk.Align.CENTER)
        label.set_xalign(0.0)
        content.append(label)
        self.page4_label = label
        # Lock button
        lock_btn = Gtk.LockButton.new(get_permision())
        lock_btn.set_margin_top(20)
        lock_btn.set_halign(Gtk.Align.CENTER)
        lock_btn.set_hexpand(False)
        content.append(lock_btn)
        # buttoms
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        box.set_halign(Gtk.Align.CENTER)
        box.set_margin_top(20)
        box.set_spacing(10)
        for x in range(5):
            btn = Gtk.Button()
            btn.set_label(f'Button {x}')
            btn.connect('clicked', self.on_button_clicked)
            box.append(btn)
        content.append(box)
        # Entry
        entry = Gtk.Entry()
        entry.set_halign(Gtk.Align.FILL)
        entry.set_valign(Gtk.Align.END)
        entry.set_margin_top(20)
        entry.set_margin_start(20)
        entry.set_margin_end(20)
        entry.set_placeholder_text("Type something here ....")
        entry.connect('activate', self.on_entry_activate)
        content.append(entry)
        # Calendar
        calendar = Gtk.Calendar()
        calendar.set_margin_top(20)
        calendar.set_halign(Gtk.Align.CENTER)
        calendar.connect('day-selected', self.on_calendar_changed)
        content.append(calendar)
        frame.set_child(content)
        # Add the content box as a new page in the stack
        return self.stack.add_page(name, title, frame)

    def setup_page_five(self, name, title):
        """ Add a page with a text selector to the stack"""
        # Content box for the page
        frame = Gtk.Frame()
        # Set Frame Margins
        frame.set_margin_top(15)
        frame.set_margin_start(15)
        frame.set_margin_end(15)
        frame.set_margin_bottom(15)

        # Content box for the page
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        # Add a label with custom font in the center
        label = Gtk.Label()
        markup = get_font_markup('Noto Sans Regular 20', f'This is {title}')
        label.set_markup(markup)
        label.set_valign(Gtk.Align.START)
        content.append(label)
        # Output label to write stuff
        label = Gtk.Label()
        label.set_margin_top(20)
        label.set_margin_start(20)
        label.set_hexpand(True)
        label.set_halign(Gtk.Align.CENTER)
        label.set_xalign(0.0)
        content.append(label)
        self.page5_label = label
        # List View
        # Use the signal Factory, so we can connect our own methods to setup
        self.factory = Gtk.SignalListItemFactory()
        # connect to factory signals
        self.factory.connect('setup', self.on_factory_setup)
        self.factory.connect('bind', self.on_factory_bind)
        # self.factory.connect('unbind', self.on_factory_unbind)
        # self.factory.connect('teardown', self.on_factory_teardown)
        sw = Gtk.ScrolledWindow()
        # Create Gtk.Listview
        self.listview = Gtk.ListView.new()
        self.listview.set_vexpand(True)
        self.listview.set_margin_start(50)
        self.listview.set_margin_end(50)
        self.listview.set_margin_bottom(50)
        self.listview.set_factory(self.factory)
        # Create data model, use our own class as elements
        self.store = Gio.ListStore.new(ListElem)
        # put some data into the model
        self.store.append(ListElem("One", True))
        self.store.append(ListElem("Two", False))
        self.store.append(ListElem("Three", True))
        self.store.append(ListElem("Four", False))
        # create a selection model containing our data model
        self.model = Gtk.SingleSelection.new(self.store)
        # set the selection model to the view
        self.listview.set_model(self.model)
        sw.set_child(self.listview)
        content.append(sw)
        frame.set_child(content)
        # Add the content box as a new page in the stack
        return self.stack.add_page(name, title, frame)

# ---------------------- Handlers --------------------------

    def on_factory_setup(self, widget, item):
        """ Setup the widgets to go into the ListView """
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        label = Gtk.Label()
        label.set_halign(Gtk.Align.START)
        label.set_hexpand(True)
        label.set_margin_start(10)
        switch = Gtk.Switch()
        switch.set_halign(Gtk.Align.END)
        switch.set_margin_end(10)
        box.append(label)
        box.append(switch)
        item.set_child(box)

    def on_factory_bind(self, widget, item: Gtk.ListItem):
        """ apply data from model to widgets set in setup"""
        # get the Gtk.Box stored in the ListItem
        box = item.get_child()
        # get the model item, connected to current ListItem
        data = item.get_item()
        # get the Gtk.Label (first item in box)
        label=box.get_first_child()
        # get the Gtk.Switch (next sibling to the Label)
        switch = label.get_next_sibling()
        # Update Gtk.Label with data from model item
        label.set_text(data.name)
        # Update Gtk.Switch with data from model item
        switch.set_state(data.state)
        item.set_child(box)


    def on_factory_unbind(self, widget, item):
        print(f'unbind : {widget=} {item=}')
        item.set_child(None)

    def on_factory_teardown(self, widget, item):
        print(f'teardown : {widget=} {item=}')


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

    def on_button_clicked(self, widget):
        txt = f'{widget.get_label()} was pressed'
        markup = f'<span foreground="#00ffff" weight="bold">{txt}</span>'
        self.page4_label.set_markup(markup)

    def on_calendar_changed(self, widget):
        date = widget.get_date().format('%F')
        txt = f'{date} was selected in calendar'
        markup = f'<span foreground="#00ffff" weight="bold">{txt}</span>'
        self.page4_label.set_markup(markup)

    def on_entry_activate(self, widget):
        txt = f'{widget.get_buffer().get_text()} was typed in entry'
        markup = f'<span foreground="#00ffff" weight="bold">{txt}</span>'
        self.page4_label.set_markup(markup)


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
