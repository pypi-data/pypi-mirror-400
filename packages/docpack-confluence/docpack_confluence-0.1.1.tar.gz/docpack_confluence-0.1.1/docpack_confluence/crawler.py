# -*- coding: utf-8 -*-

"""
Confluence space crawler using Parent Clustering Algorithm.

This module provides efficient fetching of complete space hierarchies,
handling the Confluence API's depth=5 limitation by clustering boundary
nodes and fetching from parent level.
"""

import dataclasses
import gzip

import orjson

# fmt: off
from sanhe_confluence_sdk.api import Confluence
from sanhe_confluence_sdk.methods.descendant.get_page_descendants import GetPageDescendantsResponseResult
# fmt: on

from .constants import GET_PAGE_DESCENDANTS_MAX_DEPTH, DescendantTypeEnum
from .type_hint import T_ID_PATH, CacheLike
from .selector import Selector
from .shortcuts import get_descendants_of_page, get_descendants_of_folder

# Minimum depth required for the Parent Clustering Algorithm to work.
# Why depth >= 2?
#   - If depth=1: boundary nodes are direct children of root (depth=1)
#   - Their parent is the root itself, which is NOT in entity_pool
#   - _cluster_by_parents would return [(root, "page")], same as initial root
#   - Next iteration fetches same nodes (all duplicates), boundary_nodes=[]
#   - Result: only L1 nodes fetched, L2+ are missed!
# With depth >= 2:
#   - Boundary nodes at depth=N have parents at depth=N-1
#   - Parents ARE in entity_pool (fetched in same iteration)
#   - Clustering by parents allows algorithm to go deeper
MIN_DEPTH = 2

# Sanity check: ensure configured depth meets minimum requirement
assert GET_PAGE_DESCENDANTS_MAX_DEPTH >= MIN_DEPTH, (
    f"GET_PAGE_DESCENDANTS_MAX_DEPTH ({GET_PAGE_DESCENDANTS_MAX_DEPTH}) must be >= {MIN_DEPTH} "
    f"for Parent Clustering Algorithm to work correctly"
)


@dataclasses.dataclass
class Entity:
    """
    Represents a Confluence entity with its hierarchical path.

    :param lineage: List of nodes from this entity to root (reverse order).
        The first item is this entity, the last item is the root ancestor.
        Stored in reverse for efficient construction via append.
    """

    lineage: list[GetPageDescendantsResponseResult] = dataclasses.field(
        default_factory=list
    )

    @property
    def node(self) -> GetPageDescendantsResponseResult:
        """The current entity (first in the lineage)."""
        return self.lineage[0]

    @property
    def id_path(self) -> T_ID_PATH:
        """IDs from root to this entity."""
        return [n.id for n in reversed(self.lineage)]

    @property
    def title_path(self) -> list[str]:
        """Titles from root to this entity."""
        return [n.title for n in reversed(self.lineage)]

    @property
    def position_path(self) -> list[int]:
        """Child positions from root to this entity."""
        return [n.childPosition for n in reversed(self.lineage)]

    @property
    def id_breadcrumb_path(self) -> str:
        """
        ID breadcrumb path as a string (e.g., "root_id || parent_id || child_id").
        """
        return " ~ ".join(self.id_path)

    @property
    def title_breadcrumb_path(self) -> str:
        """
        Title breadcrumb path as a string (e.g., "Root Title || Parent Title || Child Title").
        """
        return " ~ ".join(self.title_path)

    @property
    def sort_key(self) -> list[int]:
        """
        Sorting key based on position_path for depth-first ordering.
        """
        return self.position_path


# ------------------------------------------------------------------------------
# Helper functions for crawl_descendants
# ------------------------------------------------------------------------------
def _build_lineage(
    node: GetPageDescendantsResponseResult,
    entity_pool: dict[str, "Entity"],
) -> list[GetPageDescendantsResponseResult]:
    """
    Build lineage list for a node by walking up the parent chain.

    :param node: The node to build lineage for
    :param entity_pool: Existing entities (used to look up parents)

    :returns: List of nodes from self to root: [self, parent, grandparent, ...]
        The list is in reverse order for efficient append during construction.
        Root ancestor is at the end of the list.

    **Example**::

        Hierarchy:  homepage -> p1 -> f2 -> p3 -> f4 -> p5
                    (L0)       (L1)  (L2)  (L3)  (L4)  (L5)

        When building lineage for p5:
        - entity_pool already has: {p1, f2, p3, f4}
        - Walk up: p5 -> f4 -> p3 -> f2 -> p1 -> (homepage not in pool, stop)
        - Result: [p5, f4, p3, f2, p1]  # reverse order

        Later, Entity.title_path reverses this to get root-to-leaf order:
        - title_path: ["p1", "f2", "p3", "f4", "p5"]
    """
    lineage: list[GetPageDescendantsResponseResult] = [node]
    current_id = node.parentId
    while current_id in entity_pool:
        parent_entity = entity_pool[current_id]
        lineage.append(parent_entity.node)
        current_id = parent_entity.node.parentId
    return lineage


