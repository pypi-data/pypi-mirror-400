# -*- coding: utf-8 -*-

from sys import hexversion
from itertools import islice


def _batched(iterable, n, *, strict=False):  # pragma: no cover
    """Batch data into tuples of length *n*. If the number of items in
    *iterable* is not divisible by *n*:
    * The last batch will be shorter if *strict* is ``False``.
    * :exc:`ValueError` will be raised if *strict* is ``True``.

    >>> list(batched('ABCDEFG', 3))
    [('A', 'B', 'C'), ('D', 'E', 'F'), ('G',)]

    On Python 3.13 and above, this is an alias for :func:`itertools.batched`.
    """
    if n < 1:
        raise ValueError("n must be at least one")
    iterator = iter(iterable)
    while batch := tuple(islice(iterator, n)):
        if strict and len(batch) != n:
            raise ValueError("batched(): incomplete batch")
        yield batch


if hexversion >= 0x30D00A2:  # pragma: no cover
    from itertools import batched as itertools_batched

    def batched(iterable, n, *, strict=False):
        return itertools_batched(iterable, n, strict=strict)

    batched.__doc__ = _batched.__doc__
else:  # pragma: no cover
    batched = _batched
