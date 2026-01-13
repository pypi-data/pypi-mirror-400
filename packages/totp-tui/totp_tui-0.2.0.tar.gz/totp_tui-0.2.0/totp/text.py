import curses
import time
from dataclasses import dataclass
from typing import Self, Tuple

from totp.config import DEFAULT_FG, BLANK_DEF, NICK_DEF, SLIDER_DEF, FANCY_SLIDER
from totp.crypt import EntrySite


def_colors = {
    "white": 1,
    "red": 2,
    "green": 3,
    "yellow": 4,
    "blue": 5,
    "magenta": 6,
    "cyan": 7,
    "black": 8,
}


def init_colors():
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(7, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_BLACK)


def color(col: str) -> int:
    col = col.lower()
    try:
        if col in def_colors.keys():
            return def_colors[col]
        if str(DEFAULT_FG) in def_colors.keys():
            return def_colors[DEFAULT_FG]
    except TypeError:
        return 1
    else:
        return 1


def _slider_perc(perc: float) -> str:
    perc = int(perc % 1 * 7)
    ret = "\u2588"
    match perc:
        case 0:
            ret = "\u2589"
        case 1:
            ret = "\u258a"
        case 2:
            ret = "\u258b"
        case 3:
            ret = "\u258c"
        case 4:
            ret = "\u258d"
        case 5:
            ret = "\u258e"
        case 6:
            ret = "\u258f"
    return ret


def get_slider(width: int) -> str:
    if type(FANCY_SLIDER) is bool and FANCY_SLIDER:
        return calc_slider(width)
    else:
        return simple_slider(width)


def simple_slider(width: int) -> str:
    text_def_chr = (
        NICK_DEF[0] if type(NICK_DEF) is str and len(NICK_DEF) > 0 else "\u0023"
    )
    blank_def_chr = (
        BLANK_DEF[0] if type(BLANK_DEF) is str and len(BLANK_DEF) > 0 else "\u0020"
    )

    if type(SLIDER_DEF) is list and len(SLIDER_DEF) == 3:
        slider_chr, last_chr, filler_chr = SLIDER_DEF
    else:
        slider_chr, last_chr, filler_chr = [text_def_chr, text_def_chr, blank_def_chr]

    inside_brac = max(width - 2, 0)
    perc_width = (time.time() % 30) / 30
    rem = perc_width * inside_brac % 1

    filler_width = int(perc_width * inside_brac)
    slider_width = max((inside_brac - filler_width) - 1, 0)
    slider = slider_chr * slider_width
    filler = filler_chr * filler_width
    return f"[{slider}{last_chr}{filler}]"


def calc_slider(width: int) -> str:
    time_diff = time.time() % 30
    chr = "\u2588"
    inside_brac = max(width - 2, 0)
    perc_width = time_diff / 30
    rem = perc_width * inside_brac % 1

    filler_width = int(perc_width * inside_brac)
    slider_width = max((inside_brac - filler_width) - 1, 0)
    slider = chr * slider_width
    filler = BLANK_DEF * filler_width
    return f"[{slider}{_slider_perc(perc=rem)}{filler}]"


@dataclass
class FormattedText:
    text: str
    color: str = DEFAULT_FG

    @classmethod
    def from_tuple(cls, formatted: Tuple[str, str]) -> Self:
        text, color = formatted
        return cls(text=text, color=color)

    def get_text(self) -> str:
        return str(self.text)

    def get_color(self) -> int:
        return color(self.color)

    def len(self) -> int:
        return len(self.text)

    def len_strip(self) -> int:
        return len(self.text.strip())
