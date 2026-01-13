import curses
import time
from curses import window
from dataclasses import dataclass
from typing import Self, List, Dict

from totp import utils

from totp.text import FormattedText, get_slider, calc_slider, init_colors
from totp.crypt import EntrySite, InvalidSecretKey
from totp.config import (
    BLANK_DEF,
    NICK_DEF,
    SITE_DEF,
    ENTRY_SCHEMA,
    STATUSLINE_SCHEMA,
    DEFAULT_FG,
)

logger = utils.get_logger(__name__)

# FIX: AuthWindow shouldnt modify stdsrc directly: textpad? newpad? to prevent overflow
# FIX: raise exception if width not provided instead of ignore
# WARN: properly assert config.py typings
# TODO: box entries


class SchemaTypeError(Exception):
    def __init__(self, component: str) -> None:
        self.component = component
        self.message = f"Schema component {self.component} has incorrect typing or is missing an element."
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"Schema component {self.component} has incorrect typing or is missing an element."


@dataclass
class Schema:
    format = ENTRY_SCHEMA
    statusline = STATUSLINE_SCHEMA

    @classmethod
    def get_line_len(
        cls, components: (List[FormattedText], List[FormattedText])
    ) -> int:
        return sum(
            sum(len(comp.get_text()) for comp in components[x])
            for x in range(len(components))
        )

    def format_entry_line(
        self, line: List[Dict], values: Dict
    ) -> (List[FormattedText], List[FormattedText]):
        """ """

        left_align: List[FormattedText] = []
        right_align: List[FormattedText] = []

        for component in line:
            try:
                val = component["type"]
            except KeyError:
                logger.warn("Schema component ignored, invalid type found")
                continue
            if val in values.keys() and type(val) is str:
                text = values[val]

                match val:
                    case "slider":
                        if (
                            "width" in component.keys()
                            and type(component["width"]) is int
                        ):
                            width = component["width"]
                        else:
                            raise SchemaTypeError(component="slider")

                        text = get_slider(width=width)

                    case "time":
                        rem = 30 - time.time() % 30
                        if (
                            "precision" in component.keys()
                            and type(component["precision"]) is int
                        ):
                            prec = component["precision"]
                            text = repr(round(rem, prec))
                        else:
                            raise SchemaTypeError(component="time")

                    case "token":
                        text = values["token"]

                    case _:
                        if "width" in component.keys():
                            try:
                                width = int(component["width"])
                                dif = width - len(text)
                                text = text[: min(width, len(text))]
                                if dif > 0:
                                    text = text + (BLANK_DEF * dif)
                            except TypeError:
                                raise SchemaTypeError(component=val)
                        else:
                            raise SchemaTypeError(component=val)

                if "space_before" in component.keys():
                    try:
                        space_before = int(component["space_before"])
                        text = (BLANK_DEF * space_before) + text
                    except TypeError:
                        logger.warn("Schema component ignored, no valid type found.")
                if "space_after" in component.keys():
                    try:
                        space_after = int(component["space_after"])
                        text = text + (BLANK_DEF * space_after)
                    except TypeError:
                        logger.warn("Schema component ignored, no valid type found.")

                color = DEFAULT_FG
                if "color" in component.keys():
                    try:
                        color = str(component["color"])
                    except TypeError:
                        pass
                if "alignment" in component.keys():
                    try:
                        align = str(component["alignment"])
                        formatted = FormattedText(text=text, color=color)
                        if align == "right":
                            right_align.append(formatted)
                        elif align == "left":
                            left_align.append(formatted)
                    except TypeError:
                        left_align.append(FormattedText(text=text, color=color))
                else:
                    logger.warn("Schema component ignored, no valid alignment found.")
            else:
                logger.warn(
                    f'Schema component ignored, unknown element type "{str(val)}"'
                )

        return (left_align, right_align)

    def draw_line(
        self,
        src: window,
        start_y: int,
        components: (List[FormattedText], List[FormattedText]),
    ) -> None:
        _, maxx = src.getmaxyx()
        pos_x = 0
        if Schema.get_line_len(components) <= maxx:
            for comp in components[0]:
                comp_off = comp.len()
                src.addstr(
                    start_y, pos_x, comp.get_text(), curses.color_pair(comp.get_color())
                )
                pos_x += comp_off
            filler = maxx - pos_x - sum(comp.len() for comp in components[1])
            src.addstr(start_y, pos_x, BLANK_DEF * filler)
            pos_x += filler
            for comp in components[1]:
                comp_off = comp.len()
                src.addstr(
                    start_y, pos_x, comp.get_text(), curses.color_pair(comp.get_color())
                )
                pos_x += comp_off
        else:
            for comp in components[0]:
                comp_off = comp.len()
                src.addstr(
                    start_y, pos_x, comp.get_text(), curses.color_pair(comp.get_color())
                )
                pos_x += comp_off
            for comp in components[1]:
                comp_off = comp.len()
                src.addstr(
                    start_y, pos_x, comp.get_text(), curses.color_pair(comp.get_color())
                )
                pos_x += comp_off

    def draw_entry(self, src: window, start_y: int, entry: EntrySite) -> None:
        """ """

        try:
            totp_token = entry.get_totp_token()
        except InvalidSecretKey as exc:
            totp_token = (
                NICK_DEF[0] if type(NICK_DEF) is str and len(NICK_DEF) > 0 else "\u0023"
            ) * 6
            logger.error(exc)

        values = {
            "nick": entry.nick,
            "site": entry.site,
            "time": None,
            "token": totp_token,
            "slider": None,
            "blank": BLANK_DEF,
        }

        for off, (_, line) in enumerate(self.format.items()):
            ll = self.format_entry_line(line=line, values=values)
            self.draw_line(src=src, start_y=start_y + off, components=ll)

    def format_statusline(
        self, line: List[Dict], values: Dict
    ) -> (List[FormattedText], List[FormattedText]):
        """ """

        left_align: List[FormattedText] = []
        right_align: List[FormattedText] = []

        for component in line:
            try:
                val = component["type"]
            except KeyError:
                logger.warn("Schema component ignored, invalid type found")
                continue
            if val in values.keys() and type(val) is str:
                text = values[val]

                match val:
                    case "slider":
                        if (
                            "width" in component.keys()
                            and type(component["width"]) is int
                        ):
                            width = component["width"]
                        else:
                            raise SchemaTypeError(component="slider")
                        text = get_slider(width=width)
                    case "time":
                        localtime = time.localtime()
                        if (
                            "format" in component.keys()
                            and type(component["format"]) is str
                        ):
                            text = time.strftime(component["format"], localtime)
                        else:
                            raise SchemaTypeError(component="time")
                    case "token_time":
                        rem = 30 - time.time() % 30
                        if (
                            "precision" in component.keys()
                            and type(component["precision"]) is int
                        ):
                            prec = component["precision"]
                            text = repr(round(rem, prec))
                        else:
                            raise SchemaTypeError(component="token_time")

                if "space_before" in component.keys():
                    try:
                        space_before = int(component["space_before"])
                        text = (BLANK_DEF * space_before) + text
                    except TypeError:
                        logger.warn("Schema component ignored, no valid type found.")
                if "space_after" in component.keys():
                    try:
                        space_after = int(component["space_after"])
                        text = text + (BLANK_DEF * space_after)
                    except TypeError:
                        logger.warn("Schema component ignored, no valid type found.")

                color = DEFAULT_FG
                if "color" in component.keys():
                    try:
                        color = str(component["color"])
                    except TypeError:
                        pass
                if "alignment" in component.keys():
                    try:
                        align = str(component["alignment"])
                        formatted = FormattedText(text=text, color=color)
                        if align == "right":
                            right_align.append(formatted)
                        elif align == "left":
                            left_align.append(formatted)
                    except TypeError:
                        left_align.append(FormattedText(text=text, color=color))
                else:
                    logger.warn("Schema component ignored, no valid alignment found.")
            else:
                logger.warn(
                    f'Schema component ignored, unknown element type "{str(val)}"'
                )

        return (left_align, right_align)

    def draw_statusline(self, src: window) -> None:
        """ """

        _y, _x = src.getmaxyx()
        len_status = len(self.statusline)
        start_y = max(0, _y - len_status)

        values = {"time": None, "token_time": None, "slider": None}

        for off, (_, line) in enumerate(self.statusline.items()):
            ll = self.format_statusline(line=line, values=values)
            self.draw_line(src=src, start_y=start_y + off, components=ll)

    def entry_offset(self) -> int:
        return len(self.format.items())


