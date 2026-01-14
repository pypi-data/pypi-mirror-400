#!/usr/bin/env python2
# coding: utf-8


K = 1024**1
M = 1024**2
G = 1024**3
T = 1024**4
P = 1024**5
E = 1024**6
Z = 1024**7
Y = 1024**8

value_to_unit = {
    1: "",
    K: "K",
    M: "M",
    G: "G",
    T: "T",
    P: "P",
    E: "E",
    Z: "Z",
    Y: "Y",
}

unit_to_value = dict([(v, k) for (k, v) in value_to_unit.items() if v != ""])

integer_types = (type(0),)


def hunum_int(i, unit=None):
    i = int(i)

    if i < 0:
        minus = "-"
        i = -i
    else:
        minus = ""

    if unit is None:
        unit = K

        # keep at least 2 digit
        while i // unit > 0:
            unit *= K

        unit /= K

        while unit not in value_to_unit:
            unit /= K

    v = i * 1.0 / unit

    if v == int(v):
        return minus + "%d%s" % (v, value_to_unit[unit])

    if v > 10:
        vlen = 1
    elif v > 1:
        vlen = 2
    else:
        vlen = 3

    return minus + ("%." + str(vlen) + "f%s") % (v, value_to_unit[unit])


def readable(data, unit=None, include=None, exclude=None):
    """
    readable convert number or dict/list of number to string in a format easy to read for human.

    Args:
        data: could be a primitive type: `int` or `float`,
            or a non-primitive type object `list` or `dict`.

            -   For primitive type like `int`, it converts it to string.
            -   For non-primitive type like `dict`, it traverse recursively over all
                of its fields and convert them to string.

        unit(int): specifies the unit of the number in the result string.
            It could be one of: `1024` (K), `1024²` (M) ... `1024⁸` (Y).

            If it is None, a proper unit will be chosen to output the shortest string.
            For example, for `102400` it chooses `K`. For `10240000` it chooses `M`.

        include(bool): specifies to convert only a subset of the keys of a `dict` `data`.
            It could be a `list`, `tuple` or `set` of keys.

            -   It has no effect on a primitive `data`.
            -   It is not passed to sub `dict` or `list`.

        exclude(bool): specifies **NOT** to convert some of the keys of a `dict`
            `data`.  It could be a `list`, `tuple` or `set` of keys.

            -   It has no effect on a primitive `data`.
            -   It is not passed to sub `dict` or `list`.

    Returns:

        int/dict/list.

        -   For a primitive type data, it returns a string representing the number.
        -   For a `dict` or `list`, it makes a duplicate of `data` and convert its
            number fields.
            It leaves the original `data` intact.
    """

    if isinstance(data, dict):
        data = data.copy()

        keys = set(data.keys())
        if include is not None:
            keys = keys & set(include)

        if exclude is not None:
            keys = keys - set(exclude)

        for k in keys:
            data[k] = readable(data[k])

        return data

    elif isinstance(data, bool):
        # We have to deal with bool because for historical reason bool is
        # subclass of int.
        # When bool is introduced into python 2.2 it is represented with int,
        # similar to C.
        return data

    elif isinstance(data, list):
        return [readable(x) for x in data]

    elif isinstance(data, (str, bytes)):
        return data

    elif isinstance(data, integer_types):
        return hunum_int(data, unit=unit)

    elif isinstance(data, float):
        if data > 999:
            return hunum_int(int(data), unit=unit)
        elif abs(data) < 0.0000000001:
            return "0"
        else:
            return "%.2f" % (data)

    else:
        return data


def parseint(data, safe=None):
    """
    Same as `parsenum` but it always casts result to a `int` number.
    """
    return int(parsenum(data, safe=safe))


def parsenum(data, safe=None):
    """
    Parse humanized number string like `10.5K` to `int` or `float`.
    It also parses percentage number to `float`.

    Args:
        data(str): number string.

            Valid units are:
            `k`, `m`, `g`, `t`, `p`, `e`, `z` and `y`.
            Suffix `b` and `i` will be ignored.
            For example: `10.1K`, `10.1k`, `10.1Kb` and `10.1Ki` are all the same.

            For percentage number, valid unit is `%`.
            For example: `10.1%`.

        safe: if `safe` is `True` and data is not a valid number string, it silently
            returns the original `data`, instead of raising an `ValueError`.

            By default it is `False`.

    Returns:
        int/float.

    """

    if safe is None:
        safe = False

    original = data

    if isinstance(data, integer_types):
        return data

    if not isinstance(data, (str, bytes)):
        return data

    if isinstance(data, bytes):
        data = data.decode("utf-8")

    if data == "":
        return 0

    if data.endswith("%"):
        fl = float(data[:-1]) / 100.0
        return fl

    data = data.upper().rstrip("B").rstrip("I")

    unit_name = data[-1]

    try:
        if unit_name in unit_to_value:
            val = float(data[:-1]) * unit_to_value[unit_name]
        else:
            val = float(data)

        if val == int(val):
            val = int(val)

    except ValueError:
        if safe:
            val = original
        else:
            raise

    return val


# if __name__ == "__main__":
#     import doctest
#     doctest.testmod()
