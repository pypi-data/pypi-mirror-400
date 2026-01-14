# colors.py

"""
Mini project generating text with ansi color codes
"""

import argparse
import re

from .__about__ import __version__, APPNAME

NL = chr(10)


# ANSI codes:
# # style
BLD = "\033[1m"
ITL = "\033[3m"
# # color
GRY = "\x1b[38;2;150;150;150m"
RED = "\033[31m"
GRN = "\033[32m"
BLU = "\033[34m"
YLW = "\033[33m"
# # reset
RST = "\033[0m"

CODES = {
        'BLD': BLD,
        'ITL': ITL,
        'GRY': GRY,
        'RED': RED,
        'GRN': GRN,
        'BLU': BLU,
        'YLW': YLW,
        'RST': RST,
        }

STYLES = {
        "red": RED,
        None: "",
        }

PATTERN3 = re.compile(r'(?<!%)%(BLD|ITL|GRY|RED|GRN|BLU|YLW|RST)')

USAGE_EXAMPLES = [
        "%BLD%REDWarning!%RST",
        ("Hello, world! %YLWColours%RST and %BLDformatting%RST "
         "in the %ITL%BLD%GRNterminal%RST!"),
]


def translate(text: str) -> str:
        result = PATTERN3.sub(replace_code3, text)
        return _clear(result)


def cprintd(*args, opening=None, loc="", end="\n"):
    opening = f" {YLW + BLD}DBG:{RST} " if opening is None else \
            f" {YLW + BLD}{opening}:{RST} "
    loc = f"{GRY}{ITL} [{loc}]{RST}" if loc and end == "\n" else ""
    print(f"{opening}" + str(*args) +  loc)


def _clear(text: str) -> str:
    """ Escapes % signs """
    return re.sub("%%", "%", text)


def red(text: str) -> str:
    return f"\033[31m{text}\033[0m"


def green(text: str) -> str:
    return f"\033[32m{text}\033[0m"


def blue(text: str) -> str:
    return f"\033[34m{text}\033[0m"


def yellow(text: str) -> str:
    return f"\033[33m{text}\033[0m"


def bold(text: str) -> str:
    return f"\033[1m{text}\033[0m"


def italic(text: str) -> str:
    return f"\033[3m{text}\033[0m"


def replace_code(match: re.Match) -> str:
    return CODES[match.group()[1:]]


def replace_code3(match: re.Match) -> str:
    code = match.group(1)
    return CODES.get(code, match.group(0))


def hello() -> None:
    print(f"{yellow('Hello')} {green('from')} "
          f"{bold(italic(red('mykhcolors!')))}")
    print()
    print("Try typing")
    for example in USAGE_EXAMPLES:
        print(f"> {APPNAME} {example} → ")
        print(translate(example))


def version() -> None:
    print(f"{APPNAME} v. {__version__}")


def main() -> int:
    epilog = f"example: {APPNAME} '%BLD%REDWarning!%RST"
    parser = argparse.ArgumentParser(epilog=epilog)
    parser.add_argument("-v", "--version", action="store_true",
                        help="application version")
    parser.add_argument("text", nargs="*", help="text to format and print")
    args = parser.parse_args()
    if args.version:
        version()
        return 0
    if args.text:
        text = " ".join(args.text)
        result = translate(text)
        print(result)
        return 0
    else:
        hello()

    return 0
