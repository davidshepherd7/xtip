from abc import abstractmethod
from subprocess import check_output, check_call, run
from typing import List

from xtip.exceptions import Quit


class Ui:
    # TODO: return None for "user quit" instead of throwing?
    @abstractmethod
    def display_menu(self, options: List[str]) -> str:
        pass

    @abstractmethod
    def display_result(self, text: str) -> None:
        pass


class UnixToolsUi(Ui):
    def display_menu(self, options: List[str]) -> str:
        names = "\n".join(options).encode("utf-8")
        try:
            dmenu_result = check_output(
                ["dmenu", "-p", "select command: ", "-i"], input=names
            )
        except Exception:
            print("Dmenu failed which normally means the user hit escape, quitting")
            raise Quit()

        return dmenu_result.strip().decode("utf-8")

    def display_result(self, text: str) -> None:
        # TODO: log stderr?
        check_call(
            [
                "zenity",
                "--info",
                "--width",
                "600",
                "--height",
                "400",
                "--text",
                text + "\n\nResult copied to X selection.",
            ]
        )
