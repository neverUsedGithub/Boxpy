# Boxpy

Boxpy is a Python library that offers a faithful recreation of the [boxen](https://github.com/sindresorhus/boxen/) module originally written in Node.js. It has been meticulously transpiled by hand from the source code, ensuring that the functionality and features of the original module are accurately reproduced in Python. With Boxpy, you can enjoy the same capabilities for generating customizable text boxes, creating visually appealing command-line interfaces, and adding stylish visual elements to your Python applications.

# Usage
```python
>>> from boxpy import boxpy
>>> boxpy("Hello, World!", padding=1)
    ┌───────────────────┐
    │                   │
    │   Hello, World!   │
    │                   │
    └───────────────────┘
>>> boxpy("Multiple\nLines", padding=1, text_alignment="center")
    ┌──────────────┐
    │              │
    │   Multiple   │
    │    Lines     │
    │              │
    └──────────────┘
>>> boxpy("Foo", title="Bar", title_alignment="center", text_alignment="center")
    ┌ Bar ┐
    │ Foo │
    └─────┘
```

# API
The following parameters can be used when calling the `boxpy` function.
- **text**: `str` - The text inside the box.
- **width**: `int` - The width of the box.
- **height**: `int` - The height of the box.
- **fullscreen**: `bool | Callable` - If `True` the box will take up the whole terminal, else its used to transform the `rows` and `cols` returned by `os.get_terminal_size()`.
- **margin**: `int` - The space outside the box.
- **padding**: `int` - The extra space inside the box.
- **border_style**: `"single" | "double" | "round" | "bold" | "single-double" | "double-single" | "classic" | "arrow" | dict` - Style of the border.
- **dim_border**: `bool` - Specify whether the border should have a dimmer color.
- **text_alignment**: `"left" | "center" | "right"` - Where the text should be centered.
- **float**: `"left" | "center" | "right"` - Where the box should horizontally be located.
- **title**: `str` - The title to display in the header of the box.
- **title_alignment**: `"left" | "center" | "right"` - Where the title should be located.
- **border_color**: `str` - The border's color. (using [termcolor](https://pypi.org/project/termcolor/))
- **background_color**: `str` - The box's background (using [termcolor](https://pypi.org/project/termcolor/))