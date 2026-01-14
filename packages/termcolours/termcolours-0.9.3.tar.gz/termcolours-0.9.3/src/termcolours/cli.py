import argparse
from collections import deque
from sys import argv, stdout
from datetime import datetime
from functools import partial
from pathlib import Path
from sys import exit as sysexit
from typing import List, Dict

import pyperclip

from .lib.m_utils.auxiliary import choose_safe_name, foritemin
from .lib.m_utils.printing import (AORG, ARED, ARST, num_to_bg_ansi,
                                   term_del_line)
from .lib.palette import list_palettes
from .lib.softdev.user_input import get_input
from .lib.softdev.debug import RangeError, cprintd

from . import APPNAME, ROOTPATH
from .__about__ import __version__ as VERSION

FTITLE = __file__.split("/", maxsplit=-1)[-1].split(".", maxsplit=-1)[0]
YLW = "\033[33m"
BLD = "\033[1m"
RST = "\033[0m"

BUFF_MAX = 80
# BUFF_MAX = 3
STATE = {
        'buffer': deque(maxlen=BUFF_MAX), 'buffer_capacity': BUFF_MAX,
        'color': "", 'ansi_code': "", 'rgb': tuple(), 'hexa': "",
        'new': False, 'lines_to_del': 1, 'after_help': False,
        'palette': (False, ""),
        'del_lines_called': [],
        'end': True, 'log': [], 'cprintd': cprintd,
        'parser': None
        }
QUITCONT = {
        "quit": "__QUIT__",
        "continue": "__CONTINUE__",
        "shutdown": "__SHUTDOWN__"
        }
HELP_LINES = 11  # 9
COPYCOMMAND = ["fg", "bg"]
if "-d" in argv or "--dev" in argv:
    cprintd = partial(STATE['cprintd'], dbg=True)
    term_del_line = lambda *args, **kwargs: None
else:
    cprintd = partial(STATE['cprintd'], dbg=False)
# !TST:
# term_del_line = lambda *args, **kwargs: None

cprint = print


def _dec_to_fmt(value: int, fmt: str) -> str:
    """ Converts decimal value to 'format' representation """

    if fmt == "hexa":
        return f"{value:02x}"
    elif fmt == "prct":
        return f"{float(value/255):.2f}"
    elif fmt == "decm":
        return str(value)
    else:
        raise ValueError(f"Unknown format: {fmt}")


def _emit(line: str, rgb: tuple) -> None:
    """ Prints line and appends it to buffer """

    loc = f"{APPNAME}::{FTITLE}::_emit"  # !DBG
    print(line)
    cprintd(f"→→→ {line = !r}, {rgb = },  {len(STATE['buffer']) = }…",
            location=loc)
    STATE['buffer'].append((line, rgb))
    cprintd(f"…{len(STATE['buffer']) = }", location=loc)


def decm(value: str) -> int:
    result = int(value, 10)
    return range_check(result)


def hexa(value: str) -> int:
    result = int(value, 16)
    return range_check(result)


def prct(value: str) -> int:
    loc = f"{APPNAME}::{FTITLE}.prct"  # !DBG
    result = int(float(value) * 255)
    cprintd(f"got {value!r} → {result!r}", location=loc)
    return range_check(result)


def range_check(value: int | float) -> int:
    if not 0 <= value <= 255:
        err = f"Value {value!r} is out of range <0-255>"
        raise RangeError(err)
    return int(value)


def color_dec_to_hex(color: str) -> str:
    """ Convertig decimal triplet (string) to hex triplet (string) """

    r, g, b = map(int, color.split(";"))
    return f"#{r:02x}{g:02x}{b:02x}"


def color_hex_to_dec(color: str) -> tuple:
    return tuple(int(color.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))


def del_lines(source: str = "?") -> None:
    if STATE['after_help']:
        term_del_line(HELP_LINES)
        STATE['after_help'] = False
        STATE['del_lines_called'].append((source, HELP_LINES))
        return
    term_del_line(STATE['lines_to_del'])
    STATE['lines_to_del'] = 1
    STATE['del_lines_called'].append((source, 1))


METHOD = {'current': "decm"}
CONVERSIONS = {"decm": decm,
               "hexa": hexa,
               "prct": prct}


