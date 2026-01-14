# from .lib.m_utils.printing import (ABLD, AGRY, AGRYBG, AITL, AORG, ARED,
#                                    ARST, TAB)
from ..m_utils.printing import (ABLD, ADWT, AGRN, AGRY, AGRYBG, AITL, ALBL,
                                AORG, ARED, ARST, ASAL, AYEL, TAB)
# TAB_SPCS = 4
# TAB = "·"*TAB_SPCS


class RangeError(Exception):
    pass


def cprintd(message, opening="DBG:", location="", tabs_nr: int = 0, dbg=True,
            end="\n"):
    """ Print debug message

        Args:
            message (str): message to print
            opening (str, optional): opening. Defaults to "DBG:".
            location (str, optional): location. Defaults to "".
            tabs_nr (int, optional): tabs number. Defaults to 0.

        Returns:
            None
    """

    if not dbg:
        return
    # if CN['console'] is None:
    #     CN['console'] = Console(file=file)

    opening = f"{opening:^6}" if opening else ""
    # bg = "navajo_white3"
    bg = AGRYBG
    # fg = ARED
    fg = AORG
    # fg = "bright_red"
    # fg = "dark_red"
    # dbg_message = Text(f"{TAB*tabs_nr}")
    dbg_message = f"{TAB*tabs_nr}"
    # opening_color = "red" if any(info in opening for info in ("DBG", "ERR"))\
    #     else "blue"
    dbg_message += f"{ABLD + AITL + AGRYBG + AYEL}{opening}{ARST}"
    dbg_message += f" {ADWT}{message}{ARST}"
    if location:
        dbg_message += f" {AITL + AGRY}[{location}]{ARST}"

    print(dbg_message, end=end)
