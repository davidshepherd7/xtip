from subprocess import check_output, check_call, run
import importlib.util
from typing import Optional, List, Any
import os.path

# Load the commands
import xtip.commands
from xtip.commands import Command, ALL_COMMANDS


class Quit(Exception):
    pass


def _get_x_selection() -> str:
    # TODO: log stderr?
    output = check_output(["xclip", "-o"])
    return output.decode("utf-8")


def _set_x_selection(text: str) -> None:
    run(["xclip", "-i"], input=text.encode("utf-8"))


def _sanitize(text: str) -> str:
    return text.strip().replace("\n", " ").replace("\t", " ")


def _display(text: str) -> None:
    # TODO: log stderr?
    check_call(
        ["zenity", "--info", "--width", "600", "--height", "400", "--text", text]
    )


def _pick_command(text: str) -> Command:
    commands = [c for c in ALL_COMMANDS if c.accepts(text)]

    if len(commands) == 0:
        raise Exception("No possible commands")

    if len(commands) == 1:
        return commands[0]

    names = "\n".join(c.unique_name for c in commands).encode("utf-8")
    try:
        dmenu_result = check_output(
            ["dmenu", "-p", "select command: ", "-i"], input=names
        )
    except Exception:
        print("Dmenu failed which normally means the user hit escape, quitting")
        raise Quit()

    selected = dmenu_result.strip().decode("utf-8")
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

    selection = _sanitize(_get_x_selection())
    print("Got selection:", selection)

    try:
        command = _pick_command(selection)
        print("Running command:", command.unique_name)
        result = command.run(selection)
        print("Finished sucessfully")
    except Quit:
        return 0
    except Exception as e:
        _display("Command failed: " + str(e))
        raise

    if result is not None:
        print("Result was:", result)
        _set_x_selection(result)
        _display(result + "\n\nResult copied to X selection.")
    else:
        print("No result")

    return 0
