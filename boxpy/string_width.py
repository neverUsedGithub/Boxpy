from .strip_ansi import strip_ansi


def string_width(line):
    return len(strip_ansi(line))
