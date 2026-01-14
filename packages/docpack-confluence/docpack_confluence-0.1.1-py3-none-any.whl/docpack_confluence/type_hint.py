# -*- coding: utf-8 -*-

import typing as T


T_ID_PATH = list[str] # Type alias: path from root to current node, e.g., ["id1", "id2", "id3"]


class HasRawData(T.Protocol):
    """Protocol for objects that have a raw_data attribute."""

    raw_data: dict[str, T.Any]


class CacheLike(T.Protocol):
    """Minimal cache protocol for duck typing."""

    def set(
        self,
        key: T.Any,
        value: T.Any,
        expire: float | int | None = None,
    ) -> T.Any: ...

    def get(
        self,
        key: T.Any,
        default: T.Any | None = None,
    ) -> T.Any: ...

    def delete(self, key: T.Any) -> bool: ...

    def clear(self) -> int: ...
