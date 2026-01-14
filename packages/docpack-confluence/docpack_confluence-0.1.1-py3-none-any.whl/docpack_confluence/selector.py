# -*- coding: utf-8 -*-

"""
Confluence page selector with include/exclude filter rules.

This module implements the filter language defined in the documentation,
supporting URL-based matching with wildcard syntax.
"""

import typing as T
import re
import enum
import dataclasses

from .type_hint import T_ID_PATH


class MatchMode(str, enum.Enum):
    """
    Defines how a pattern matches against a page's path.

    - SELF: Match only the node itself (no wildcard)
    - DESCENDANTS: Match all descendants, excluding the node itself (/*)
    - RECURSIVE: Match the node and all its descendants (/**)
    """

    SELF = "self"
    DESCENDANTS = "descendants"
    RECURSIVE = "recursive"

    def is_self(self) -> bool:  # pragma: no cover
        """Check if the mode is SELF."""
        return self == MatchMode.SELF

    def is_descendant(self) -> bool:  # pragma: no cover
        """Check if the mode is DESCENDANTS."""
        return self == MatchMode.DESCENDANTS

    def is_recursive(self) -> bool:  # pragma: no cover
        """Check if the mode is RECURSIVE."""
        return self == MatchMode.RECURSIVE


@dataclasses.dataclass(frozen=True)
class Pattern:
    """
    A matching pattern parsed from a Confluence URL.

    :param id: The page or folder ID extracted from the URL
    :param mode: The matching mode (SELF, DESCENDANTS, or RECURSIVE)
    """

    id: str
    mode: MatchMode

    def __repr__(self) -> str:
        suffix = {
            MatchMode.SELF: "",
            MatchMode.DESCENDANTS: "/*",
            MatchMode.RECURSIVE: "/**",
        }[self.mode]
        return f"Pattern({self.id!r}{suffix})"


# Regex patterns for parsing Confluence URLs
# Page URL: https://{domain}/wiki/spaces/{space_key}/pages/{page_id}/{title}
# Folder URL: https://{domain}/wiki/spaces/{space_key}/folder/{folder_id}?{params}
_PAGE_URL_PATTERN = re.compile(
    r"https?://[^/]+/wiki/spaces/[^/]+/pages/(\d+)(?:/[^/*]*)?"
)
_FOLDER_URL_PATTERN = re.compile(
    r"https?://[^/]+/wiki/spaces/[^/]+/folder/(\d+)(?:\?[^/*]*)?"
)


def parse_pattern(url: str) -> Pattern:
    """
    Parse a Confluence URL into a Pattern object.

    Supports three formats:
    - ``{url}`` -> MatchMode.SELF (match only the node)
    - ``{url}/*`` -> MatchMode.DESCENDANTS (match all descendants)
    - ``{url}/**`` -> MatchMode.RECURSIVE (match node and all descendants)

    :param url: Confluence page or folder URL, optionally with /* or /** suffix

    :returns: Parsed Pattern object

    :raises ValueError: If the URL format is not recognized
    """
    # Determine match mode from suffix
    if url.endswith("/**"):
        mode = MatchMode.RECURSIVE
        url = url[:-3]
    elif url.endswith("/*"):
        mode = MatchMode.DESCENDANTS
        url = url[:-2]
    else:
        mode = MatchMode.SELF

    # Try to match page URL
    match = _PAGE_URL_PATTERN.match(url)
    if match:
        return Pattern(id=match.group(1), mode=mode)

    # Try to match folder URL
    match = _FOLDER_URL_PATTERN.match(url)
    if match:
        return Pattern(id=match.group(1), mode=mode)

    raise ValueError(f"Invalid Confluence URL format: {url}")