def change_method(shortcut: str) -> None:
    METHOD['current'] = shortcut
    del_lines("change_method")


def print_buffer() -> None:
    loc = f"{APPNAME}::{FTITLE}.print_buffer"  # !DBG
    cprintd(f"{STATE['buffer'] = }", location=loc)
    try:
        for line in STATE['buffer']:
            print(line[0])
    except TypeError as e:
        err = f"ERROR: {e.__class__.__name__} / {e}"
        cprintd(err)


def buffer_pop(left: bool = False) -> None:
    """ Drops nr of lines from the buffer

        note: perspective parameter nr -- for removing nr of lines
    """

    if not STATE['buffer']:
        return
    dropped = STATE['buffer'].pop() if not left else STATE['buffer'].popleft()
    comment = " (dropped)" if not left else " (taken)"
    del_lines("buffer_pop")
    print(f"{dropped[0]}{comment}")


def dump(fmt="prct") -> None:
    """ Saving buffer to a file """

    loc = f"{APPNAME}::{FTITLE}.dump"  # !DBG
    cprintd(f"{STATE['buffer'] = }", location=loc)
    print("Dumping buffer to a file:")
    fmt = get_input("    Enter format ", default=fmt,
                    choices=list(CONVERSIONS.keys()))
    cprintd(f"chosen format: {fmt!r}", location=loc)
    filename_ = get_input("    Enter filename ")
    filename = filename_.split("/")[-1]
    parent = "/".join(filename_.split("/")[:-1])
    cprintd(f"→ {parent = }, {filename = }", location=loc)
    filename += ".ssv" if not filename.endswith(".ssv") else ""
    filepath = ROOTPATH / parent / choose_safe_name(ROOTPATH / parent /
                                                    filename)
    cprintd(f"chosen filename: {filename!r}, {filepath = }", location=loc)
    cprintd(f"{filepath = }, {filepath.parent.exists() = }", location=loc)
    cprintd(f"{';'.join(_dec_to_fmt(x, fmt) for x in STATE['buffer'][0][1]) = }",
            location=loc)
    with open(filepath, "w") as fout:
        fout.write(f"# {filename}\n")
        for line in STATE['buffer']:
            the_color = f"{';'.join(_dec_to_fmt(x, fmt) for x in line[1])}"
            fout.write(f"{the_color};{fmt}\n")
        print(f"current buffor saved as a palette to {filepath.name}")
    # with open("dump.txt", "w") as f:
    #     for line in STATE['buffer']:
    #         f.write(f"{line[0]}\n")
    #         #

def quit() -> str | None:
    loc = f"{APPNAME}::{FTITLE}.quit"  # !DBG
    del_lines(source="quit") if not STATE['parser'].parse_args().file else None
    # del_lines(source="quit")
    # cprintd(f"returning {QUITCONT['quit']}", location=loc)
    print("quitting...")
    # cprintd(f"{STATE['log'] = }, `return('__QUIT__')`",
    #         location=f"{APPNAME}::{FTITLE}.quit")
    # if command == QUITCONT["quit"]:
        # sysexit(0)
    return QUITCONT["quit"]


COMMANDS = {
        'decm':    lambda: change_method('decm'),
        'hexa':    lambda: change_method('hexa'),
        'prct':    lambda: change_method('prct'),
        'buffer':  lambda: print_buffer(),
        'clear':   lambda: clear_buffer(),
        'dump':    lambda: dump(),
        'drop':    lambda: buffer_pop(),
        'help':    lambda: usage(quit=False),
        'palette': lambda: palette(),
        'take':    lambda: buffer_pop(left=True),
        'quit':    lambda: quit(),
        'q':       lambda: quit(),
        }

OUTPUT = {
        'mode': "visual",
        }

