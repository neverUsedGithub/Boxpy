# chalk -> colored
from colored import fg, bg, attr
# For process.stdout.columns
import os
# For loading boxes.json
import json
# For Math.floor
import math
# string-width replacement
from .string_width import string_width
# ansi-align replacement
from .ansi_align import ansi_align
# wrap-ansi replacement
from .wrap_ansi import wrap_ansi
# widest-line replacement
from .widest_line import widest_line

# boxes.json
import pkg_resources

# Typing
from typing import Callable

cli_boxes = json.loads(
    pkg_resources.resource_string(__name__, "boxes.json")
)

NEWLINE = "\n"
PAD = " "
BORDERS_WIDTH = 2


def terminal_columns():
    return os.get_terminal_size().columns


def get_object(detail):
    if type(detail) == int:
        return {
            "top": detail,
            "right": detail * 3,
            "bottom": detail,
            "left": detail * 3
        }

    return {
        **{
            "top": 0,
            "right": 0,
            "bottom": 0,
            "left": 0
        },
        **detail
    }


def get_border_chars(border_style: str | dict[str, str] | None):
    sides = [
        "topLeft",
        "topRight",
        "bottomRight",
        "bottomLeft",
        "left",
        "right",
        "top",
        "bottom"
    ]

    characters = None

    if border_style == None:
        border_style = {}
        for side in sides:
            border_style[side] = ""

    if type(border_style) == str:
        characters = cli_boxes.get(border_style, None)

        if not characters:
            raise Exception(f"Invalid border style: {border_style}")
    else:
        if border_style.get("vertical", None):
            border_style["left"] = border_style["vertical"]
            border_style["right"] = border_style["vertical"]

        if border_style.get("horizontal", None):
            border_style["top"] = border_style["horizontal"]
            border_style["bottom"] = border_style["horizontal"]

        for side in sides:
            if border_style.get(side, None) == None or type(border_style.get(side, None)) != str:
                raise Exception(f"Invalid border style: {side}")

        characters = border_style

    return characters


