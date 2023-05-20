from .string_width import string_width


def widest_line(string):
    line_width = 0

    for line in string.split("\n"):
        line_width = max(line_width, string_width(line))

    return line_width