NAMES = {
        'decm': {'method': "decimal",
              'desc': "sets conversion from decimal format"},
        'hexa': {'method': "hexadecimal",
              'desc': "sets conversion from hexadecimal format"},
        'prct': {'method': "perentage",
              'desc': "sets conversion from percentage format"},
        'palette': {'method': "", 'desc': "generates a named palette"},
        'buffer':  {'method': "", 'desc': "prints the color buffer"},
        'clear':   {'method': "", 'desc': "clears the color buffer"},
        'drop':    {'method': "", 'desc': "drops the last line from the buffer"},
        'take':    {'method': "", 'desc': "takes the first line from the buffer"},
        'dump':    {'method': "", 'desc': "dumps the buffer to an .ssv file"},
        'help':    {'method': "", 'desc': "prints this message"},
        'quit':    {'method': "", 'desc': "exits the application"}
        }
RANGES = {
        'decm': "0-255",
        'hexa': "00-ff",
        'prct': "0.00-1.00",
        }


def ask_for_color() -> str:

    loc = f"{APPNAME}::{FTITLE}.ask_for_color"  # !DBG
    method = METHOD['current']
    ans = get_input(f"Enter a colour code (R;G;B, {NAMES[method]['method']};"
                    f" {RANGES[method]}), command or help")
    color = ""
    try:
        if ans.lower() in COMMANDS:
            return ans
        if ans.lower() in COPYCOMMAND:
            return ans

        r, g, b = map(CONVERSIONS[method], ans.split(";"))
        color = f"#{r:02x}{g:02x}{b:02x}"

    except ValueError as e:
        if ans == "":
            print(f"{AORG}No input given, quitting...{ARST}")
            return QUITCONT['quit']

        cprint(f"{ARED}ERROR: unrecognized value/command {ans!r} - "
               f"use 'help' for help{ARST}")
        return "__CONTINUE__"
    except RangeError as e:
        cprint("ERROR: " + e.args[0])
        STATE['color'] = ""
        STATE['ansi_code'] = ""
    except AttributeError:
        # sysexit(1)
        return QUITCONT['shutdown']
    except KeyboardInterrupt:
        cprint("...aborting... (KeyboardInterrupt)")
        # cprintd(f"{STATE['del_lines_called'] = }",
        #         location=FTITLE + ".ask_for_color (KeyboardInterrupt)")
        # sysexit(1)
        return QUITCONT['shutdown']

    return color


def palette() -> None:
    """ Generate a named (predefined) palette """

    loc = f"{APPNAME}::{FTITLE}.palette"  # !DBG
    palettes = list_palettes()
    cnt = 0
    lines = []
    line = ""
    for i, palette in enumerate(sorted(palettes)):
        if len(line + f"{palette!r} | ") < 79:
            line += f"{palette!r} | "
            continue
        else:
            cnt += 1
            line = line[:-3]
            lines.append(line)
            line = f"{palette!r} | "
            continue
    cnt += 1
    line = line[:-3]
    lines.append(line)
    print(*lines, sep="\n")
    palette_name = get_input("Enter a palette name", choices=palettes,
                             show_choices=False)
    log(f"setting STATE['lines_to_del'] to {i + 2}", "palette")
    STATE['lines_to_del'] = cnt + 2
    log(f"about to delete {STATE['lines_to_del']} lines", "palette")
    del_lines("palette")
    print(f"palette: {palette_name}")
    batch_conversion(palettes[palette_name], once=False)
    STATE['palette'] = (True, palette_name)


def print_colored_line(nr_chars: int = 10,
                       ansi: str = "", hexa: str = "",
                       ending: str = "") -> None | str:
    """ Print a line with specified color and ansi code """

    loc = f"{APPNAME}::{FTITLE}.print_colored_line"  # !DBG
    ansi = ansi or STATE['ansi_code']
    hexa = STATE['color'] or hexa
    rgb = color_hex_to_dec(hexa) if hexa else STATE['rgb']
    output = ""
    if OUTPUT['mode'] == "visual":
        output = f"{ansi}{' ' * nr_chars}{ARST} ← "
    else:
        ending = ""
    # !INF: description next to the line:
    STATE['color'] = ""
    STATE['hexa'] = STATE['color']
    output += f"{hexa} = {str(rgb):<15} = {ansi!r:<25} {ending}"
    _emit(output, rgb)


