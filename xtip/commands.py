from typing import Optional, Any, List
from subprocess import run


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
