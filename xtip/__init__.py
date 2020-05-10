
import sys

from xtip.xtip import application, Quit


def main() -> int:
    try:
        return application(sys.argv[1:])
    except Quit:
        return 0

    return 0