def is_match(pattern: Pattern, id_path: T_ID_PATH) -> bool:
    """
    Check if a page's ID path matches the given pattern.

    :param pattern: The pattern to match against
    :param id_path: The page's full ID path from root to current node,
        e.g., ["p1", "f1", "p2"] means the page is at p1 -> f1 -> p2

    :returns: True if the path matches the pattern, False otherwise

    **Matching rules**:

    - SELF: The page's ID (last element) must equal pattern.id
    - DESCENDANTS: pattern.id must be an ancestor (not the page itself)
    - RECURSIVE: pattern.id must be in the path (ancestor or self)

    **Examples**::

        >>> path = ["p1", "f1", "p2"]  # page p2 under f1 under p1
        >>> is_match(Pattern("p2", MatchMode.SELF), path)
        True   # p2 is the page itself
        >>> is_match(Pattern("p1", MatchMode.SELF), path)
        False  # p1 is not the page itself
        >>> is_match(Pattern("p1", MatchMode.DESCENDANTS), path)
        True   # p2 is a descendant of p1
        >>> is_match(Pattern("p2", MatchMode.DESCENDANTS), path)
        False  # p2 has no descendants here
        >>> is_match(Pattern("p1", MatchMode.RECURSIVE), path)
        True   # p2 is under p1
        >>> is_match(Pattern("p2", MatchMode.RECURSIVE), path)
        True   # p2 is itself
    """
    if not id_path:
        return False

    target_id = pattern.id
    current_id = id_path[-1]
    is_in_path = target_id in id_path
    is_self = current_id == target_id

    if pattern.mode == MatchMode.SELF:
        # Only match if the current node IS the target
        return is_self
    elif pattern.mode == MatchMode.DESCENDANTS:
        # Match if target is an ancestor (in path but not the current node)
        return is_in_path and not is_self
    elif pattern.mode == MatchMode.RECURSIVE:
        # Match if target is in path (ancestor or self)
        return is_in_path
    else:
        return False


@dataclasses.dataclass
class Selector:
    """
    Page selector with include/exclude filter rules.

    :param include: List of URL patterns to include. Empty list means include all.
    :param exclude: List of URL patterns to exclude. Empty list means exclude nothing.

    **Priority**: exclude > include. If a page matches both, it is excluded.

    **Example**::

        selector = Selector(
            include=["https://example.atlassian.net/wiki/spaces/DEMO/pages/123/Title/**"],
            exclude=["https://example.atlassian.net/wiki/spaces/DEMO/pages/456/Other/*"],
        )

        # Check if a page should be included
        if selector.should_include(page_id_path):
            # Process this page
            ...
    """

    include: list[str] = dataclasses.field(default_factory=list)
    exclude: list[str] = dataclasses.field(default_factory=list)

    def __post_init__(self):
        # Parse URL strings into Pattern objects
        self._include_patterns: list[Pattern] = [
            parse_pattern(url) for url in self.include
        ]
        self._exclude_patterns: list[Pattern] = [
            parse_pattern(url) for url in self.exclude
        ]

    def _matches_any(self, patterns: list[Pattern], id_path: T_ID_PATH) -> bool:
        """Check if id_path matches any of the patterns."""
        return any(is_match(pattern, id_path) for pattern in patterns)

    def should_include(self, id_path: T_ID_PATH) -> bool:
        """
        Determine if a page should be included based on filter rules.

        :param id_path: The page's full ID path from root to current node

        :returns: True if the page should be included, False otherwise

        **Logic**:

        1. If exclude patterns exist and page matches any -> excluded
        2. If include patterns are empty -> included (include all)
        3. If include patterns exist and page matches any -> included
        4. Otherwise -> excluded
        """
        # Check exclude first (higher priority)
        if self._exclude_patterns and self._matches_any(
            self._exclude_patterns, id_path
        ):
            return False

        # Empty include means include all
        if not self._include_patterns:
            return True

        # Check if matches any include pattern
        return self._matches_any(self._include_patterns, id_path)

    def select(
        self,
        pages: T.Iterable[tuple[str, T_ID_PATH]],
    ) -> T.Iterator[tuple[str, T_ID_PATH]]:
        """
        Filter pages based on include/exclude rules.

        :param pages: Iterable of (page_id, id_path) tuples

        :returns: Iterator of pages that pass the filter
        """
        for page_id, id_path in pages:
            if self.should_include(id_path):
                yield page_id, id_path
