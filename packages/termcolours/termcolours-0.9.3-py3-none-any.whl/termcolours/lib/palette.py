# ./src/termcolours/lib/palette.py

"""
Module for generatig a named palette
"""

from pathlib import Path

from .softdev.debug import cprintd
from .. import ROOTPATH
from .. import APPNAME

PALETTE_FOLDER = "assets"
FTITLE = __file__.split("/", maxsplit=-1)[-1].split(".", maxsplit=-1)[0]
# APPNAME = "termcolours"


def list_palettes() -> dict:
    palettes_path = ROOTPATH / PALETTE_FOLDER
    result = {}

    for palette_path in palettes_path.glob("*.ssv"):
        if palette_path.is_file():
            # apalette = {'name': "", 'path': palette_path}
            name = None
            with palette_path.open("r", encoding="utf-8") as fin:
                first_line = fin.readline().rstrip("\n")
                if "palette" in first_line:
                    name = first_line.lstrip("# ").split(";")[0].\
                            split(":")[1].strip()
                name = name or palette_path.stem
                result.update({name:  palette_path})

    return {k: result[k] for k in sorted(result.keys())}