def _fetch_iteration(
    client: Confluence,
    roots: list[tuple[int, str]],
    entity_pool: dict[str, "Entity"],
    depth: int,
) -> tuple[
    list[GetPageDescendantsResponseResult], list[GetPageDescendantsResponseResult]
]:
    """
    Fetch descendants from multiple roots (pages or folders) and process them.

    For each root, calls the appropriate get_descendants API based on type and:
    1. Skips already-fetched nodes (deduplication)
    2. Builds lineage for new nodes
    3. Creates Entity and adds to entity_pool
    4. Identifies boundary nodes (at max depth, may have children)

    :param client: Confluence API client
    :param roots: List of (id, type) tuples where type is "page" or "folder"
    :param entity_pool: Existing entities, will be mutated to add new ones
    :param depth: Max depth to fetch (API limit is 5)

    :returns: Tuple of (new_nodes, boundary_nodes)
        - new_nodes: All newly fetched nodes in this iteration
        - boundary_nodes: Nodes at max depth that may have unfetched children

    **Example**::

        Hierarchy (12 levels deep):
            homepage -> p1 -> p2 -> p3 -> f4 -> p5 -> p6 -> p7 -> f8 -> p9 -> p10 -> p11 -> p12
            (L0)       (L1)  (L2)  (L3)  (L4)  (L5)  (L6)  (L7)  (L8)  (L9)  (L10)  (L11)  (L12)

        Iteration 1: roots = [(homepage, "page")]
        - Fetch depth=5 from homepage
        - Gets: p1(L1), p2(L2), p3(L3), f4(L4), p5(L5)
        - Boundary nodes: [p5] (at depth=5, may have children)
        - new_nodes: 5, boundary_nodes: 1

        Iteration 2: roots = [(f4, "folder")]  # f4 is p5's parent
        - Fetch depth=5 from f4
        - Gets: p5(dup), p6(L6), p7(L7), f8(L8), p9(L9), p10(L10)
        - p5 skipped (already in entity_pool)
        - Boundary nodes: [p10] (at depth=5 relative to f4)
        - new_nodes: 5, boundary_nodes: 1

        Iteration 3: roots = [(f8, "folder")]  # f8 is p10's parent
        - Fetch depth=5 from f8
        - Gets: p9(dup), p10(dup), p11(L11), p12(L12)
        - Boundary nodes: [] (p12 at depth=4, no more children)
        - Done!
    """
    new_nodes: list[GetPageDescendantsResponseResult] = []
    boundary_nodes: list[GetPageDescendantsResponseResult] = []

    for root_id, root_type in roots:
        # Call appropriate API based on root type
        if root_type == DescendantTypeEnum.page.value:
            descendants = get_descendants_of_page(
                client=client,
                page_id=root_id,
                depth=depth,
            )
        elif root_type == DescendantTypeEnum.folder.value:  # folder
            descendants = get_descendants_of_folder(
                client=client,
                folder_id=root_id,
                depth=depth,
            )
        else:  # TODO handle other types if needed
            continue

        for node in descendants:
            # Skip if already fetched (deduplication)
            if node.id in entity_pool:
                continue

            new_nodes.append(node)

            # Build lineage and create Entity
            lineage = _build_lineage(node, entity_pool)
            entity = Entity(lineage=lineage)
            entity_pool[node.id] = entity

            # Boundary node: at max depth relative to current root.
            # These nodes might have children we haven't fetched yet.
            # We use the `depth` parameter (not a hardcoded constant) so the algorithm
            # automatically adapts if Confluence API increases the max depth limit.
            if node.depth == depth:
                boundary_nodes.append(node)

    return new_nodes, boundary_nodes


