# ./src/termcolors/lib/m_utils/auxiliary.py

from re import search
from pathlib import Path

FTITLE = __file__.split("/", maxsplit=-1)[-1].split(".", maxsplit=-1)[0]

cprint = print
printrow = print


def choose_safe_name(file_path_name: Path | str) -> Path | str:
    """ Automatically choosing new safe name/Path for the file """

    loc = FTITLE + ".choose_safe_name"
    # cprintd(f"{file_path_name = }", location=loc)
    actual_path = Path(file_path_name)
    # cprintd(f"{actual_path = }", location=loc)
    actual_name = actual_path.name
    # cprintd(f"{actual_name = }", location=loc)
    try:
        stem, suffix = actual_name.rsplit(".", maxsplit=1)
        dot = "."
    except ValueError:
        stem, suffix = actual_name, ""
        dot = ""
    # cprintd(f"{stem = }, {suffix = }", location=loc)

    # file does not exist case:
    if not actual_path.is_file():
        return file_path_name

    # file exists case:
    dbg_cnt = 0
    while actual_path.is_file():
        # if _ends_with_number(stem):
        if search(r'\d+$', stem):
            nr_ = search(r"\d+$", stem)[0]
            # cprintd(f"ending number: {int(nr_) = }, {len(nr_) = }",
            #         location=loc)
            nr = int(nr_)
            nr_final = f"{nr + 1:0{len(nr_)}}"
            # cprintd(f"{nr_final = }", location=loc)
            new_stem = stem[:-len(nr_)] + nr_final
            # cprintd(f"{new_stem = }", location=loc)
            stem = new_stem
        else:
            new_stem = f"{stem}_01"
            # cprintd(f"{new_stem = }", location=loc)
            stem = new_stem
        new_name = f"{new_stem}{dot}{suffix}"
        # cprintd(f"{new_name = }", location=loc)
        actual_path = actual_path.parent / new_name
        dbg_cnt += 1
        if dbg_cnt > 13:
            print("break!", end="")
            print(" [m_system.files.choose_safe_name]")
            break

    # if actual_path.is_file():
    #     new_path = actual_path.parent / new_name
    #     return new_path

    try:
        return file_path_name.parent / new_name
    except AttributeError:
        return new_name

    return 'bla'


def foritemin(items, message="", start=0, end=None, *, oftype=False, cond="",
              func=None, special=False, nrs=True):
    """ Simple iteration.

    Function performing iteration for all elements of `items`.
    items -- list of elements to iterate over (iterable)
    start: int -- iteration from `start`
    end: int -- iteration to `end`
    oftype: bool -- prints the type of each item, if True
    cond: str -- prints only items containing `cond` string
                 (`~def foritemin(` for `not containing`, `⧹` escapes `~`;
                                  `⧹` -- stands for 'backslash')
    func: function  -- function to perform on each element, default: `print`
    special: bool -- if special members are to be printed
    nrs: bool -- if numbers are to be printed
    """

    # from m_utils.khutils import printrow
    printrow = print

    # from time import perf_counter  # timing
    # pT0 = perf_counter()
    # printd(f"{items = }")
    # printd(f"{type(items) = }")
    if cond.startswith('~'):
        condition = lambda cond, item: cond not in item
        print(f"DBG: {condition = }")
        cond = cond[1:]
    elif cond.startswith('\u005c'):  # \u005c = backslash, \
        condition = lambda cond, item: cond in item
        cond = cond[1:]
    else:
        condition = lambda cond, item: cond in item
    if func is None:
        func = print
    # pT1 = perf_counter()
    types = []
    try:
        itemsEnum = enumerate(items[start:end])
    except TypeError:  # this exception hits the case of a module
        # printd("Not done, except...")
        itemsEnum = enumerate(dir(items)[start:end])
        for item in dir(items)[start:end]:
            types.append(type(item))
    # pT2 = perf_counter()
    if message != "":
        cprint(message)
    for i, item in itemsEnum:
        if special:
            specialCase = True
        else:
            specialCase = True if not str(item).startswith("__") else False
        if condition(cond, str(item)) and specialCase:
            if func is print and nrs is True:
                whatType = f"[{type(items.__getattribute__(item))}]"\
                    if oftype else ""
                print(f"{i:>3}) {whatType} ", end="")
            # func(item)  # !TODO: temporary, if printrow workes
            # printrow(item, width=60)
            printrow(item)