def num_to_ansi() -> str | None:
    """ Transforms a color (R;G;B) into ansi code """

    loc = f"{APPNAME}::{FTITLE}.num_to_ansi"  # !DBG
    cprintd(f"at the very beginning: {STATE['color'] = }", location=loc)
    if STATE['ansi_code'] != "" and STATE['new']:
        result = print_colored_line(20)
        if result == QUITCONT['quit']:
            return QUITCONT['quit']
        STATE['new'] = False

    if STATE['color'] == "":
        color = ask_for_color().strip()
    else:
        color = STATE['color']

    cprintd(f"got {color = }: {STATE['color'] = }", location=loc)
    if color in QUITCONT.values():
        return color

    # !INF: if the input was a command:
    if color.lower() in COMMANDS:
        result = COMMANDS[color.lower()]()
        return result

    # !INF: if the input was a copy command:
    if color.lower() in COPYCOMMAND:
        copy_color(color)
        return

    del_lines(source="(trying_num_to_ansi)")
    STATE['color'] = color

    rgb_ = tuple()
    try:
        ansi_code, *rgb_ = num_to_bg_ansi(STATE['color'], with_rgb_dec=True)

        STATE['color'] = color
        STATE['ansi_code'] = ansi_code
        STATE['new'] = True
    except Exception as e:
        if STATE['color'] == "":  # !INF: if the input was empty → quit
            return "__QUIT__"
        cprint(f"{ARED}error → {e}{ARST}")
        STATE['lines_to_del'] = 3

        if color in COPYCOMMAND:
            STATE['new'] = True
    STATE['rgb'] = rgb_[0] if rgb_ else tuple()


def parse_color_value(value: str, fmt: str):
    """ Converts color value, depending on format. """

    if fmt in CONVERSIONS:
        return CONVERSIONS[fmt](value)
    else:
        raise ValueError(f"Unknown format: {fmt}")


