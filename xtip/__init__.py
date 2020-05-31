
import sys

from xtip.xtip import application
from xtip.exceptions import Quit


def main() -> int:
    try:
        return application(sys.argv[1:])
    except Quit:
        return 0

    return 0
