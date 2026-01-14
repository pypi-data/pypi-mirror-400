#!/usr/bin/env python
# coding: utf-8

import re
import string


def percentage(percentage, total=100, ptn="{0}"):
    """
    Build a `Str` instance from pattern `ptn` and colorize it with color blue,
    green, yellow or red for value of `precentage` from 0 to `total`.

    E.g., following snippet builds a blue text "it is 20":

        percentage(20, total=80, ptn='it is {0}')

    Args:
        percentage: value to render.

        total: upper bound of percentage. By default it is 100.

        ptn: a pattern to create the text. By default it is `{0}`.

    Returns:
        Str: colored text.

    """
    if total > 0:
        color = fading_color(percentage, total)
    else:
        color = fading_color(-total - percentage, -total)
    return Str(ptn.format(percentage), color)


class Str(object):
    """
    `Str` is a string like object in terminal on Unix.
    `Str` provides with basic string operations and methods such as
    `len(s)`: length.
    `s + t`: concat two strings.
    `s * 10`: repeat a string.
    `s == t`: equal.
    `splitliens()`.
    `split()`.
    `join()`.

    Args:

        plain_str:
            the string to colourize.

        color:
            the color of **plain_str**.
            It can also be a named color such as:
            `blue` `cyan` `green` `purple` `red` `white` `yellow`
            `optimal` `normal` `loaded` `warn` `danger`.

            A int value colour must be in range of `[0-256]`.
    """

    def __init__(self, v, color=None, prompt=True):
        if isinstance(color, str):
            color = _named_colors[color]

        if isinstance(v, Str):
            vs = "".join([x[0] for x in v.elts])
            self.elts = [(vs, color)]
        else:
            self.elts = [(str(v), color)]

        self._prompt = prompt

    def __str__(self):
        rst = []
        for e in self.elts:
            if len(e[0]) == 0:
                continue

            if e[1] is None:
                val = e[0]
            else:
                _clr = "\033[38;5;" + str(e[1]) + "m"
                _rst = "\033[0m"

                if self._prompt:
                    _clr = "\001" + _clr + "\002"
                    _rst = "\001" + _rst + "\002"

                val = _clr + str(e[0]) + _rst

            rst.append(val)

        return "".join(rst)

    def __len__(self):
        return sum([len(x[0]) for x in self.elts])

    def __add__(self, other):
        prompt = self._prompt
        if isinstance(other, Str):
            prompt = prompt or other._prompt

        c = Str("", prompt=prompt)
        if isinstance(other, Str):
            c.elts = self.elts + other.elts
        else:
            c.elts = self.elts[:] + [(str(other), None)]
        return c

    def __mul__(self, num):
        c = Str("", prompt=self._prompt)
        c.elts = self.elts * num
        return c

    def __eq__(self, other):
        if not isinstance(other, Str):
            return False
        return str(self) == str(other) and self._prompt == other._prompt

    def _find_sep(self, line, sep):
        ma = re.search(sep, line)
        if ma is None:
            return -1, 0

        return ma.span()

    def _recover_colored_str(self, colored_chars):
        rst = Str("")
        n = len(colored_chars)
        if n == 0:
            return rst

        head = list(colored_chars[0])
        for ch in colored_chars[1:]:
            if head[1] == ch[1]:
                head[0] += ch[0]
            else:
                rst += Str(head[0], head[1])
                head = list(ch)
        rst += Str(head[0], head[1])

        return rst

    def _split(self, line, colored_chars, sep, maxsplit, keep_sep, keep_empty):
        rst = []
        n = len(line)
        i = 0
        while i < n:
            if maxsplit == 0:
                break

            s, e = self._find_sep(line[i:], sep)

            if s < 0:
                break

            edge = s
            if keep_sep:
                edge = e

            rst.append(self._recover_colored_str(colored_chars[i : i + edge]))

            maxsplit -= 1
            i += e

        if i < n:
            rst.append(self._recover_colored_str(colored_chars[i:]))

        # sep in the end
        # 'a b '  ->  ['a', 'b', '']
        elif keep_empty:
            rst.append(Str(""))

        return rst

    def _separate_str_and_colors(self):
        colored_char = []
        line = ""
        for elt in self.elts:
            for c in elt[0]:
                colored_char.append((c, elt[1]))
            line += elt[0]

        return line, colored_char

    def splitlines(self, *args):
        # to verify arguments
        "".splitlines(*args)

        sep = "\r(\n)?|\n"
        maxsplit = -1
        keep_empty = False
        keep_sep = False
        if len(args) > 0:
            keep_sep = args[0]

        line, colored_chars = self._separate_str_and_colors()

        return self._split(line, colored_chars, sep, maxsplit, keep_sep, keep_empty)

    def split(self, *args):
        # to verify arguments
        "".split(*args)

        sep, maxsplit = (list(args) + [None, None])[:2]
        if maxsplit is None:
            maxsplit = -1
        keep_empty = True
        keep_sep = False

        line, colored_chars = self._separate_str_and_colors()

        i = 0
        if sep is None:
            sep = r"\s+"
            keep_empty = False

            # to skip whitespaces at the beginning
            # ' a b'.split() -> ['a', 'b']
            n = len(line)
            while i < n and line[i] in string.whitespace:
                i += 1

        return self._split(line[i:], colored_chars[i:], sep, maxsplit, keep_sep, keep_empty)

    def join(self, iterable):
        rst = Str("")
        for i in iterable:
            if len(rst) == 0:
                rst += i
            else:
                rst += self + i
        return rst


