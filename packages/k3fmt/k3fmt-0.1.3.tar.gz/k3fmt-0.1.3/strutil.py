import re
import os
import errno
import string
import subprocess
import k3color

listtype = (tuple, list)

invisible_chars = "".join(map(chr, list(range(0, 32))))
invisible_chars_re = re.compile("[%s]" % re.escape(invisible_chars))


def break_line(linestr, width):
    lines = linestr.splitlines()
    rst = []

    space = " "
    if isinstance(linestr, k3color.Str):
        space = k3color.Str(" ")

    for line in lines:
        words = line.split(" ")

        buf = words[0]
        for word in words[1:]:
            if len(word) + len(buf) + 1 > width:
                rst.append(buf)
                buf = word
            else:
                buf += space + word

        if buf != "":
            rst.append(buf)

    return rst


def line_pad(linestr, padding=""):
    """

    :param linestr: multiple line string with `\n` as line separator.
    :param padding: left padding string to add before each line.
    It could also be a callable object that returns a string.
    This is useful when creating dynamic padding.

    :return: multiple line string with `\n` as line separator, with left padding added.
    """
    lines = linestr.split("\n")

    if type(padding) in (str, bytes):
        lines = [padding + x for x in lines]

    elif callable(padding):
        lines = [padding(x) + x for x in lines]

    lines = "\n".join(lines)

    return lines


def _to_str(y):
    if isinstance(y, k3color.Str):
        pass
    elif isinstance(y, int):
        y = str(y)
    elif isinstance(y, listtype):
        y = str(y)

    return y


def struct_repr(data, key=None):
    """
    Render primitive or composite data to a structural representation string list.
    :param data: a number, string, list or dict to render to a structural representation.
    :param key: is a callable that is used to sort dict keys. It is used in sort: `keys.sort(key=key)`.
    :return: a list of string.
    Render a data to a multi-line structural(yaml-like) representation.
    a = {
    1: 3,
    'x': {1:4, 2:5},
    'l': [1, 2, 3],
    }
    for l in struct_repr(a):

        print l
    """
    # Output:
    # 1 : 3
    # l : - 1
    #     - 2
    #     - 3
    # x : 1 : 4
    # 2 : 5

    if type(data) in listtype:
        if len(data) == 0:
            return ["[]"]

        max_width = 0
        elt_lines = []
        for elt in data:
            sublines = struct_repr(elt)
            sublines_max_width = max([len(x) for x in sublines])

            if max_width < sublines_max_width:
                max_width = sublines_max_width

            elt_lines.append(sublines)

        lines = []
        for sublines in elt_lines:
            # - subline[0]
            #   subline[1]
            #   ...

            lines.append("- " + sublines[0].ljust(max_width))

            for line in sublines[1:]:
                lines.append("  " + line.ljust(max_width))

        return lines

    elif type(data) is dict:
        if len(data) == 0:
            return ["{}"]

        max_k_width = 0
        max_v_width = 0

        kvs = []

        for k, v in data.items():
            k = utf8str(k)
            sublines = struct_repr(v)
            sublines_max_width = max([len(x) for x in sublines])

            if max_k_width < len(k):
                max_k_width = len(k)

            if max_v_width < sublines_max_width:
                max_v_width = sublines_max_width

            kvs.append((k, sublines))

        kvs.sort(key=key)

        lines = []
        for k, sublines in kvs:
            # foo : sub-0
            #       sub-1
            #   b : sub-0
            #       sub-0

            lines.append(k.rjust(max_k_width) + " : " + sublines[0].ljust(max_v_width))

            for line in sublines[1:]:
                lines.append(" ".rjust(max_k_width) + "   " + line.ljust(max_v_width))

        return lines

    else:
        data = filter_invisible_chars(data)
        return [utf8str(data)]


def filter_invisible_chars(data):
    """
    Filters invisible characters in a string or a unicode object
    :param data: a string or unicode object to filter invisible characters
    :return: a filtered string or unicode object
    """
    # from pykit.strutil import filter_invisible_chars
    # cases = [
    #     "1273883926293937729\000\001\031",
    #     "\x00\x01\x02\x03\x04\005",
    #     u"1122299299299299292",
    #     u"\x00\x01\x02\x03\x04\005",
    # ]
    #
    # rst = []
    # for case in cases:
    #     rst.append(strutil.filter_invisible_chars(case))
    #
    # for r in rst:
    #     print(r)
    # '1273883926293937729'
    # ''
    # u'1122299299299299292'
    # u''
    if type(data) not in (bytes, str):
        return data

    return invisible_chars_re.sub("", data)


