import re
from itertools import chain, count, islice, repeat

__all__ = [
    'ITERATOR_FNS',
]

dct = dict(a=1, b=2, c=3)
tup = (1, 2, 3)
lst = [1, 2, 3]
st = {1, 2, 3}


def gen_fn():
    yield 1
    yield 2
    yield 3


def counter():
    i = 0

    def _next():
        nonlocal i
        i += 1
        return i

    return _next


patt = re.compile('.')

ITERATOR_FNS = (
    lambda: range(5),
    lambda: map(str, lst),
    lambda: filter(str.isupper, 'aBcDeF'),
    lambda: zip(tup, lst),
    lambda: iter(tup),
    lambda: iter(lst),
    lambda: iter(st),
    lambda: dct.items(),
    lambda: dct.keys(),
    lambda: dct.values(),
    lambda: chain(lst, lst, lst),
    lambda: islice(lst, 2),
    lambda: count(0, 3),
    lambda: repeat(9),
    lambda: (str(i) for i in lst),
    lambda: gen_fn(),
    lambda: iter(counter(), 5),
)
