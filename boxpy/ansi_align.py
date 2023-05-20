from .string_width import string_width
import math


def ansi_align(text, align="center", split="\n", pad=" "):
    if not text:
        return text

    if align == "left":
        return text
    width_diffn = half_diff if align != "right" else full_diff

    return_string = False
    if type(text) != list:
        return_string = True
        text = text.split(split)

    global max_width
    max_width = 0

    def text_mapper(line):
        global max_width

        width = string_width(line)
        max_width = max(width, max_width)

        return {"str": line, "width": width}

    text = text.copy()
    for i, line in enumerate(text):
        text[i] = text_mapper(line)

    def text_mapper2(obj):
        return width_diffn(max_width, obj["width"]) * pad + obj["str"]

    for i, line in enumerate(text):
        text[i] = text_mapper2(line)

    return split.join(text) if return_string else text


def left(text): return ansi_align(text, align="left")
def center(text): return ansi_align(text, align="center")
def right(text): return ansi_align(text, align="right")


def half_diff(max_width, cur_width):
    return math.floor((max_width - cur_width) / 2)


def full_diff(max_width, cur_width):
    return max_width - cur_width
