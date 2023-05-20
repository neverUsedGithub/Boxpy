import re

ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')

def strip_ansi(line):
  return ansi_escape.sub('', line)