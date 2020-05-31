from subprocess import check_output, check_call, run
import importlib.util
from typing import Optional, List, Any
import os.path

from xtip.ui import Ui, UnixToolsUi
from xtip.exceptions import Quit

# Load the commands
import xtip.commands
from xtip.commands import Command, ALL_COMMANDS


# TODO: could probably eliminate xclip dependency in Gtk UI by using Gtk
# clipboard. Maybe we could even do it with a pure python library?


def _get_x_selection() -> str:
    # TODO: log stderr?
    output = check_output(["xclip", "-o"])
    return output.decode("utf-8")


def _set_clipboard(text: str) -> None:
    run(["xclip", "-i", "-selection", "clipboard"], input=text.encode("utf-8"))


def _sanitize(text: str) -> str:
    return text.strip().replace("\n", " ").replace("\t", " ")


def _pick_command(ui: Ui, text: str) -> Command:
    commands = [c for c in ALL_COMMANDS if c.accepts(text)]

    if len(commands) == 0:
        raise Exception("No possible commands")

    if len(commands) == 1:
        return commands[0]

    selected = ui.display_menu([c.unique_name for c in commands])
    return next(c for c in commands if c.unique_name == selected)


def _load_user_commands(config_path: str) -> None:
    if os.path.exists(config_path):
        spec = importlib.util.spec_from_file_location("config", config_path)
        config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config)  # type: ignore


def application(argv: List[str]) -> int:

    # Load the user's custom commands
    config_path = os.path.expanduser("~/.config/xtip/custom_commands.py")
    _load_user_commands(config_path)

    ui_type = "unix"
    # ui_type = "gtk"

    ui: Ui
    if ui_type == "unix":
        ui = UnixToolsUi()
    elif ui_type == "gtk":
        from xtip.ui_gtk import GtkUi

        ui = GtkUi()

    selection = _sanitize(_get_x_selection())
    print("Got X11 selection:", selection)

    try:
        command = _pick_command(ui, selection)
    except Quit:
        print("User quit")
        return 0

    try:
        print(f"Running command: {command.unique_name}")
        result = command.run(selection)
        print(f"Command {command.unique_name} finished sucessfully")
    except Exception as e:
        ui.display_result(f"Command {command.unique_name} failed with error: " + str(e))
        raise

    if result is not None:
        print("Result was:", result)
        _set_clipboard(result)
        ui.display_result(result)
    else:
        print("No result")

    return 0
