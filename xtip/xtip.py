from subprocess import check_output, check_call, run

from typing import Optional, List, Any


class Quit(Exception):
    pass


def get_x_selection() -> str:
    # TODO: log stderr?
    output = check_output(["xclip", "-o"])
    return output.decode("utf-8")


def set_x_selection(text: str) -> None:
    run(["xclip", "-i"], input=text.encode("utf-8"))


def sanitize(text: str) -> str:
    return text.strip().replace("\n", " ").replace("\t", " ")


def display(text: str) -> None:
    # TODO: log stderr?
    check_call(
        ["zenity", "--info", "--width", "600", "--height", "400", "--text", text]
    )


class Command:
    @property
    def unique_name(self) -> str:
        pass

    def run(self, text: str) -> Optional[str]:
        pass

    def accepts(self, text: str) -> bool:
        return True


ALL_COMMANDS: List[Command] = []


def command(c: Any) -> None:
    ALL_COMMANDS.append(c())


def pick_command(text: str) -> Command:
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


def application(argv: List[str]) -> int:

    selection = sanitize(get_x_selection())
    print("Got selection:", selection)

    try:
        command = pick_command(selection)
        print("Running command:", command.unique_name)
        result = command.run(selection)
        print("Finished sucessfully")
    except Quit:
        return 0
    except Exception as e:
        display("Command failed: " + str(e))
        raise

    if result is not None:
        print("Result was:", result)
        set_x_selection(result)
        display(result + "\n\nResult copied to X selection.")
    else:
        print("No result")

    return 0


########################################
# Commands
########################################


@command
class UnixTimestamp(Command):
    unique_name = "Parse unix timestamp"

    def run(self, text: str) -> Optional[str]:
        from datetime import datetime

        dt = datetime.utcfromtimestamp(int(text))
        return dt.strftime("%Y-%m-%d %H:%M:%S") + " UTC"

    def accepts(self, text: str) -> bool:
        return text.isnumeric()


@command
class GoogleTranslate(Command):
    """Depends on googletrans
    """

    unique_name = "Google translate"

    def run(self, text: str) -> Optional[str]:
        from googletrans import Translator

        translator = Translator()
        r = translator.translate(text)
        return f"Translated {r.src} to {r.dest}: {r.text}"

    def accepts(self, text: str) -> bool:
        return not text.isnumeric()


@command
class GoogleSearch(Command):
    unique_name = "Google search"

    def run(self, text: str) -> Optional[str]:
        import urllib.parse

        escaped = urllib.parse.quote(text)
        run(["sensible-browser", f"https://google.com/search?q={escaped}"])
        return None


@command
class Emacsclient(Command):
    unique_name = "Open in emacsclient"

    def run(self, text: str) -> Optional[str]:
        # TODO(david): Figure out a way to get the absolute path... maybe by
        # guessing from a few possible prefixes?
        run(["emacsclient", "-c", "-n", text])
        return None

    def accepts(self, text: str) -> bool:
        # TODO: allow relative paths
        return text.startswith("/") or text.startswith("~")
