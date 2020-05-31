from typing import Any, List, Callable

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

from xtip.ui import Ui
from xtip.exceptions import Quit


def _configure_window(win: Any) -> None:

    # Hide toolbar etc
    win.set_decorated(False)

    # Hopefully tell window managers to float this window near the mouse
    win.set_keep_above(True)
    # win.set_modal_hint(True)
    win.set_position(Gtk.WindowPosition.MOUSE)

    # This is helpful to configure window managers to float this window
    win.set_wmclass("davidshepherd7.xtip", "davidshepherd7.xtip")

    win.connect("focus-out-event", lambda a, b: win.close())
    win.connect("destroy", Gtk.main_quit)


class DisplayTextWindow(Gtk.Window):
    # TODO: this is ugly as hell
    def __init__(self, text: str):
        Gtk.Window.__init__(self, title="XTip", default_width=600)
        _configure_window(self)
        self.add(Gtk.Label(text, selectable=True))


class MenuWindow(Gtk.Window):
    def __init__(self, options: List[str], report: Callable[[str], None]) -> None:
        Gtk.Window.__init__(self, title="XTip", default_width=600)
        _configure_window(self)
        self.report = report

        vbox = Gtk.VBox(spacing=2)

        buttonlist = []
        for label in options:
            b = Gtk.Button(label, name=label)
            b.connect("clicked", self.on_click)
            buttonlist.append(b)
            vbox.pack_start(b, True, True, 0)

        self.add(vbox)

    def on_click(self, button: Any) -> None:
        self.report(button.props.label)
        self.close()


# TODO: Does it improve anything if I use a single Gtk.main call?


class GtkUi(Ui):
    def display_menu(self, options: List[str]) -> str:

        # TODO: Nasty hacks here to return data from a gtk window, there's
        # probably a better way.
        out = None

        def store(x: str) -> None:
            nonlocal out
            out = x

        css = b"""
        button {
            margin: 0.2em;
        }
        """

        style_provider = Gtk.CssProvider()
        style_provider.load_from_data(css)

        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

        win = MenuWindow(options, store)
        win.show_all()
        Gtk.main()

        # If out is still None, then no buttons were clicked but we quit the
        # window. That means the user closed the tooltip.
        if out is None:
            raise Quit()

        return out

    def display_result(self, text: str) -> None:
        css = b"""
        button {
            margin: 0.2em;
        }
        """

        style_provider = Gtk.CssProvider()
        style_provider.load_from_data(css)

        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

        win = DisplayTextWindow(text)
        win.show_all()
        Gtk.main()