def _cluster_by_parents(
    boundary_nodes: list[GetPageDescendantsResponseResult],
    entity_pool: dict[str, "Entity"],
) -> list[tuple[int, str]]:
    """
    Cluster boundary nodes by their direct parents.

    This is the core optimization of Parent Clustering Algorithm.
    Instead of fetching from each boundary node individually (N API calls),
    we group them by their parents and fetch from those (M calls, M << N).

    :param boundary_nodes: Nodes at depth=5 that may have unfetched children
    :param entity_pool: Existing entities (used to look up parent types)

    :returns: List of unique (parent_id, parent_type) tuples for next iteration

    **Example**::

        Hierarchy with multiple branches at L5:
            homepage -> f1 -> p2 -> f3 -> p4 -> [p5a, p5b, p5c]  # 3 children under p4
                                        -> f4 -> [p5d, p5e]      # 2 children under f4
                                   -> p3 -> f4b -> [p5f]         # 1 child under f4b

        After iteration 1 (depth=5 from homepage):
        - boundary_nodes = [p5a, p5b, p5c, p5d, p5e, p5f]  # 6 nodes at L5
        - Their parents: p5a/p5b/p5c -> p4, p5d/p5e -> f4, p5f -> f4b

        _cluster_by_parents returns:
        - [(p4.id, "page"), (f4.id, "folder"), (f4b.id, "folder")]
        - Only 3 API calls instead of 6!

        With 100 boundary nodes sharing 3 parents:
        - Naive approach: 100 API calls
        - Parent clustering: 3 API calls (97% reduction)
    """
    parents: dict[int, str] = {}  # id -> type
    for node in boundary_nodes:
        parent_id = int(node.parentId)
        if parent_id not in parents:
            # Look up parent type in entity_pool
            parent_entity = entity_pool.get(node.parentId)
            parent_type = (
                parent_entity.node.type
                if parent_entity
                else DescendantTypeEnum.page.value
            )
            parents[parent_id] = parent_type
    return list(parents.items())


# ------------------------------------------------------------------------------
# Main crawler function
# ------------------------------------------------------------------------------
def crawl_descendants(
    client: Confluence,
    root_id: int,
    root_type: DescendantTypeEnum = DescendantTypeEnum.page,
    verbose: bool = False,
) -> list[Entity]:
    """
    Crawl all descendants of a root node using Parent Clustering Algorithm.

    Handles hierarchies deeper than 5 levels by clustering boundary nodes
    (nodes at depth=5) by their parents and fetching from parent level.
    This dramatically reduces API calls compared to naive per-node fetching.

    :param client: Authenticated Confluence API client
    :param root_id: ID of the root node (page or folder) to crawl from
    :param root_type: Type of the root node (page or folder)
    :param verbose: If True, print progress information

    :returns: List of Entity objects sorted by position_path (depth-first order).
        Each Entity contains the node and its lineage (path to root).

    **Algorithm**:

    1. Fetch descendants from root (depth=5) → get L1-L5
    2. Find boundary nodes (depth=5, meaning they might have children)
    3. Cluster boundary nodes by their direct parents (pages or folders)
    4. Fetch from each unique parent (depth=5)
    5. Deduplicate (skip nodes already fetched)
    6. Repeat until no more boundary nodes
    7. Sort all entities by position_path for depth-first ordering

    **Example**::

        from docpack_confluence.constants import DescendantTypeEnum

        # Crawl from a page (e.g., space homepage)
        entities = crawl_descendants(client, homepage_id, DescendantTypeEnum.page)

        # Crawl from a folder
        entities = crawl_descendants(client, folder_id, DescendantTypeEnum.folder)

        # Entities are sorted in depth-first order by position_path
        for entity in entities:
            print(entity.node.title)
            print(entity.title_path)    # ['root', 'parent', 'child']
            print(entity.position_path) # [0, 2, 1]

        # Get all page entities
        pages = [e for e in entities if e.node.type == "page"]
    """
    entity_pool: dict[str, Entity] = {}
    # (id, type) tuples - start with provided root
    current_roots: list[tuple[int, str]] = [(root_id, root_type.value)]
    iteration = 0

    while current_roots:
        iteration += 1

        if verbose:  # pragma: no cover
            msg = f"Iteration {iteration}: fetching from {len(current_roots)} root(s)"
            print(msg)  # for debug only

        # Fetch descendants and identify boundary nodes
        new_nodes, boundary_nodes = _fetch_iteration(
            client, current_roots, entity_pool, GET_PAGE_DESCENDANTS_MAX_DEPTH
        )

        if verbose:  # pragma: no cover
            msg = f"  - Found {len(new_nodes)} new nodes, {len(boundary_nodes)} at boundary"
            print(msg)  # for debug only

        if not boundary_nodes:
            break

        # Cluster boundary nodes by parents for next iteration
        current_roots = _cluster_by_parents(boundary_nodes, entity_pool)

        if verbose:  # pragma: no cover
            msg = (
                f"  - Clustering into {len(current_roots)} parent(s) for next iteration"
            )
            print(msg)  # for debug only

    if verbose:  # pragma: no cover
        msg = f"Completed: {len(entity_pool)} total nodes in {iteration} iteration(s)"
        print(msg)  # for debug only

    # Sort by position_path for depth-first ordering
    entities = list(entity_pool.values())
    entities.sort(key=lambda e: e.position_path)

    return entities