def _get_key_and_headers(keys, rows):
    if keys is None:
        if len(rows) == 0:
            keys = []
        else:
            r0 = rows[0]

            if type(r0) is dict:
                keys = list(r0.keys())
                keys.sort()
            elif type(r0) in listtype:
                keys = [i for i in range(len(r0))]
            else:
                keys = [""]

    _keys = []
    column_headers = []

    for k in keys:
        if type(k) not in listtype:
            k = [k, k]

        _keys.append(k[0])
        column_headers.append(str(k[1]))

    return _keys, column_headers


def utf8str(s):
    if isinstance(s, bytes):
        return str(s, "utf-8")
    return str(s)


def format_line(items, sep=" ", aligns=""):
    """
    It formats a list in a multi row manner.
    It is compatible with colored string such as those created with `strutil.blue("blue-text")`.
    :param items: elements in a line.
    Each element could be a `string` or a `list` of `string`.
    If it is a `list` of `string`, it would be rendered as a multi-row
    element.
    :param sep: specifies the separator between each element in a line.
    By default it is a single space `" "`.
    :param aligns: specifies alignment for each element.
    -   `l` for left-align.
    -   `r` for right-align.
    If no alignment specified for i-th element, it will be aligned to right by default.
    :return: formatted string.
    format a line with multi-row columns.
    """
    # items = [ 'name:',
    #           [ 'John',
    #             'j is my nick'],
    #           [ 'age:' ],
    #           [ 26, ],
    #           [ 'experience:' ],
    #           [ '2000 THU',
    #             '2006 sina',
    #             '2010 other'
    #             ],
    #           ]
    # format_line(items, sep=' | ', aligns = 'llllll')
    #
    # outputs:
    # name: | John         | age: | 26 | experience: | 2000 THU
    # | j is my nick |      |    |             | 2006 sina
    # |              |      |    |             | 2010 other

    aligns = [x for x in aligns] + [""] * len(items)
    aligns = aligns[: len(items)]
    aligns = ["r" if x == "r" else x for x in aligns]

    items = [(x if type(x) in listtype else [x]) for x in items]

    items = [[_to_str(y) for y in x] for x in items]

    maxHeight = max([len(x) for x in items] + [0])

    def max_width(x):
        return max([y.__len__() for y in x] + [0])

    widths = [max_width(x) for x in items]

    items = [(x + [""] * maxHeight)[:maxHeight] for x in items]

    lines = []
    for i in range(maxHeight):
        line = []
        for j in range(len(items)):
            width = widths[j]
            elt = items[j][i]

            actualWidth = elt.__len__()
            elt = utf8str(elt)
            if actualWidth < width:
                padding = " " * (width - actualWidth)
                if aligns[j] == "l":
                    elt = elt + padding
                else:
                    elt = padding + elt

            line.append(elt)

        line = sep.join(line)

        lines.append(line)

    return "\n".join(lines)


def format_table(rows, keys=None, colors=None, sep=" | ", row_sep=None):
    """
    Render a list of data into a table.
    Number of rows is `len(rows)`.
    Number of columns is `len(rows[0])`.
    :param rows: list of items to render.
    Element of list can be number, string, list or dict.
    :param keys: specifies indexes(for list) or keys(for dict) to render.
    It is a list.
    Indexes or keys those are not in this list will not be rendered.
    It can also be used to specify customized column headers, if element in
    list is a 2-element tuple or list:
    :param colors: specifies the color for each column.
    It is a list of color values in number or color name strings.
    If length of `colors` is smaller than the number of columns(the number of
    indexes of a list, or keys of a dict), the colors are repeated for columns
    after.
    :param sep: specifies char to separate rows.
    By default it is None, it means do not add line separator.
    :param row_sep: specifies column separator char.
    By default it is `" | "`.
    :return: a list of string.
    """
    keys, column_headers = _get_key_and_headers(keys, rows)
    colors = _get_colors(colors, len(keys))

    # element of lns is a mulit-column line
    # lns = [
    #         # line 1
    #         [
    #                 # column 1 of line 1
    #                 ['name:', # row 1 of column 1 of line 1
    #                  'foo',   # row 2 of column 1 of line 1
    #                 ],
    #
    #                 # column 2 of line 1
    #                 ['school:',
    #                  'foo',
    #                  'bar',
    #                 ],
    #         ],
    # ]

    # headers
    lns = [[[a + ": "] for a in column_headers]]

    for row in rows:
        if row_sep is not None:
            lns.append([[None] for k in keys])

        if type(row) is dict:
            ln = [struct_repr(row.get(k, "")) for k in keys]

        elif type(row) in listtype:
            ln = [struct_repr(row[int(k)]) if len(row) > int(k) else "" for k in keys]

        else:
            ln = [struct_repr(row)]

        lns.append(ln)

    def get_max_width(cols):
        return max([len(utf8str(c[0])) for c in cols] + [0])

    max_widths = [get_max_width(cols) for cols in zip(*lns)]

    rows = []
    for row in lns:
        ln = []

        for i in range(len(max_widths)):
            color = colors[i]
            w = max_widths[i]

            ln.append([k3color.Str(x.ljust(w), color) if x is not None else row_sep * w for x in row[i]])

        rows.append(format_line(ln, sep=sep))

    return rows


