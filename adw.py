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
gi.require_version("Adw", "1")

from gi.repository import Gtk, GObject, Gio, Adw
from widgets import ColumnViewListStore


class ColumnElem(GObject.GObject):
    """custom data element for a ColumnView model (Must be based on GObject)"""

    def __init__(self, name: str):
        super(ColumnElem, self).__init__()
        self.name = name

    def __repr__(self):
        return f"ColumnElem(name: {self.name})"


class MyColumnViewColumn(ColumnViewListStore):
    """Custom ColumnViewColumn"""

    def __init__(
        self, win: Gtk.ApplicationWindow, col_view: Gtk.ColumnView, data: List
    ):
        # Init ListView with store model class.
        super(MyColumnViewColumn, self).__init__(ColumnElem, col_view)
        self.win = win
        # put some data into the model
        for elem in data:
            self.add(ColumnElem(elem))

    def factory_setup(self, widget, item: Gtk.ListItem):
        """Gtk.SignalListItemFactory::setup signal callback
        Handles the creation widgets to put in the ColumnViewColumn
        """
        label = Gtk.Label()
        label.set_halign(Gtk.Align.START)
        label.set_hexpand(True)
        label.set_margin_start(10)
        item.set_child(label)

    def factory_bind(self, widget, item: Gtk.ListItem):
        """Gtk.SignalListItemFactory::bind signal callback
        Handles adding data for the model to the widgets created in setup
        """
        label = item.get_child()  # Get the Gtk.Label stored in the ListItem
        data = item.get_item()  # get the model item, connected to current ListItem
        label.set_text(data.name)  # Update Gtk.Label with data from model item


class MyWindow(Adw.ApplicationWindow):
    def __init__(self, title, width, height, **kwargs):
        super(MyWindow, self).__init__(**kwargs)
        self.set_default_size(width, height)
        box = Gtk.Box()
        box.props.orientation = Gtk.Orientation.VERTICAL
        header = Gtk.HeaderBar()
        stack = Adw.ViewStack()
        switcher = Adw.ViewSwitcherTitle()
        switcher.set_stack(stack)
        header.set_title_widget(switcher)
        box.append(header)
        content = self.setup_content()
        page1 = stack.add_titled(content, "page1", "Page 1")
        box_p2 = Gtk.Box()
        page2 = stack.add_titled(box_p2, "page2", "Page 2")
        box.append(stack)
        self.set_content(box)

    def setup_content(self):
        """Add a page with a text selector to the stack"""
        # ColumnView with custom columns
        self.columnview = Gtk.ColumnView()
        self.columnview.set_show_column_separators(True)
        data = [f"Data Row: {row}" for row in range(5000)]
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
        return lw_frame


class Application(Adw.Application):
    """Main Aplication class"""

    def __init__(self):
        super().__init__(
            application_id="dk.rasmil.Example", flags=Gio.ApplicationFlags.FLAGS_NONE
        )

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = MyWindow("My Gtk4 Application", 800, 800, application=self)
        win.present()


def main():
    """Run the main application"""
    app = Application()
    return app.run(sys.argv)


if __name__ == "__main__":
    main()