def make_title(text, horizontal, alignment):
    title = ""

    text_width = string_width(text)

    if alignment == "left":
        title = text + horizontal[text_width:]
    elif alignment == "right":
        title = horizontal[text_width:] + text
    else:
        horizontal = horizontal[text_width:]

        if len(horizontal) % 2 == 1:
            horizontal = horizontal[math.floor(len(horizontal) / 2):]
            title = horizontal[1:] + text + horizontal
        else:
            horizontal = horizontal[len(horizontal) // 2:]
            title = horizontal + text + horizontal

    return title


def make_context_text(text, padding: int, width: int, text_alignment: str, height: int):
    text = ansi_align(text, align=text_alignment)
    lines = text.split(NEWLINE)
    text_width = widest_line(text)

    max_ = width - padding["left"] - padding["right"]

    if text_width > max_:
        new_lines = []
        for line in lines:
            created_lines = wrap_ansi(line, max_, hard=True)
            aligned_lines = ansi_align(created_lines, align=text_alignment)
            aligned_lines_array = aligned_lines.split("\n")
            longest_length = max(*map(string_width, aligned_lines_array))

            for aligned_line in aligned_lines_array:
                padded_line = None

                if text_alignment == "center":
                    padded_line = PAD * \
                        ((max_ - longest_length) / 2) + aligned_line
                elif text_alignment == "right":
                    padded_line = PAD * (max_ - longest_length) + aligned_line
                else:
                    padded_line = aligned_line

                new_lines.append(padded_line)

        lines = new_lines

    if text_alignment == "center" and text_width < max_:
        lines = list(
            map(lambda line: PAD * ((max_ - text_width) // 2) + line, lines))
    elif text_alignment == "right" and text_width < max_:
        lines = list(map(lambda line: PAD * (max - text_width) + line, lines))

    padding_left = PAD * padding["left"]
    padding_right = PAD * padding["right"]

    lines = list(map(lambda line: padding_left + line + padding_right, lines))

    def line_mapper(line):
        if width - string_width(line) > 0:
            return line + PAD * (width - string_width(line))

        return line
    lines = list(map(line_mapper, lines))

    if padding["top"] > 0:
        lines = [PAD * width] * padding["top"] + lines

    if padding["bottom"] > 0:
        lines = lines + [PAD * width] * padding["bottom"]

    if height and len(lines) > height:
        lines = lines[0:height]
    elif height and len(lines) < height:
        lines = lines + [PAD * width] * (height - len(lines))

    return NEWLINE.join(lines)


def box_content(content, content_width, margin, border_style: str, title_alignment: str = None, title: str = None, float: str = None, border_color: str = None, dim_border: bool = None, background_color: str = None):
    def colorize_border(border):
        new_border = (fg(border_color) + border + attr("reset")
                      ) if border_color else border
        return (attr("dim") + new_border + attr("reset")) if dim_border else new_border

    def colorize_content(content):
        return (bg(background_color) + content + attr("reset")) if background_color else content

    chars = get_border_chars(border_style)
    columns = terminal_columns()
    margin_left = " " * margin["left"]

    if float == "center":
        margin_width = max((columns - content_width - BORDERS_WIDTH) // 2, 0)
        margin_left = " " * margin_width
    elif float == "right":
        margin_width = max(columns - content_width -
                           margin["right"] - BORDERS_WIDTH, 0)
        margin_left = " " * margin_width

    top = colorize_border(NEWLINE * margin["top"] + margin_left + chars["topLeft"] + (make_title(
        title, chars["top"] * content_width, title_alignment) if title else (chars["top"] * content_width)) + chars["topRight"])
    bottom = colorize_border(margin_left + chars["bottomLeft"] + chars["bottom"]
                             * content_width + chars["bottomRight"] + NEWLINE * margin["bottom"])

    lines = content.split(NEWLINE)
    middle = NEWLINE.join(map(lambda line: margin_left + colorize_border(
        chars["left"]) + colorize_content(line) + colorize_border(chars["right"]), lines))

    return top + NEWLINE + middle + NEWLINE + bottom


def sanitize_options(fullscreen: bool | Callable, width: int = None, height: int = None):
    if fullscreen:
        __size = os.get_terminal_size()
        new_dimensions = [__size.columns, __size.lines]

        if type(fullscreen) != bool:
            new_dimensions = fullscreen(*new_dimensions)

        if not width:
            width = new_dimensions[0]

        if not height:
            height = new_dimensions[1]

    if width:
        width = max(1, width - BORDERS_WIDTH)

    if height:
        height = max(1, height - BORDERS_WIDTH)

    return fullscreen, width, height


def determine_dimensions(text, margin, padding, title: str = None, fullscreen: bool = None, width: int = None, height: int = None):
    fullscreen, width, height = sanitize_options(fullscreen, width, height)

    width_override = width != None
    columns = terminal_columns()
    max_width = columns - margin["left"] - margin["right"] - BORDERS_WIDTH

    widest = widest_line(wrap_ansi(text, columns - BORDERS_WIDTH,
                         hard=True, trim=False)) + padding["left"] + padding["right"]

    if title and width_override:
        title = title[0:max(0, width - 2)]

        if title:
            title = " " + title + " "
    elif title:
        title = title[0:max(0, max_width - 2)]

        if title:
            title = " " + title + " "

            if string_width(title) > widest:
                width = string_width(title)

    width = width if width else widest

    if not width_override:
        if (margin["left"] and margin["right"]) and width > max_width:
            space_for_margins = columns - width - BORDERS_WIDTH
            multiplier = space_for_margins / (margin["left"] + margin["right"])

            margin["left"] = max(0, math.floor(margin["left"] * multiplier))
            margin["right"] = max(0, math.floor(margin["right"] * multiplier))

        width = min(width, columns - BORDERS_WIDTH -
                    margin["left"] - margin["right"])

    if width - (padding["left"] + padding["right"]) <= 0:
        padding["left"] = 0
        padding["right"] = 0

    if height and height - (padding["top"] + padding["bottom"]) <= 0:
        padding["top"] = 0
        padding["bottom"] = 0

    return margin, padding, title, fullscreen, width, height


def boxpy(text: str, width: int = None, height: int = None, fullscreen: bool | Callable = None, margin=0, padding=0, border_style="single", dim_border: bool = False, text_alignment="left", float="left", title_alignment="left", title=None, border_color: str = None, background_color: str = None) -> str:
    padding = get_object(padding)
    margin = get_object(margin)

    margin, padding, title, fullscreen, width, height = determine_dimensions(
        text, margin, padding, title, fullscreen, width, height)
    text = make_context_text(text, padding, width, text_alignment, height)

    return box_content(text, width, margin, border_style, title_alignment, title, float, border_color, dim_border, background_color)
