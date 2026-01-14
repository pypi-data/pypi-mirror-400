# -*- coding: utf-8 -*-

from functools import cached_property
from diskcache import Cache

from .paths import path_enum


class One:
    @cached_property
    def cache(self) -> Cache:
        return Cache(str(path_enum.dir_cache))


one = One()
