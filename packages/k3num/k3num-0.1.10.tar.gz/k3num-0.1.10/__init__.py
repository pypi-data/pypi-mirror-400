"""
k3num convert numbers(or numbers in `dict` or `list`) to human readable
format in string::

    >>> readable(103425)
    '101.0K'
    >>> readable({ 'total': 10240, 'progress': [1, 1024*2.1, 1024*3.2], })
    {'total': '10K', 'progress': ['1', '2.10K', '3.20K']}
    >>> parsenum('5.2K')
    5324.8
    >>> parsenum('10%')
    0.1

Attributes:
    value_to_unit(dict): map of int to unit, e.g.: `1024 -> "K"`, `1024² -> "M"`.

        Usage::

            >>> value_to_unit[1024**2]
            'M'

            >>> unit_to_value['K']
            1024

    unit_to_value(dict): reverse map of `value_to_unit`.


k3num.Hex provides hex integer with arithmatic support.

Different ways to create a 4-byte crc32 hex str::

    >>> Hex(0x0102, 4)
    '00000102'
    >>> Hex(0x0102, 'crc32')
    '00000102'
    >>> Hex.crc32(0x0102)
    '00000102'
    >>> Hex('00000102', 'crc32')
    '00000102'
    >>> Hex.crc32('00000102')
    '00000102'


Create with a tuple of prefix and a filling byte::

    >>> Hex(('12', 1), 'crc32')
    '12010101'


Arithmetic operations::

    >>> Hex(0x0102, 'crc32') + 1
    '00000103'
    >>> Hex(0x0102, 'crc32') * 2
    '00000204'
    >>> Hex(0x0102, 'crc32') - 1000000
    '00000000'
    >>> Hex(0x0102, 'crc32') * 1000000000
    'ffffffff'


Iterate over sha1 space with a specific step::

    >>> Hex.sha1(0) + Hex.sha1(('10', 0))
    '1000000000000000000000000000000000000000'
    >>> Hex.sha1(0) + Hex.sha1(('10', 0)) * 2
    '2000000000000000000000000000000000000000'
"""

from importlib.metadata import version

__version__ = version("k3num")

from .readable import (
    K,
    M,
    G,
    T,
    P,
    E,
    Z,
    Y,
    readable,
    parsenum,
    parseint,
    value_to_unit,
    unit_to_value,
)

from .hex import (
    Hex,
)

__all__ = [
    "K",
    "M",
    "G",
    "T",
    "P",
    "E",
    "Z",
    "Y",
    "readable",
    "parsenum",
    "parseint",
    "value_to_unit",
    "unit_to_value",
    "Hex",
]