def _get_colors(colors, col_n):
    if colors is None:
        colors = []

    colors = colors or ([None] * col_n)

    while len(colors) < col_n:
        colors.extend(colors)

    colors = colors[:col_n]

    return colors


def _findquote(line, quote):
    if len(quote) == 0:
        return -1, -1, []

    i = 0
    n = len(line)
    escape = []
    while i < n:
        if line[i] == "\\":
            escape.append(i)
            i += 2
            continue

        if line[i] in quote:
            quote_s = i - len(escape)

            j = i
            i += 1
            while i < n and line[i] != line[j]:
                if line[i] == "\\":
                    escape.append(i)
                    i += 2
                    continue

                i += 1

            if i < n:
                quote_e = i - len(escape)
                return quote_s, quote_e, escape
            else:
                return quote_s, -1, escape

        i += 1

    return -1, -1, escape


def tokenize(line, sep=None, quote="\"'", preserve=False):
    r"""
    :param line: the line to tokenize.
    :param sep: is None or a non-empty string separator to tokenize with.
    If sep is None, runs of consecutive whitespace are regarded as a single
    separator, and the result will contain no empty strings at the start or end
    if the string has leading or trailing whitespace. Consequently, splitting
    an empty string or a string consisting of just whitespace with a None
    separator returns `[]`. Just like `str.split(None)`.
    By default, `sep` is None.
    :param quote:Every character in `quote` is regarded as a quote. Add a `\` prefix to make
    an exception. Segment between the same quotes is preserved.
    By default, `quote` is `'"\''`.

    :param preserve: preserve the quote itself if `preserve` is `True`.
    By default, `preserve` is `False`.
    :return: a list of string.
    """

    if sep == quote:
        raise ValueError("diffrent sep and quote is required")

    if sep is None:
        if len(line) == 0:
            return []
        line = line.strip()

    rst = [""]
    n = len(line)
    i = 0
    while i < n:
        quote_s, quote_e, escape = _findquote(line[i:], quote)

        if len(escape) > 0:
            lines = []
            x = 0
            for e in escape:
                lines.append(line[x : i + e])
                x = i + e + 1
            lines.append(line[x:])
            line = "".join(lines)
            n = len(line)

        if quote_s < 0:
            sub = n
        else:
            sub = i + quote_s

        if i < sub:
            sub_rst = line[i:sub].split(sep)
            if sep is None:
                if line[sub - 1] in string.whitespace:
                    sub_rst.append("")
                if line[i] in string.whitespace:
                    sub_rst.insert(0, "")

            head = rst.pop()
            sub_rst[0] = head + sub_rst[0]
            rst += sub_rst

        if quote_s < 0:
            break

        # discard incomplete
        # 'a b"c'  ->  ['a']
        if quote_e < 0:
            rst.pop()
            break

        head = rst.pop()

        if preserve:
            head += line[i + quote_s : i + quote_e + 1]
        else:
            head += line[i + quote_s + 1 : i + quote_e]

        rst.append(head)
        i += quote_e + 1

    return rst


def parse_colon_kvs(data):
    data = tokenize(data, quote="\"'")

    ret = {}
    for buf in data:
        if ":" not in buf:
            raise ValueError('invalid arguments, argumentsneed key-val like: "k:v"')

        k, v = buf.split(":", 1)

        ret[k] = v

    return ret


def page(lines, max_lines=10, control_char=True, pager=("less",)):
    """
    Display `lines` of string in console, with a pager program (`less`) if too many
    lines.

    It could be used in a interactive tool to display large content.

    It output strings directly to stdout.
    :param lines: is `list` of lines to display.
    :param max_lines: specifies the max lines not to use a pager.
    By default it is 10 lines.
    :param control_char: specifies if to interpret controlling chars, such as color char in terminal.
    :param pager: specifies the program as a pager.
    It is a list of command and argument.
    By default it is `('less',)`.
    :return: Nothing
    """
    if len(lines) > max_lines:
        pp = {"stdin": subprocess.PIPE, "stdout": None, "stderr": None}

        cmd_pager = list(pager)
        if control_char:
            if pager == ("less",):
                cmd_pager += ["-r"]

        subproc = subprocess.Popen(cmd_pager, close_fds=True, cwd="./", **pp)

        try:
            out, err = subproc.communicate(bytes("\n".join(lines).encode("utf-8")))
        except IOError as e:
            if e[0] == errno.EPIPE:
                pass
            else:
                raise
        subproc.wait()
    else:
        os.write(1, bytes(("\n".join(lines) + "\n").encode("utf-8")))