def read_colors_file(filename: str) -> List[Dict]:

    loc = f"{APPNAME}::{FTITLE}.read_colors_file"  # !DBG
    colors = []
    filepath = Path(filename)
    filepath = ROOTPATH / filename if not filepath.exists() else filepath
    cprintd(f"{filepath = }, {filepath.exists() = }", location=loc)
    cnt = 0  # !INF: for netto lines nr
    with open(filepath, "r") as fin:
        cprintd(f"reading colors file {filename}", location=loc)
        for line_no, line in enumerate(fin, start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(";")
            if len(parts) < 4:
                print(f"Skipping invalid line {line_no}: {line}")
                continue
            r_s, g_s, b_s, fmt = parts[:4]
            cprintd(f"{r_s = }, {g_s = }, {b_s = }, {fmt = }", location=loc)
            try:
                r = parse_color_value(r_s, fmt)
                g = parse_color_value(g_s, fmt)
                b = parse_color_value(b_s, fmt)
                x = f"#{r:02x}{g:02x}{b:02x}"
                cnt += 1
            except (ValueError, RangeError):
                continue
            colors.append({"r": r, "g": g, "b": b, "x": x, "format": fmt})
            cprintd(f"{colors = }", location=loc)
    return colors


def batch_conversion(filename: str | Path | None = None,
                     once: bool = False) -> str | None:
    """ Generating colors/ANSI codes from a .ssv file """

    loc = f"{APPNAME}::{FTITLE}.batch_conversion"  # !DBG
    cprintd(f"{STATE.get('file') = }", location=loc)
    filename = filename if filename is not None else\
            STATE['parser'].parse_args().file
    cprintd(f"{filename = }", location=loc)
    colors = read_colors_file(filename)
    colors_nr = len(colors)
    for i, color in enumerate(colors):
        ending = "\u2502" if colors_nr > 1 else ""
        if i == 0 and colors_nr > 1:
            ending = "↓"
        elif i == colors_nr - 1 and colors_nr > 1:
            ending = f"↑ ({colors_nr})"
        ansi = num_to_bg_ansi(color["x"])
        print_colored_line(20, ansi, hexa=color["x"], ending=ending)

    if once:
        return QUITCONT["quit"]
    return QUITCONT["continue"]


def clear_buffer() -> None:
    """ Clearing the buffer """

    STATE['buffer'] = deque(maxlen=STATE['buffer_capacity'])


def copy_color(fbg: str) -> None:
    """ Copying the bg/fg colour to clipboard

        Args:
            fbg (str): foreground or background, 'fg' or 'bg'
    """

    loc = f"{APPNAME}::{FTITLE}.copy_color"  # !DBG
    if STATE['ansi_code'] == "":
        cprint(f"{ARED}no color to copy{ARST}")
        sysexit(0)

    fgbg = "(background)"
    if fbg.lower() == "fg":
        STATE['ansi_code'] = STATE['ansi_code'].replace("[48", "[38", 1)
        fgbg = "(foreground)"
    try:
        pyperclip.copy(STATE['ansi_code'])
        cprint(f"copying {STATE['rgb']} = {STATE['hexa']}: "
               f"{STATE['ansi_code']!r} {fgbg}")
    except pyperclip.PyperclipException as e:
        err = f"error copying to clipboard: {e}"
        cprint(f"{ARED}{err}{ARST}")
        cprint(f"what should be copied: {STATE['rgb']} = {STATE['hexa']}: "
               f"{STATE['ansi_code']!r} {fgbg}")


def usage(quit: bool = False) -> None:
    print("Input color as 3 hex numbers, separated by semicolon, "
          "when prompted,")
    print("e.g. 'ff;00;00' for red.")
    print("Commands in the interactive mode:")
    # print(f"    - {'/'.join(COPYCOMMAND)} to copy the current "
    #       "color to the clipboard \n      (ANSI foreground/background, "
    #       "respectively).")
    key_len = max(len(key) for key in NAMES) + 1 * 7 + 3  # + 1 *… ← T&E
    cprintd(f"{key_len = }, {type(key_len) = }",
            location=f"{APPNAME}::{FTITLE}.usage")
    for cmd in COPYCOMMAND:
        command = f"{BLD}{cmd}{RST}:"
        print(f"    - {command:<{key_len}} to copy the current color "
              "to the clipboard")
    for key, value in NAMES.items():
        command = f"{BLD}{key}{RST}:"
        print(f"    - {command:<{key_len}} {value['desc']}")
    if quit and STATE['end']:
        sysexit(0)
    STATE['after_help'] = True


def log(message: str, source: str = "main") -> None:
    t = datetime.now().strftime("%H:%M:%S")
    STATE['log'].append(f"{message} -- {source}@{t}")



def main() -> int | dict:
    loc = f"{APPNAME}::cli.main"  # !DBG

    cprintd("starting…", location=loc)
    parser = argparse.ArgumentParser(
        prog=APPNAME,
        description="Terminal color picker",
        epilog=f"version: {VERSION}",
        add_help=False,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
                        "-f", "--file",
                        metavar="FILE",
                        type=str,
                        help="file to process in batch mode"
                        )
    parser.add_argument(
        "color",
        nargs="?",
        default=None,
        help="color to convert to ANSI code (e.g. 0.1;.8;.15;decm -- optional)"
        )
    parser.add_argument("-d", "--dev", action="store_true",
                        help="development mode")
    parser.add_argument("-m", "--mode",
                        choices=["visual", "raw"],
                        default="visual",
                        help="output mode (default: visual)")
    parser.add_argument("-v", "--version", action="store_true",
                        help="prints application version")
    parser.add_argument("-h", "--help", action="store_true",
                        help="prints help message")
    STATE['parser'] = parser

    args = parser.parse_args()
    STATE['dev'] = args.dev

    mode_txt = f" -- batch mode: {args.file!r}" if args.file\
            else " -- interactive mode"
    OUTPUT['mode'] = args.mode

    if args.help:
        parser.print_help()
        return 0
    if args.version:
        print(f"{APPNAME} v. {VERSION}")
        sysexit(0)
    print(f"{APPNAME} v. {VERSION}{mode_txt}")
    if args.file:
        STATE['file'] = args.file
        result = batch_conversion()
        if result == QUITCONT['quit']:
            return 0

    i = 0
    while True:
        if args.color is not None:
            r, g, b, fmt = args.color.split(";")
            if fmt == "decm":
                color = color_dec_to_hex(f"{r};{g};{b}")
                STATE['color'] = color
                args.color = None
        result = num_to_ansi()
        if result == QUITCONT['quit']:
            break
        elif result == QUITCONT['shutdown']:
            return 1
        i += 1

    return 0
