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
from widgets import Window, Stack, MenuButton, get_font_markup


APP_MENU = """
<?xml version="1.0" encoding="UTF-8"?>
<interface>
<menu id='app-menu'>
  <section>
    <item>
      <attribute name='label' translatable='yes'>_New Window</attribute>
      <attribute name='action'>win.new</attribute>
    </item>
    <item>
      <attribute name='label' translatable='yes'>_About Sunny</attribute>
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
        # Add Menu Button
        menu = MenuButton(APP_MENU, 'app-menu')
        self.headerbar.pack_end(menu.widget)
        self.add_action('new', self.menu_handler)
        self.add_action('about', self.menu_handler)
        self.add_action('quit', self.menu_handler)
        # Add Stack
        self.stack = Stack()
        # Stack Page 1
        self.page1 = self.add_page('page1', 'Page 1')
        # Stack Page 2
        self.page2 = self.add_page('page2', 'Page 2')
        # add Switcher to center of titlebar
        self.headerbar.set_title_widget(self.stack.switcher)
        # Add stack to window
        self.window.set_child(self.stack.widget)

    def add_page(self, name, title):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        label = Gtk.Label()
        markup = get_font_markup('Noto Sans Regular 32', f'This is {title}')
        label.set_markup(markup)
        # fill the whole page
        label.set_hexpand(True)
        label.set_vexpand(True)
        box.append(label)
        return self.stack.add_page(name, title, box)

    def menu_handler(self, action, state):
        name = action.get_name()
        print(f'active : {name}')
        if name == 'quit':
            self.window.close()


def on_activate(app):
    mywin = MyWindow(app, "My Application", 800, 800)
    Gtk.Widget.show(mywin.window)


app = Gtk.Application(application_id='dk.rasmil.Example')
app.connect('activate', on_activate)
app.run(None)