def serialize_entities(entities: list[Entity]) -> bytes:
    """
    Serialize a list of Entity objects to gzip-compressed JSON bytes.

    Uses a deduplicated structure where each node's raw_data is stored exactly
    once, and lineages reference nodes by ID.

    **Serialized format**::

        {
            "node_id_1": {
                "data": {raw_data},
                "lineage": ["node_id_1", "parent_id", "grandparent_id", ...]
            },
            "node_id_2": {
                "data": {raw_data},
                "lineage": ["node_id_2", "parent_id", ...]
            },
            ...
        }
    """
    data: dict[str, dict] = {}
    for entity in entities:
        node_id = entity.node.id
        data[node_id] = {
            "data": entity.node.raw_data,
            "lineage": [n.id for n in entity.lineage],
        }
    return gzip.compress(orjson.dumps(data))


def deserialize_entities(b: bytes) -> list[Entity]:
    """
    Deserialize gzip-compressed JSON bytes back to a list of Entity objects.

    Reconstructs Entity objects from the deduplicated format, reusing node
    instances across entities that share ancestors.
    """
    data = orjson.loads(gzip.decompress(b))

    # Build node objects once (reused across entities)
    node_cache: dict[str, GetPageDescendantsResponseResult] = {}
    for node_id, entry in data.items():
        node_cache[node_id] = GetPageDescendantsResponseResult(_raw_data=entry["data"])

    # Reconstruct entities
    entities = []
    for node_id, entry in data.items():
        lineage = [node_cache[lid] for lid in entry["lineage"]]
        entities.append(Entity(lineage=lineage))

    return entities


def crawl_descendants_with_cache(
    client: Confluence,
    root_id: int,
    root_type: DescendantTypeEnum,
    cache: CacheLike,
    cache_key: str | None = None,
    expire: int | None = 3600,
    force_refresh: bool = False,
    verbose: bool = False,
) -> list[Entity]:
    """
    Crawl all descendants of a root node with disk caching.

    Uses :func:`crawl_descendants` for fetching and caches the results
    using orjson for fast serialization.

    :param client: Authenticated Confluence API client
    :param root_id: ID of the root node (page or folder) to crawl from
    :param root_type: Type of the root node (page or folder)
    :param cache: Cache-like instance for storing results
    :param cache_key: Manual override for cache key (auto-generated if None)
    :param expire: Cache expiration time in seconds (None for no expiration)
    :param force_refresh: If True, bypass cache and fetch fresh data
    :param verbose: If True, print progress information

    :returns: List of Entity objects sorted by position_path (depth-first order).
        Each Entity contains the node and its lineage (path to root).

    **Example**::

        import diskcache
        from docpack_confluence.constants import DescendantTypeEnum

        cache = diskcache.Cache("/tmp/confluence_cache")
        entities = crawl_descendants_with_cache(
            client=client,
            root_id=homepage_id,
            root_type=DescendantTypeEnum.page,
            cache=cache,
            expire=3600,  # 1 hour
        )

        # Filter multiple times without re-fetching
        from docpack_confluence.shortcuts import filter_pages

        docs = filter_pages(entities, include=["...docs/**"])
        api_ref = filter_pages(entities, include=["...api/**"])
    """
    if cache_key is None:
        cache_key = f"crawl_descendants@{root_type.value}-{root_id}"

    def fetch():
        return crawl_descendants(
            client=client,
            root_id=root_id,
            root_type=root_type,
            verbose=verbose,
        )

    def store(entities: list[Entity]):
        cache.set(cache_key, serialize_entities(entities), expire=expire)

    if force_refresh:
        entities = fetch()
        store(entities)
        return entities

    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return deserialize_entities(cached_data)

    # Cache miss - fetch and cache
    entities = fetch()
    store(entities)
    return entities


