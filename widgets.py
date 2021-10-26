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
Misc classes to build Gtk4 Applications in python 3.9

It takes some of the hassle away from building Gtk4 application in Python
So you can create an cool application, without all the boilerplate code

"""
import os.path

from abc import abstractmethod

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, GLib, Gdk

from material import MATERIAL


def rgb_to_hex(r, g, b):
    if isinstance(r, float):
        r *= 255
        g *= 255
        b *= 255
    return "#{0:02X}{1:02X}{2:02X}".format(int(r), int(g), int(b))


def color_to_hex(color):
    return rgb_to_hex(color.red, color.green, color.blue)


def get_font_markup(fontdesc, text):
    return f'<span font_desc="{fontdesc}">{text}</span>'


class MaterialColorDialog(Gtk.ColorChooserDialog):
    """ Color chooser dialog with Material design colors """

    def __init__(self, title, parent):
        Gtk.ColorChooserDialog.__init__(self)
        self.set_title(title)
        self.set_transient_for(parent)
        self.set_modal(True)
        # build list of material colors in Gdk.RGBA format
        color_values = []
        for color_name in MATERIAL.colors:
            colors = MATERIAL.get_palette(color_name)
            for col in colors:
                color = Gdk.RGBA()
                color.parse(col)
                color_values.append(color)
        num_colors = 14
        self.add_palette(Gtk.Orientation.HORIZONTAL, num_colors, color_values)
        self.set_property('show-editor', False)

    def get_color(self):
        selected_color = self.get_rgba()
        return color_to_hex(selected_color)


class ListViewBase(Gtk.ListView):
    """ ListView base class, it setup the basic factory, selection model & data model
    handlers must be overloaded & implemented in a sub class
    """

    def __init__(self, model_cls):
        Gtk.ListView.__init__(self)
        # Use the signal Factory, so we can connect our own methods to setup
        self.factory = Gtk.SignalListItemFactory()
        # connect to Gtk.SignalListItemFactory signals
        # check https://docs.gtk.org/gtk4/class.SignalListItemFactory.html for details
        self.factory.connect('setup', self.on_factory_setup)
        self.factory.connect('bind', self.on_factory_bind)
        self.factory.connect('unbind', self.on_factory_unbind)
        self.factory.connect('teardown', self.on_factory_teardown)
        # Create data model, use our own class as elements
        self.set_factory(self.factory)
        self.store = self.setup_store(model_cls)
        # create a selection model containing our data model
        self.model = self.setup_model(self.store)
        self.model.connect('selection-changed', self.on_selection_changed)
        # set the selection model to the view
        self.set_model(self.model)

    def setup_model(self, store: Gio.ListModel) -> Gtk.SelectionModel:
        """  Setup the selection model to use in Gtk.ListView
        Can be overloaded in subclass to use another Gtk.SelectModel model
        """
        return Gtk.SingleSelection.new(store)

    @abstractmethod
    def setup_store(self, model_cls) -> Gio.ListModel:
        """ Setup the data model
        must be overloaded in subclass to use another Gio.ListModel
        """
        raise NotImplemented

    def add(self, elem):
        """ add element to the data model """
        self.store.append(elem)

    # Gtk.SignalListItemFactory signal callbacks
    # transfer to some some callback stubs, there can be overloaded in
    # a subclass.

    def on_factory_setup(self, widget, item: Gtk.ListItem):
        """ GtkSignalListItemFactory::setup signal callback

        Setup the widgets to go into the ListView """

        self.factory_setup(widget, item)

    def on_factory_bind(self, widget: Gtk.ListView, item: Gtk.ListItem):
        """ GtkSignalListItemFactory::bind signal callback

        apply data from model to widgets set in setup"""
        self.factory_bind(widget, item)

    def on_factory_unbind(self, widget, item: Gtk.ListItem):
        """ GtkSignalListItemFactory::unbind signal callback

        Undo the the binding done in ::bind if needed
        """
        self.factory_unbind(widget, item)

    def on_factory_teardown(self, widget, item: Gtk.ListItem):
        """ GtkSignalListItemFactory::setup signal callback

        Undo the creation done in ::setup if needed
        """
        self.factory_teardown(widget, item)

    def on_selection_changed(self, widget, position, n_items):
        # get the current selection (GtkBitset)
        selection = widget.get_selection()
        # the the first value in the GtkBitset, that contain the index of the selection in the data model
        # as we use Gtk.SingleSelection, there can only be one ;-)
        ndx = selection.get_nth(0)
        self.selection_changed(widget, ndx)

    # --------------------> abstract callback methods <--------------------------------
    # Implement these methods in your subclass

    @abstractmethod
    def factory_setup(self, widget: Gtk.ListView, item: Gtk.ListItem):
        """ Setup the widgets to go into the ListView (Overload in subclass) """
        pass

    @abstractmethod
    def factory_bind(self, widget: Gtk.ListView, item: Gtk.ListItem):
        """ apply data from model to widgets set in setup (Overload in subclass)"""
        pass

    @abstractmethod
    def factory_unbind(self, widget: Gtk.ListView, item: Gtk.ListItem):
        pass

    @abstractmethod
    def factory_teardown(self, widget: Gtk.ListView, item: Gtk.ListItem):
        pass

    @abstractmethod
    def selection_changed(self, widget, ndx):
        """ trigged when selecting in listview is changed
        ndx: is the index in the data store model that is selected
        """
        pass


class ListViewListStore(ListViewBase):
    """ ListView base with an Gio.ListStore as data model
    It can contain misc objects derived from GObject
    """

    def __init__(self, model_cls):
        super(ListViewListStore, self).__init__(model_cls)

    def setup_store(self, model_cls) -> Gio.ListModel:
        """ Setup the data model """
        return Gio.ListStore.new(model_cls)


class ListViewStrings(ListViewBase):
    """ Add ListView with only strings """

    def __init__(self):
        super(ListViewStrings, self).__init__(Gtk.StringObject)

    def setup_store(self, model_cls) -> Gio.ListModel:
        """ Setup the data model
        Can be overloaded in subclass to use another Gio.ListModel
        """
        return Gtk.StringList()


class SelectorBase(Gtk.ListBox):
    """ Selector base class """

    def __init__(self):
        Gtk.ListBox.__init__(self)
        # Setup the listbox
        self.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.connect('row-selected', self.on_row_changes)
        self._rows = {}
        self.ndx = 0
        self.callback = None

    def add_row(self, name, markup):
        """ Overload this in a subclass"""
        raise NotImplemented

    def on_row_changes(self, widget, row):
        ndx = row.get_index()
        if self.callback:
            self.callback(self._rows[ndx])
        else:
            print(f'Row Selected : {self._rows[ndx]}')

    def set_callback(self, callback):
        self.callback = callback


class TextSelector(SelectorBase):
    """ Vertical Selector Widget that contains a number of strings where one can be selected """

    def add_row(self, name: str, markup: str):
        """ Add a named row to the selector with at given icon name"""
        # get the image
        label = Gtk.Label()
        label.set_markup(markup)
        # set the widget size request to 32x32 px, so we get some margins
        # label.set_size_request(100, 24)
        label.set_single_line_mode(True)
        label.set_halign(Gtk.Align.START)
        label.set_hexpand(True)
        label.set_xalign(0)
        label.set_margin_start(5)
        label.set_margin_end(10)
        row = self.append(label)
        # store the index names, so we can find it on selection
        self._rows[self.ndx] = name
        self.ndx += 1


class IconSelector(SelectorBase):
    """ Vertical Selector Widget that contains a number of icons where one can be selected """

    def add_row(self, name, icon_name):
        """ Add a named row to the selector with at given icon name"""
        # get the image
        pix = Gtk.Image.new_from_icon_name(icon_name)
        # set the widget size request to 32x32 px, so we get some margins
        pix.set_size_request(32, 32)
        row = self.append(pix)
        # store the index names, so we can find it on selection
        self._rows[self.ndx] = name
        self.ndx += 1


class ViewColumnBase(Gtk.ColumnViewColumn):
    """ ColumnViewColumn base class, it setup the basic factory, selection model & data model
    handlers must be overloaded & implemented in a sub class
    """

    def __init__(self, model_cls, col_view):
        Gtk.ColumnViewColumn.__init__(self)
        self.col_view = col_view
        # Use the signal Factory, so we can connect our own methods to setup
        self.factory = Gtk.SignalListItemFactory()
        # connect to Gtk.SignalListItemFactory signals
        # check https://docs.gtk.org/gtk4/class.SignalListItemFactory.html for details
        self.factory.connect('setup', self.on_factory_setup)
        self.factory.connect('bind', self.on_factory_bind)
        self.factory.connect('unbind', self.on_factory_unbind)
        self.factory.connect('teardown', self.on_factory_teardown)
        # Create data model, use our own class as elements
        self.set_factory(self.factory)
        self.store = self.setup_store(model_cls)
        # create a selection model containing our data model
        self.model = self.setup_model(self.store)
        self.model.connect('selection-changed', self.on_selection_changed)
        # add model to the ColumnView
        self.col_view.set_model(self.model)

    def setup_model(self, store: Gio.ListModel) -> Gtk.SelectionModel:
        """  Setup the selection model to use in Gtk.ListView
        Can be overloaded in subclass to use another Gtk.SelectModel model
        """
        return Gtk.SingleSelection.new(store)

    @abstractmethod
    def setup_store(self, model_cls) -> Gio.ListModel:
        """ Setup the data model
        must be overloaded in subclass to use another Gio.ListModel
        """
        raise NotImplemented

    def add(self, elem):
        """ add element to the data model """
        self.store.append(elem)

    # Gtk.SignalListItemFactory signal callbacks
    # transfer to some some callback stubs, there can be overloaded in
    # a subclass.

    def on_factory_setup(self, widget, item: Gtk.ListItem):
        """ GtkSignalListItemFactory::setup signal callback

        Setup the widgets to go into the ListView """

        self.factory_setup(widget, item)

    def on_factory_bind(self, widget: Gtk.ListView, item: Gtk.ListItem):
        """ GtkSignalListItemFactory::bind signal callback

        apply data from model to widgets set in setup"""
        self.factory_bind(widget, item)

    def on_factory_unbind(self, widget, item: Gtk.ListItem):
        """ GtkSignalListItemFactory::unbind signal callback

        Undo the the binding done in ::bind if needed
        """
        self.factory_unbind(widget, item)

    def on_factory_teardown(self, widget, item: Gtk.ListItem):
        """ GtkSignalListItemFactory::setup signal callback

        Undo the creation done in ::setup if needed
        """
        self.factory_teardown(widget, item)

    def on_selection_changed(self, widget, position, n_items):
        # get the current selection (GtkBitset)
        selection = widget.get_selection()
        # the the first value in the GtkBitset, that contain the index of the selection in the data model
        # as we use Gtk.SingleSelection, there can only be one ;-)
        ndx = selection.get_nth(0)
        self.selection_changed(widget, ndx)

    # --------------------> abstract callback methods <--------------------------------
    # Implement these methods in your subclass

    @abstractmethod
    def factory_setup(self, widget: Gtk.ColumnViewColumn, item: Gtk.ListItem):
        """ Setup the widgets to go into the ColumnViewColumn (Overload in subclass) """
        pass

    @abstractmethod
    def factory_bind(self, widget: Gtk.ColumnViewColumn, item: Gtk.ListItem):
        """ apply data from model to widgets set in setup (Overload in subclass)"""
        pass

    @abstractmethod
    def factory_unbind(self, widget: Gtk.ColumnViewColumn, item: Gtk.ListItem):
        pass

    @abstractmethod
    def factory_teardown(self, widget: Gtk.ColumnViewColumn, item: Gtk.ListItem):
        pass

    @abstractmethod
    def selection_changed(self, widget, ndx):
        """ trigged when selecting in listview is changed
        ndx: is the index in the data store model that is selected
        """
        pass


class ColumnViewListStore(ViewColumnBase):
    """ ColumnViewColumn base with an Gio.ListStore as data model
    It can contain misc objects derived from GObject
    """

    def __init__(self, model_cls, col_view):
        super(ColumnViewListStore, self).__init__(model_cls, col_view)

    def setup_store(self, model_cls) -> Gio.ListModel:
        """ Setup the data model """
        return Gio.ListStore.new(model_cls)


class SearchBar(Gtk.SearchBar):
    """ Wrapper for Gtk.Searchbar Gtk.SearchEntry"""

    def __init__(self, win=None):
        super(SearchBar, self).__init__()
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
        self.set_child(box)
        # connect search entry to seach bar
        self.connect_entry(self.entry)
        if win:
            # set key capture from main window, it will show searchbar, when you start typing
            self.set_key_capture_widget(win)
        # show close button in search bar
        self.set_show_close_button(True)
        # Set search mode to off by default
        self.set_search_mode(False)

    def set_callback(self, callback):
        """ Connect the search entry activate to an callback handler"""
        self.entry.connect('activate', callback)


class ButtonRow(Gtk.Box):
    """ Row of button"""

    def __init__(self, btn_list: list, callback):
        super(ButtonRow, self).__init__(orientation=Gtk.Orientation.HORIZONTAL)
        # self.set_halign(Gtk.Align.CENTER)
        self.set_margin_start(20)
        self.set_margin_top(20)
        self.set_spacing(10)
        for title in btn_list:
            btn = Gtk.Button()
            btn.set_label(f'{title}')
            btn.connect('clicked', callback)
            self.append(btn)


class SwitchRow(Gtk.Box):
    def __init__(self, text):
        super(SwitchRow, self).__init__(orientation=Gtk.Orientation.HORIZONTAL)
        # Switch to control overlay visibility
        self.label = Gtk.Label.new(text)
        self.label.set_halign(Gtk.Align.FILL)
        self.label.set_valign(Gtk.Align.CENTER)
        self.label.set_hexpand(True)
        self.label.set_xalign(0.0)
        self.label.set_margin_start(20)
        self.label.set_margin_bottom(20)
        self.append(self.label)
        self.switch = Gtk.Switch()
        self.switch.set_halign(Gtk.Align.END)
        self.switch.set_margin_end(20)
        self.switch.set_margin_bottom(20)
        self.append(self.switch)

    def connect(self, signal, callback):
        self.switch.connect(signal, callback)

    def set_state(self, state):
        self.switch.set_state(state)


class MenuButton(Gtk.MenuButton):
    """
    Wrapper class for at Gtk.Menubutton with a menu defined
    in a Gtk.Builder xml string
    """

    def __init__(self, xml, name, icon_name='open-menu-symbolic'):
        super(MenuButton, self).__init__()
        builder = Gtk.Builder()
        builder.add_from_string(xml)
        menu = builder.get_object(name)
        self.set_menu_model(menu)
        self.set_icon_name(icon_name)


class Stack(Gtk.Stack):
    """ Wrapper for Gtk.Stack with  with a StackSwitcher """

    def __init__(self):
        super(Stack, self).__init__()
        self.switcher = Gtk.StackSwitcher()
        self.switcher.set_stack(self)
        self._pages = {}

    def add_page(self, name, title, widget):
        page = self.add_child(widget)
        page.set_name(name)
        page.set_title(title)
        self._pages[name] = page
        return page


class Window(Gtk.ApplicationWindow):
    """ custom Gtk.ApplicationWindow with a headerbar"""

    def __init__(self, title, width, height, **kwargs):
        super(Window, self).__init__(**kwargs)
        self.set_default_size(width, height)
        self.headerbar = Gtk.HeaderBar()
        self.set_titlebar(self.headerbar)
        label = Gtk.Label()
        label.set_text(title)
        self.headerbar.set_title_widget(label)
        # custom CSS provider
        self.css_provider = None

    def load_css(self, css_fn):
        """create a provider for custom styling"""
        if css_fn and os.path.exists(css_fn):
            css_provider = Gtk.CssProvider()
            try:
                css_provider.load_from_path(css_fn)
            except GLib.Error as e:
                print(f"Error loading CSS : {e} ")
                return None
            print(f'loading custom styling : {css_fn}')
            self.css_provider = css_provider

    def _add_widget_styling(self, widget):
        if self.css_provider:
            context = widget.get_style_context()
            context.add_provider(
                self.css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

    def add_custom_styling(self, widget):
        self._add_widget_styling(widget)
        # iterate children recursive
        for child in widget:
            self.add_custom_styling(child)

    def create_action(self, name, callback):
        """ Add an Action and connect to a callback """
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
