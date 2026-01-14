from sys import stdout

TAB_NR = 4
TAB = " "*TAB_NR  # noqa: E226

# - formatting:
ARST = "\033[0m"  # wyłącza wszystkie efekty
ABLD = "\033[1m"  # bold
AITC = "\033[3m"  # italic
AITL = AITC  # italic
ABLIT = "\033[1;3m"  # italic + bold
ABC = "\033[1;3m"  # italic + bold
AUND = "\033[4m"  # underline
ABLK = "\033[5m"  # blink
ARVS = "\033[7m"  # reversed

# - colors:
ADWT = "\x1b[38;2;216;222;233m"  # ← nord
ARED = "\x1b[38;2;191;97;106m"  # ← nord
ABLU = "\033[34m"
ALBL = "\x1b[38;2;129;161;193m"
# AORG = "\033[38;5;221m"
AORG = "\x1b[38;2;208;135;112m"  # ← nord
AORG1 = "\033[38;5;214m"
AYEL = "\x1b[38;2;235;203;139m"  # ← nord
# AGRN = "\033[32m"
AGRN = "\x1b[38;2;163;190;140m"  # ← nord
ASAL = "\x1b[38;2;191;97;106m"  # ← nord
AWTH = "\033[37m"
# AGRY = "\033[251m"
# AGRY = "\033[38;2;150;150;150m"\x1b[48;2;76;86;106m
AGRY = "\x1b[38;2;76;86;106m"  # ← nord
# AGRYBG = "\033[48;2;100;100;100m"
AGRYBG = "\x1b[48;2;76;86;106m"  # ← nord

# - cursor moves:
AERSLIN = "\033[1A\033[2K"  # moves up, erease line


def num_to_fg_ansi(color: str | int,
                   with_rgb_dec=False,
                   fgbg: int = 38) -> str | tuple[str, tuple[int, int, int]]:
    """ Hex to terminal foreground ANSI code """

    if not isinstance(color, (str, int)):
        err = "color must be str or int"
        raise TypeError(err)
    color = hex(color) if isinstance(color, int) else color
    color = color.lstrip("#")
    color = color.replace("0x", "")
    r = int(color[:2], 16)
    g = int(color[2:4], 16)
    b = int(color[4:], 16)
    # cprintd(f"{color = } → {r = }, {g = }, {b = }",
    #         location=FTITLE + ".hex_to_fg_ansi")
    if not with_rgb_dec:
        return f"\x1b[{fgbg};2;{r};{g};{b}m"
    return (f"\x1b[{fgbg};2;{r};{g};{b}m", (r, g, b))


def num_to_bg_ansi(color: str | int,
                   with_rgb_dec=False) -> str | tuple[str,
                                                      tuple[int, int, int]]:
    """ Hex to terminal background ANSI code """

    return num_to_fg_ansi(color, with_rgb_dec=with_rgb_dec, fgbg=48)


def term_del_line(nr: int = 0) -> None:
    """ Deletes nr of lines in the terminal """

    for _ in range(nr):
        # print(AERSLIN, end="")
        stdout.write(AERSLIN)
        stdout.flush()