def filter_entities(
    entities: list[Entity],
    include: list[str] | None = None,
    exclude: list[str] | None = None,
) -> list[Entity]:
    """
    Filter entities to get matching pages only.

    This is a pure filtering function with no I/O. Use this when you already
    have entities (e.g., from cache) and want to apply include/exclude filters.

    :param entities: List of Entity objects from crawl_descendants
    :param include: List of URL patterns to include. None or empty means include all.
        Supports wildcards: ``/*`` (descendants only), ``/**`` (self and descendants)
    :param exclude: List of URL patterns to exclude. None or empty means exclude nothing.
        Supports same wildcards as include.

    :returns: List of Entity objects (pages only) sorted by position_path (depth-first order).
        Each Entity has: ``node`` (the page), ``id_path``, ``title_path``, ``position_path``

    **Example**::

        from docpack_confluence.crawler import crawl_descendants
        from docpack_confluence.constants import DescendantTypeEnum

        # Get entities once (or from cache)
        entities = crawl_descendants(client, homepage_id, DescendantTypeEnum.page)

        # Filter multiple times with different patterns
        docs = filter_pages(entities, include=["...docs/**"])
        api_ref = filter_pages(entities, include=["...api/**"])

    **Filter priority**: exclude > include. If a page matches both, it is excluded.
    """
    # Create selector with include/exclude patterns
    selector = Selector(
        include=include or [],
        exclude=exclude or [],
    )

    # Filter: pages only + matches selector
    # entities are already sorted by position_path (depth-first order)
    result: list["Entity"] = []
    for entity in entities:
        # Skip folders, only include pages
        if entity.node.type != "page":
            continue

        # Check if page matches include/exclude patterns
        if selector.should_include(entity.id_path):
            result.append(entity)

    return result


def select_entities(
    client: Confluence,
    root_id: int,
    root_type: DescendantTypeEnum,
    include: list[str] | None = None,
    exclude: list[str] | None = None,
    verbose: bool = False,
) -> list[Entity]:
    """
    Select pages from a Confluence hierarchy based on include/exclude patterns.

    This is a convenience API that combines crawling and filtering. For multiple
    filter operations on the same hierarchy, use :func:`filter_pages` with cached entities.

    :param client: Authenticated Confluence API client
    :param root_id: ID of the root node (page or folder) to crawl from
    :param root_type: Type of the root node (page or folder)
    :param include: List of URL patterns to include. None or empty means include all.
        Supports wildcards: ``/*`` (descendants only), ``/**`` (self and descendants)
    :param exclude: List of URL patterns to exclude. None or empty means exclude nothing.
        Supports same wildcards as include.
    :param verbose: If True, print progress information

    :returns: List of Entity objects (pages only) sorted by position_path (depth-first order).
        Each Entity has: ``node`` (the page), ``id_path``, ``title_path``, ``position_path``

    **Example**::

        from docpack_confluence.constants import DescendantTypeEnum

        # Include all pages under a specific page, exclude a subtree
        pages = select_pages(
            client=client,
            root_id=homepage_id,
            root_type=DescendantTypeEnum.page,
            include=[
                "https://example.atlassian.net/wiki/spaces/DEMO/pages/111/Topic1/**",
                "https://example.atlassian.net/wiki/spaces/DEMO/pages/222/Topic2/**",
            ],
            exclude=[
                "https://example.atlassian.net/wiki/spaces/DEMO/pages/333/Draft/*",
            ],
        )

        # Get page IDs for fetching content
        page_ids = [entity.node.id for entity in pages]

    **Filter priority**: exclude > include. If a page matches both, it is excluded.

    .. seealso::
        :func:`filter_pages` for filtering pre-fetched or cached entities.
    """
    # Crawl all descendants (handles depth > 5)
    if verbose:
        print("Crawling hierarchy...")
    entities = crawl_descendants(
        client=client,
        root_id=root_id,
        root_type=root_type,
        verbose=verbose,
    )

    # Filter using the pure function
    result = filter_entities(entities, include, exclude)

    if verbose:
        print(f"Selected {len(result)} pages out of {len(entities)} entities")

    return result