def fading_color(v, total):
    """
    Returns a color visually represents a precentage from `v` to `total`
    It returns blue for small `v`, then green, yellow and red if `v` is close to `total`.

    Args:

        v:
            a value between 0 and `total`.

        total:
            upper boundary.

    Returns:
        int: a value used in terminal.
    """
    return _clrs[_fading_idx(v, total)]


def _fading_idx(v, total=100):
    n_colors = len(_clrs)
    pos = int(v * n_colors / (total + 0.0001) + 0.5)
    pos = min(pos, n_colors - 1)
    pos = max(pos, 0)
    return pos


#  blue green yellow red
_clrs = [63, 67, 37, 36, 41, 46, 82, 118, 154, 190, 226, 220, 214, 208, 202, 196]

_named_colors = {
    # by emergence levels
    "danger": _clrs[_fading_idx(100)],
    "warn": 3,
    "loaded": _clrs[_fading_idx(30)],
    "normal": 7,
    "optimal": _clrs[_fading_idx(0)],
    "dark": _clrs[1],
    # for human
    "black": 0,
    "darkgrey": 0,
    "darkred": 1,
    "darkgreen": 2,
    "darkyellow": 3,
    "darkblue": 4,
    "darkpurple": 5,
    "darkcyan": 6,
    "darkwhite": 7,
    "grey": 8,
    "red": 9,
    "green": 10,
    "yellow": 11,
    "blue": 12,
    "purple": 13,
    "cyan": 14,
    "white": 15,
}


def danger(v):
    return Str(v, "danger")


def warn(v):
    return Str(v, "warn")


def loaded(v):
    return Str(v, "loaded")


def normal(v):
    return Str(v, "normal")


def optimal(v):
    return Str(v, "optimal")


def dark(v):
    return Str(v, "dark")


def blue(v):
    return Str(v, "blue")


def cyan(v):
    return Str(v, "cyan")


def green(v):
    return Str(v, "green")


def yellow(v):
    return Str(v, "yellow")


def red(v):
    return Str(v, "red")


def purple(v):
    return Str(v, "purple")


def white(v):
    return Str(v, "white")


def darkblue(v):
    return Str(v, "darkblue")


def darkcyan(v):
    return Str(v, "darkcyan")


def darkgreen(v):
    return Str(v, "darkgreen")


def darkyellow(v):
    return Str(v, "darkyellow")


def darkred(v):
    return Str(v, "darkred")


def darkpurple(v):
    return Str(v, "darkpurple")


def darkwhite(v):
    return Str(v, "darkwhite")
