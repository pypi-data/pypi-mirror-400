# test_colors.py

from mykhcolors import red, green, yellow, bold, italic

def test_red():
    assert "\033[31m" in red("hello")
    assert red("hello").endswith("\033[0m")

def test_green():
    assert "\033[32m" in green("world")

def test_yellow():
    assert "\033[33m" in yellow("!")

def test_bold():
                 assert "\033[1m" in bold("hello")

def test_italic():
    assert "\033[3m" in italic("world")

def test_bold_yellow():
    assert "\033[1m\033[33m" in bold(yellow("hello"))
