from .string_width import string_width
from .ansi_styles import ansi_styles
from .strip_ansi import strip_ansi
import math
import re

ESCAPES = set([
    '\u001B',
    '\u009B'
])

END_CODE = 39
ANSI_ESCAPE_BELL = '\u0007'
ANSI_CSI = '['
ANSI_OSC = ']'
ANSI_SGR_TERMINATOR = 'm'
ANSI_ESCAPE_LINK = f"{ANSI_OSC}8;;"


def wrap_ansi_code(code):
    return f"{ESCAPES[0]}{ANSI_CSI}{code}{ANSI_SGR_TERMINATOR}"


def wrap_ansi_hyperlink(uri):
    return f"{ESCAPES[1]}{ANSI_ESCAPE_LINK}{uri}{ANSI_ESCAPE_BELL}"


def word_lengths(string):
    return list(map(string_width, string.split(" ")))


def wrap_word(rows, word, columns):
    characters = word.copy()

    is_inside_escape = False
    is_inside_link_escape = False
    visible = string_width(strip_ansi(rows[-1]))

    for index, character in enumerate(characters):
        character_length = string_width(character)

        if visible + character_length <= columns:
            rows[-1] += character
        else:
            rows.append(character)
            visible = 0

        if character in ESCAPES:
            is_inside_escape = True
            is_inside_link_escape = "".join(
                characters[index + 1:]).startswith(ANSI_ESCAPE_LINK)

        if is_inside_escape:
            if is_inside_link_escape:
                if character == ANSI_ESCAPE_BELL:
                    is_inside_escape = False
                    is_inside_link_escape = False
            elif character == ANSI_SGR_TERMINATOR:
                is_inside_escape = False

            continue

        visible += character_length

        if visible == columns and index < len(characters) - 1:
            rows.append("")
            visible = 0

    if not visible and len(rows[-1]) > 0 and len(rows) > 1:
        rows[-2] += rows.pop()


def string_visible_trim_spaces_right(string):
    words = string.split(" ")
    last = len(words)

    while last > 0:
        if string_width(words[last - 1] > 0):
            break

        last -= 1

    if last == len(words):
        return string

    return " ".join(words[0:last]) + words[last:].join("")


def exec(string, columns, trim=True, word_wrap=True, hard=False):
    global escape_code
    global escape_url

    if trim and string.strip() == "":
        return ""

    return_value = ""
    escape_code = None
    escape_url = None

    lengths = word_lengths(string)
    rows = [""]

    for index, word in enumerate(string.split(" ")):
        if trim:
            rows[-1] = rows[-1].lstrip()

        row_length = string_width(rows[-1])

        if index != 0:
            if row_length >= columns and (not word_wrap or not trim):
                rows.append("")
                row_length = 0

            if row_length > 0 or not trim:
                rows[-1] += " "
                row_length += 1

        if hard and lengths[index] > columns:
            remaining_columns = columns - row_length
            breaks_starting_this_line = 1 + \
                math.floor((lengths[index] - remaining_columns - 1) / columns)
            breaks_starting_next_line = math.floor(
                (lengths[index] - 1) / columns)

            if breaks_starting_next_line < breaks_starting_this_line:
                rows.append("")

            wrap_word(rows, word, columns)
            continue

        if row_length + lengths[index] > columns and row_length > 0 and lengths[index] > 0:
            if word_wrap == False and row_length < columns:
                wrap_word(rows, word, columns)
                continue

            rows.append("")

        if row_length + lengths[index] > columns and not word_wrap:
            wrap_word(rows, word, columns)
            continue

        rows[-1] += word

    if trim:
        rows = list(map(string_visible_trim_spaces_right, rows))

    pre = "\n".join(rows)

    for index, character in enumerate(pre):
        return_value += character

        if character in ESCAPES:
            regex = re.compile(
                f"(?:\\{ANSI_CSI}(?P<code>\\d+)m|\\{ANSI_ESCAPE_LINK}(?P<uri>.*){ANSI_ESCAPE_BELL})")
            matched = regex.match("".join(pre[index:]))

            if matched and matched.group("code"):
                code = int(matched.group("code"))
                escape_code = None if code == END_CODE else code
            elif matched and matched.group("uri"):
                escape_url = None if len(matched.group(
                    "uri")) == 0 else matched.group("uri")

        if escape_code:
            code = ansi_styles.codes.get(int(escape_code))
        else:
            code = None

        if index + 1 < len(pre) and pre[index + 1] == "\n":
            if escape_url:
                return_value += wrap_ansi_hyperlink("")

            if escape_code and code:
                return_value += wrap_ansi_code(code)
        elif character == "\n":
            if escape_code and code:
                return_value += wrap_ansi_code(escape_code)

            if escape_url:
                return_value += wrap_ansi_hyperlink(escape_url)

    return return_value


def wrap_ansi(string, columns, hard=False, trim=True, word_wrap=True):
    return "\n".join(map(lambda line: exec(line, columns, trim, word_wrap, hard), string.replace("\r\n", "\n").split("\n")))