class AuthWindow:
    def __init__(self, stdsrc: window) -> None:
        self.orig = stdsrc
        self.sites: List[EntrySite] = []
        self.schema = Schema()
        self.pad = None
        init_colors()

    def update_pad(self) -> None:
        _y, _x = self.orig.getmaxyx()
        h = len(self.sites) * self.schema.entry_offset()
        try:
            self.pad = curses.newpad(h, _x)
        except curses.error:
            raise RuntimeError("Failed to create newpad")

    def draw(self) -> None:
        try:
            self.update_pad()
            self.pad.erase()
        except RuntimeError:
            logger.error("Empty sites list.")
            raise RuntimeError("Empty sites list")

        for i, site in enumerate(self.sites):
            try:
                y = self.schema.entry_offset() * i
                self.schema.draw_entry(src=self.pad, start_y=y, entry=site)
            except curses.error:
                pass
        try:
            self.schema.draw_statusline(src=self.orig)
        except curses.error:
            pass

        max_y, max_x = self.orig.getmaxyx()
        h = max_y - (1 + len(self.schema.statusline))
        w = max_x - 1
        self.pad.refresh(0, 0, 0, 0, h, w)
        self.orig.refresh()

    def add_site(self, site: EntrySite) -> None:
        self.sites.append(site)
