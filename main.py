#  Copyright (C) 2021 Tim Lauridsen < tla[at]rasmil.dk >
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to
#  the Free Software Foundation, Inc.,
#  51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
#

"""
Sample Python Gtk4 Application
"""
import sys
import time
from typing import List

import gi

gi.require_version("Gtk", "4.0")
gi.require_version('Polkit', '1.0')

from gi.repository import Gtk, Polkit, GObject, Gio
from widgets import Window, Stack, MenuButton, get_font_markup, SearchBar, \
    IconSelector, TextSelector, ListViewStrings, ListViewListStore, SwitchRow, ButtonRow, MaterialColorDialog, ColumnViewListStore


def get_permision(action_id='org.freedesktop.accounts.user-administration'):
    """
    Get an GPermission object from PolKit to use with Gtk.LockButton
    @param action_id: is just an example there exist on at Fedora 34 workstation
    """
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
      <attribute name='label' translatable='yes'>_Shortcuts</attribute>
      <attribute name='action'>win.shortcuts</attribute>
    </item>
    <item>
      <attribute name='label' translatable='yes'>_Quit</attribute>
      <attribute name='action'>win.quit</attribute>
    </item>
  </section>
</menu>
</interface>
"""


class ColumnElem(GObject.GObject):
    """ custom data element for a ColumnView model (Must be based on GObject) """

    def __init__(self, name: str):
        super(ColumnElem, self).__init__()
        self.name = name

    def __repr__(self):
        return f'ColumnElem(name: {self.name})'


class ListElem(GObject.GObject):
    """ custom data element for a ListView model (Must be based on GObject) """

    def __init__(self, name: str, state: bool):
        super(ListElem, self).__init__()
        self.name = name
        self.state = state

    def __repr__(self):
        return f'ListElem(name: {self.name} state: {self.state})'


class MyListViewStrings(ListViewStrings):
    """ Custom ListView """

    def __init__(self, win: Gtk.ApplicationWindow):
        # Init ListView with store model class.
        super(MyListViewStrings, self).__init__()
        self.win = win
        self.set_vexpand(True)
        # put some data into the model
        for i in range(1000):
            self.add(f'Item {i}')

    def factory_setup(self, widget: Gtk.ListView, item: Gtk.ListItem):
        """ Gtk.SignalListItemFactory::setup signal callback (overloaded from parent class)

        Handles the creation widgets to put in the ListView
        """
        label = Gtk.Label()
        label.set_halign(Gtk.Align.START)
        label.set_hexpand(True)
        label.set_margin_start(10)
        item.set_child(label)

    def factory_bind(self, widget: Gtk.ListView, item: Gtk.ListItem):
        """ Gtk.SignalListItemFactory::bind signal callback (overloaded from parent class)

        Handles adding data for the model to the widgets created in setup
        """
        # get the Gtk.Label
        label = item.get_child()
        # get the model item, connected to current ListItem
        data = item.get_item()
        # Update Gtk.Label with data from model item
        label.set_text(data.get_string())
        # Update Gtk.Switch with data from model item
        item.set_child(label)

    def selection_changed(self, widget, ndx: int):
        """ trigged when selecting in listview is changed"""
        markup = self.win._get_text_markup(
            f'Row {ndx} was selected ( {self.store[ndx].get_string()} )')
        self.win.page4_label.set_markup(markup)


class MyListView(ListViewListStore):
    """ Custom ListView """

    def __init__(self, win: Gtk.ApplicationWindow):
        # Init ListView with store model class.
        super(MyListView, self).__init__(ListElem)
        self.win = win
        self.set_valign(Gtk.Align.FILL)
        # self.set_vexpand(True)
        # put some data into the model
        self.add(ListElem("One", True))
        self.add(ListElem("Two", False))
        self.add(ListElem("Three", True))
        self.add(ListElem("Four", False))

    def factory_setup(self, widget: Gtk.ListView, item: Gtk.ListItem):
        """ Gtk.SignalListItemFactory::setup signal callback (overloaded from parent class)

        Handles the creation widgets to put in the ListView
        """
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

    def factory_bind(self, widget: Gtk.ListView, item: Gtk.ListItem):
        """ Gtk.SignalListItemFactory::bind signal callback (overloaded from parent class)

        Handles adding data for the model to the widgets created in setup
        """
        # get the Gtk.Box stored in the ListItem
        box = item.get_child()
        # get the model item, connected to current ListItem
        data = item.get_item()
        # get the Gtk.Label (first item in box)
        label = box.get_first_child()
        # get the Gtk.Switch (next sibling to the Label)
        switch = label.get_next_sibling()
        # Update Gtk.Label with data from model item
        label.set_text(data.name)
        # Update Gtk.Switch with data from model item
        switch.set_state(data.state)
        # connect switch to handler, so we can handle changes
        switch.connect('state-set', self.switch_changed, item.get_position())
        item.set_child(box)

    def factory_unbind(self, widget: Gtk.ListView, item: Gtk.ListItem):
        """ Gtk.SignalListItemFactory::unbind signal callback (overloaded from parent class) """
        pass

    def factory_teardown(self, widget: Gtk.ListView, item: Gtk.ListItem):
        """ Gtk.SignalListItemFactory::teardown signal callback (overloaded from parent class """
        pass

    def selection_changed(self, widget, ndx: int):
        """ trigged when selecting in listview is changed"""
        markup = self.win._get_text_markup(
            f'Row {ndx} was selected ( {self.store[ndx]} )')
        self.win.page4_label.set_markup(markup)

    def switch_changed(self, widget, state: bool, pos: int):
        # update the data model, with current state
        elem = self.store[pos]
        elem.state = state
        markup = self.win._get_text_markup(
            f'switch in row {pos}, changed to {state}')
        self.win.page4_label.set_markup(markup)


class MyColumnViewColumn (ColumnViewListStore):
    """ Custom ColumnViewColumn """

    def __init__(self, win: Gtk.ApplicationWindow, col_view: Gtk.ColumnView, data: List):
        # Init ListView with store model class.
        super(MyColumnViewColumn, self).__init__(ColumnElem, col_view)
        self.win = win
        # put some data into the model
        for elem in data:
            self.add(ColumnElem(elem))

    def factory_setup(self, widget, item: Gtk.ListItem):
        """ Gtk.SignalListItemFactory::setup signal callback 
        Handles the creation widgets to put in the ColumnViewColumn
        """
        label = Gtk.Label()
        label.set_halign(Gtk.Align.START)
        label.set_hexpand(True)
        label.set_margin_start(10)
        item.set_child(label)

    def factory_bind(self, widget, item: Gtk.ListItem):
        """ Gtk.SignalListItemFactory::bind signal callback 
        Handles adding data for the model to the widgets created in setup
        """
        label = item.get_child()  # Get the Gtk.Label stored in the ListItem
        data = item.get_item()    # get the model item, connected to current ListItem
        label.set_text(data.name)  # Update Gtk.Label with data from model item

    def selection_changed(self, widget, ndx: int):
        """ trigged when selecting in listview is changed"""
        markup = self.win._get_text_markup(
            f'Row {ndx} was selected ( {self.store[ndx]} )')
        self.win.page4_label.set_markup(markup)


class MyWindow(Window):

    def __init__(self, title, width, height, **kwargs):
        super(MyWindow, self).__init__(title, height, width, **kwargs)
        # load the custom css, so we can use it later
        self.load_css('main.css')
        self.revealer = None
        # Add Menu Button to the titlebar (Right Side)
        menu = MenuButton(APP_MENU, 'app-menu')
        self.headerbar.pack_end(menu)
        # Create actions to handle menu actions
        self.create_action('new', self.menu_handler)
        self.create_action('about', self.menu_handler)
        self.create_action('quit', self.menu_handler)
        self.create_action('shortcuts', self.menu_handler)

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
        self.search = SearchBar(self)
        content.append(self.search)
        # search bar is active by default
        self.search.set_callback(self.on_search)

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
        content.append(self.stack)
        # Add main content box to window
        self.set_child(content)

    def setup_page_header(self, name, title):
        """ setup the common widgets for each page """
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
        label.set_margin_top(20)
        markup = get_font_markup('Noto Sans Regular 20', f'This is {title}')
        label.set_markup(markup)
        label.set_valign(Gtk.Align.CENTER)
        content.append(label)
        # Output label to write user action on the page
        label = Gtk.Label()
        label.set_margin_top(20)
        label.set_margin_start(20)
        label.set_hexpand(True)
        label.set_halign(Gtk.Align.CENTER)
        label.set_xalign(0.0)
        content.append(label)
        frame.set_child(content)
        return frame, content, label

    def setup_page_one(self, name, title):
        """ Add a page with a icon selector to the stack"""
        # Main Content box for the page
        main = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        # Add info selector
        selector = IconSelector()
        selector.add_row("row1", "dialog-information-symbolic")
        selector.add_row("row2", "software-update-available-symbolic")
        selector.add_row("row3", "drive-multidisk-symbolic")
        selector.add_row("row4", "insert-object-symbolic")
        selector.set_callback(self.on_select_icon_selector)
        main.append(selector)
        page_frame, content_right, lbl = self.setup_page_header(name, title)
        self.page1_label = lbl
        # Lock button
        lock_btn = Gtk.LockButton.new(get_permision())
        lock_btn.set_margin_top(20)
        lock_btn.set_halign(Gtk.Align.CENTER)
        lock_btn.set_hexpand(False)
        content_right.append(lock_btn)
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
        content_right.append(box)
        # Entry
        entry = Gtk.Entry()
        entry.set_halign(Gtk.Align.FILL)
        entry.set_valign(Gtk.Align.END)
        entry.set_margin_top(20)
        entry.set_margin_start(20)
        entry.set_margin_end(20)
        entry.set_placeholder_text("Type something here ....")
        entry.connect('activate', self.on_entry_activate)
        content_right.append(entry)
        # Calendar
        calendar = Gtk.Calendar()
        calendar.set_margin_top(20)
        calendar.set_halign(Gtk.Align.CENTER)
        calendar.connect('day-selected', self.on_calendar_changed)
        content_right.append(calendar)
        # DropDown
        model = Gtk.StringList()
        for txt in ['One', 'Two', 'Three', 'Four']:
            model.append(txt)
        dropdown = Gtk.DropDown.new(model)
        dropdown.set_margin_top(20)
        dropdown.set_margin_start(20)
        dropdown.set_size_request(200, -1)
        dropdown.set_halign(Gtk.Align.START)
        content_right.append(dropdown)
        # DropDown
        dropdown = Gtk.DropDown.new_from_strings(
            ['Red', 'Green', 'Blue', 'Black', 'White'])
        dropdown.set_margin_top(20)
        dropdown.set_margin_start(20)
        dropdown.set_size_request(200, -1)
        dropdown.set_halign(Gtk.Align.START)
        content_right.append(dropdown)
        main.append(page_frame)
        # Add the content box as a new page in the stack
        return self.stack.add_page(name, title, main)

    def setup_page_two(self, name, title):
        """ Add a page with a text selector to the stack"""
        # Content box for the page
        main = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        # Add info selector
        selector = TextSelector()
        selector.add_row("Orange", "Orange")
        selector.add_row("Apple", "Apple")
        selector.add_row("Water Melon", "Water Melon")
        selector.add_row("Lollypop", "Lollypop")
        selector.set_callback(self.on_select_text_selector)
        main.append(selector)
        # Add a label with custom font in the center
        frame, content_right, label = self.setup_page_header(name, title)
        self.page2_label = label
        # Overlay
        overlay_info = Gtk.InfoBar()
        overlay_info.set_halign(Gtk.Align.FILL)
        overlay_info.set_valign(Gtk.Align.START)
        overlay_info.set_margin_top(10)
        overlay_info.set_margin_start(10)
        overlay_info.set_margin_end(10)
        lbl = Gtk.Label()
        lbl.set_halign(Gtk.Align.FILL)
        lbl.set_valign(Gtk.Align.FILL)
        lbl.set_hexpand(True)
        lbl.set_vexpand(True)
        lbl.set_markup(
            '<span foreground="#ff0000" size="xx-large">This is an Gtk.Infobar as an overlay</span>')
        overlay_info.add_child(lbl)
        self.overlay_info = overlay_info
        frame_child = Gtk.Frame()
        # TexkView
        sw = Gtk.ScrolledWindow()
        text = Gtk.TextView.new()
        text.set_vexpand(True)
        # Set Wrap Mode to word
        text.set_wrap_mode(Gtk.WrapMode.WORD)
        # Add some text
        txt = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras vitae leo ac magna lobortis maximus. ' \
              'Etiam eleifend, libero a pulvinar ornare, justo nunc porta velit, ut sodales mi est feugiat tellus. '
        text.get_buffer().set_text(txt * 10)
        sw.set_child(text)
        frame_child.set_child(sw)
        overlay = Gtk.Overlay()
        overlay.set_margin_top(20)
        overlay.set_margin_start(20)
        overlay.set_margin_end(20)
        overlay.set_margin_bottom(20)
        overlay.set_child(frame_child)
        overlay.add_overlay(overlay_info)
        content_right.append(overlay)
        # Switch to control overlay visibility
        switch_row = SwitchRow("Show Overlay")
        switch_row.set_state(True)
        switch_row.connect('state-set', self.on_switch_overlay)
        content_right.append(switch_row)
        main.append(frame)
        # Add the content box as a new page in the stack
        return self.stack.add_page(name, title, main)

    def setup_page_three(self, name, title):
        """ Add a page with css styled content to the stack"""
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
        self.left_right_paned = Gtk.Paned(
            orientation=Gtk.Orientation.HORIZONTAL)
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
        markup = get_font_markup(
            'Noto Sans Regular 24', f'This page is styled using main.css')
        label.set_markup(markup)
        # fill the whole page, will make the Label centered.
        label.set_halign(Gtk.Align.CENTER)
        label.set_vexpand(False)
        self.bottom_box.append(label)
        label = Gtk.Label()
        markup = get_font_markup(
            'Noto Sans Regular 18', f'UGLY AS HELL, but shows how it is working')
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
        frame, content, label = self.setup_page_header(name, title)
        self.page4_label = label

        # ColumnView with custom columns
        self.columnview = Gtk.ColumnView()
        self.columnview.set_show_column_separators(True)
        data = [f'Data Row: {row}' for row in range(50)]
        for i in range(4):
            column = MyColumnViewColumn(self, self.columnview, data)
            column.set_title(f"Column {i}")
            self.columnview.append_column(column)
        lw_frame = Gtk.Frame()
        lw_frame.set_valign(Gtk.Align.FILL)
        lw_frame.set_vexpand(True)
        lw_frame.set_margin_start(20)
        lw_frame.set_margin_end(20)
        lw_frame.set_margin_top(10)
        lw_frame.set_margin_bottom(10)
        sw = Gtk.ScrolledWindow()
        sw.set_child(self.columnview)
        lw_frame.set_child(sw)
        content.append(lw_frame)

        # Listview with switches
        self.listview = MyListView(self)
        lw_frame = Gtk.Frame()
        lw_frame.set_valign(Gtk.Align.FILL)
        lw_frame.set_vexpand(True)
        lw_frame.set_margin_start(20)
        lw_frame.set_margin_end(20)
        # lw_frame.set_margin_top(10)
        lw_frame.set_margin_bottom(10)
        sw = Gtk.ScrolledWindow()
        sw.set_child(self.listview)
        lw_frame.set_child(sw)
        content.append(lw_frame)
        # Simple Listview with strings
        self.listview_str = MyListViewStrings(self)
        lw_frame = Gtk.Frame()
        lw_frame.set_valign(Gtk.Align.FILL)
        lw_frame.set_vexpand(True)
        lw_frame.set_margin_start(20)
        lw_frame.set_margin_end(20)
        # lw_frame.set_margin_top(10)
        lw_frame.set_margin_bottom(10)
        sw = Gtk.ScrolledWindow()
        # Create Gtk.Listview
        lw = self.listview_str
        sw.set_child(lw)
        lw_frame.set_child(sw)
        content.append(lw_frame)
        frame.set_child(content)
        # Add the content box as a new page in the stack
        return self.stack.add_page(name, title, frame)

    def setup_page_five(self, name, title):
        """ Add a new page to the stack"""
        # Content box for the page
        frame, content, label = self.setup_page_header(name, title)
        self.page5_label = label
        # Material Color button
        btn_row = ButtonRow(["Material Color"], self.on_button_chooser)
        content.append(btn_row)
        # Add the content box as a new page in the stack
        return self.stack.add_page(name, title, frame)

    def _get_text_markup(self, txt):
        txt = f'<span foreground="#BF360C" weight="bold">{txt}</span>'
        markup = get_font_markup('Noto Sans Regular 14', txt)
        return markup

    def show_shortcuts(self):
        builder = Gtk.Builder.new_from_file('shortcuts.ui')
        shortcuts = builder.get_object('shortcuts')
        shortcuts.present()

    # ---------------------- Handlers --------------------------

    def menu_handler(self, action, state):
        """ Callback for  menu actions"""
        name = action.get_name()
        print(f'active : {name}')
        if name == 'quit':
            self.close()
        elif name == 'shortcuts':
            self.show_shortcuts()

    def on_color_selected(self, widget):
        selected_color = self.chooser.get_rgba()
        color_txt = selected_color.to_string()
        markup = self._get_text_markup(
            f'{widget.get_label()} was pressed. {color_txt}')
        self.page5_label.set_markup(markup)

    def on_button_chooser(self, widget):
        """ callback for buttom clicked (Page1) """
        dialog = MaterialColorDialog("Select Color", self)
        dialog.connect('response', self.on_dialog_response)
        dialog.show()

    def on_search(self, widget):
        """ callback for the searchbar entry """
        print(f'Searching for : {widget.get_text()}')

    def on_select_icon_selector(self, name):
        """ called when icon_selector selection is changed (Page1) """
        markup = self._get_text_markup(f'{name} is selected')
        self.page1_label.set_markup(markup)

    def on_select_text_selector(self, name):
        """ called when text_selector is changed (Page2) """
        markup = self._get_text_markup(f'{name} is selected')
        self.page2_label.set_markup(markup)

    def on_switch_activate(self, widget, state):
        """ callback for reveal switch (Page3) """
        if self.revealer:
            self.revealer.set_reveal_child(state)
            time.sleep(.5)
            self.top_botton_paned.set_position(1000)

    def on_switch_overlay(self, widget, state):
        """ callback for overlay switch (Page2) """
        if self.overlay_info:
            self.overlay_info.set_revealed(state)

    def on_button_clicked(self, widget):
        """ callback for buttom clicked (Page1) """
        markup = self._get_text_markup(f'{widget.get_label()} was pressed')
        self.page1_label.set_markup(markup)

    def on_calendar_changed(self, widget):
        """ callback for calendar selection (Page1) """
        date = widget.get_date().format('%F')
        txt = f'{date} was selected in calendar'
        markup = self._get_text_markup(txt)
        self.page1_label.set_markup(markup)

    def on_entry_activate(self, widget):
        """ callback for entry actication (Page1) """
        txt = f'{widget.get_buffer().get_text()} was typed in entry'
        markup = self._get_text_markup(txt)
        self.page1_label.set_markup(markup)

    def on_dialog_response(self, widget, response_id):
        if response_id == Gtk.ResponseType.OK:
            # get selected color in hex format
            color = widget.get_color()
            markup = f'<span size="xx-large" foreground="{color}">the color {color} was selected</span>'
            self.page5_label.set_markup(markup)
        elif response_id == Gtk.ResponseType.CANCEL:
            print("cancel")
            # if the messagedialog is destroyed (by pressing ESC)
        elif response_id == Gtk.ResponseType.DELETE_EVENT:
            print("dialog closed or cancelled")
        widget.destroy()


class Application(Gtk.Application):
    """ Main Aplication class """

    def __init__(self):
        super().__init__(application_id='dk.rasmil.Example',
                         flags=Gio.ApplicationFlags.FLAGS_NONE)

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = MyWindow("My Gtk4 Application", 800, 800, application=self)
        win.present()


def main():
    """ Run the main application"""
    app = Application()
    return app.run(sys.argv)


if __name__ == '__main__':
    main()
