# -*- coding: utf-8 -*-

"""
Shortcut wrappers for sanhe-confluence-sdk API with simplified parameters.
"""

import typing as T
import time
import gzip

import httpx
import orjson

# fmt: off
from sanhe_confluence_sdk.api import Confluence
from sanhe_confluence_sdk.api import paginate
from sanhe_confluence_sdk.methods.model import T_RESPONSE
from sanhe_confluence_sdk.methods.space.get_space import GetSpaceRequest
from sanhe_confluence_sdk.methods.space.get_space import GetSpaceRequestPathParams
from sanhe_confluence_sdk.methods.space.get_space import GetSpaceResponse
from sanhe_confluence_sdk.methods.space.get_spaces import GetSpacesRequest
from sanhe_confluence_sdk.methods.space.get_spaces import GetSpacesRequestQueryParams
from sanhe_confluence_sdk.methods.space.get_spaces import GetSpacesResponseResult
from sanhe_confluence_sdk.methods.page.get_pages import GetPagesRequest
from sanhe_confluence_sdk.methods.page.get_pages import GetPagesRequestQueryParams
from sanhe_confluence_sdk.methods.page.get_pages import GetPagesResponseResult
from sanhe_confluence_sdk.methods.page.get_pages_in_space import GetPagesInSpaceRequest
from sanhe_confluence_sdk.methods.page.get_pages_in_space import GetPagesInSpaceRequestPathParams
from sanhe_confluence_sdk.methods.page.get_pages_in_space import GetPagesInSpaceRequestQueryParams
from sanhe_confluence_sdk.methods.page.get_pages_in_space import GetPagesInSpaceResponse
from sanhe_confluence_sdk.methods.page.get_pages_in_space import GetPagesInSpaceResponseResult
from sanhe_confluence_sdk.methods.page.delete_page import DeletePageRequest
from sanhe_confluence_sdk.methods.page.delete_page import DeletePageRequestPathParams
from sanhe_confluence_sdk.methods.page.delete_page import DeletePageRequestQueryParams
from sanhe_confluence_sdk.methods.page.create_page import CreatePageRequest
from sanhe_confluence_sdk.methods.page.create_page import CreatePageRequestBodyParams
from sanhe_confluence_sdk.methods.page.create_page import CreatePageResponse
from sanhe_confluence_sdk.methods.descendant.get_page_descendants import GetPageDescendantsRequest
from sanhe_confluence_sdk.methods.descendant.get_page_descendants import GetPageDescendantsRequestPathParams
from sanhe_confluence_sdk.methods.descendant.get_page_descendants import GetPageDescendantsRequestQueryParams
from sanhe_confluence_sdk.methods.descendant.get_page_descendants import GetPageDescendantsResponse
from sanhe_confluence_sdk.methods.descendant.get_page_descendants import GetPageDescendantsResponseResult
from sanhe_confluence_sdk.methods.descendant.get_folder_descendants import GetFolderDescendantsRequest
from sanhe_confluence_sdk.methods.descendant.get_folder_descendants import GetFolderDescendantsRequestPathParams
from sanhe_confluence_sdk.methods.descendant.get_folder_descendants import GetFolderDescendantsRequestQueryParams
from sanhe_confluence_sdk.methods.descendant.get_folder_descendants import GetFolderDescendantsResponse
from sanhe_confluence_sdk.methods.descendant.get_folder_descendants import GetFolderDescendantsResponseResult
from sanhe_confluence_sdk.methods.folder.delete_folder import DeleteFolderRequest
from sanhe_confluence_sdk.methods.folder.delete_folder import DeleteFolderRequestPathParams
from sanhe_confluence_sdk.methods.folder.create_folder import CreateFolderRequest
from sanhe_confluence_sdk.methods.folder.create_folder import CreateFolderRequestBodyParams
from sanhe_confluence_sdk.methods.folder.create_folder import CreateFolderResponse
# fmt: on

from .vendor.more_itertools import batched

from .constants import GET_PAGE_DESCENDANTS_MAX_DEPTH
from .type_hint import HasRawData, CacheLike
from .selector import Selector

if T.TYPE_CHECKING:  # pragma: no cover
    from .crawler import Entity


def get_space_by_id(
    client: Confluence,
    space_id: int,
) -> GetSpaceResponse:
    """
    Fetches a Confluence space by its ID.

    :param client: Authenticated Confluence API client
    :param space_id: ID of the Confluence space to fetch
    """
    path_params = GetSpaceRequestPathParams(id=space_id)
    request = GetSpaceRequest(path_params=path_params)
    response = request.sync(client)
    return response


def get_space_by_key(
    client: Confluence,
    space_key: str,
) -> GetSpacesResponseResult:
    """
    Fetches a Confluence space by its key.

    :param client: Authenticated Confluence API client
    :param space_key: Key of the Confluence space to fetch
    """
    query_params = GetSpacesRequestQueryParams(keys=[space_key])
    request = GetSpacesRequest(query_params=query_params)
    response = request.sync(client)
    space = response.results[0]
    return space


def get_pages_by_ids(
    client: Confluence,
    ids: list[int],
    body_format: str = "atlas_doc_format",
) -> list[GetPagesResponseResult]:
    """
    Fetches multiple Confluence pages by their IDs in batches.

    :param client: Authenticated Confluence API client
    :param ids: List of Confluence page IDs to fetch
    :param body_format: Format of the page body content

    :returns: List of page results
    """
    results = list()
    for id_batch in batched(ids, n=250):
        query_params = GetPagesRequestQueryParams(
            id=id_batch,
            body_format=body_format,
        )
        request = GetPagesRequest(
            query_params=query_params,
        )
        response = request.sync(client)
        results.extend(response.results)
    return results


def get_pages_in_space(
    client: Confluence,
    space_id: int,
    limit: int = 9999,
) -> T.Iterator[GetPagesInSpaceResponseResult]:
    """
    Crawls and retrieves all pages from a Confluence space using pagination.

    :param client: Authenticated Confluence API client
    :param space_id: ID of the Confluence space to crawl
    :param limit: Number of pages to fetch

    :returns: Iterator of page results from the space
    """
    path_params = GetPagesInSpaceRequestPathParams(
        id=space_id,
    )
    query_params = GetPagesInSpaceRequestQueryParams(
        body_format="atlas_doc_format",
    )
    request = GetPagesInSpaceRequest(
        path_params=path_params,
        query_params=query_params,
    )
    paginator = paginate(
        client=client,
        request=request,
        response_type=GetPagesInSpaceResponse,
        page_size=250,
        max_items=limit,
    )
    for response in paginator:
        for result in response.results:
            yield result


def get_descendants_of_page(
    client: Confluence,
    page_id: int,
    limit: int = 9999,
    depth: int = GET_PAGE_DESCENDANTS_MAX_DEPTH,
) -> T.Iterator[GetPageDescendantsResponseResult]:
    """
    Crawls and retrieves all descendant pages of a given Confluence page using pagination.

    :param client: Authenticated Confluence API client
    :param page_id: ID of the Confluence page whose descendants to fetch
    :param limit: Number of descendant pages to fetch
    """
    path_params = GetPageDescendantsRequestPathParams(
        id=page_id,
    )
    query_params = GetPageDescendantsRequestQueryParams(
        depth=depth,
        limit=250,
    )
    request = GetPageDescendantsRequest(
        path_params=path_params,
        query_params=query_params,
    )
    paginator = paginate(
        client=client,
        request=request,
        response_type=GetPageDescendantsResponse,
        page_size=250,
        max_items=limit,
    )
    for response in paginator:
        for result in response.results:
            yield result


def get_descendants_of_folder(
    client: Confluence,
    folder_id: int,
    limit: int = 9999,
    depth: int = GET_PAGE_DESCENDANTS_MAX_DEPTH,
) -> T.Iterator[GetFolderDescendantsResponseResult]:
    """
    Crawls and retrieves all descendant entities of a given Confluence folder using pagination.

    :param client: Authenticated Confluence API client
    :param folder_id: ID of the Confluence folder whose descendants to fetch
    :param limit: Maximum number of descendant entities to fetch
    :param depth: Maximum depth to traverse (API limit is 5)

    :returns: Iterator of descendant results (pages and folders)
    """
    path_params = GetFolderDescendantsRequestPathParams(
        id=folder_id,
    )
    query_params = GetFolderDescendantsRequestQueryParams(
        depth=depth,
        limit=250,
    )
    request = GetFolderDescendantsRequest(
        path_params=path_params,
        query_params=query_params,
    )
    paginator = paginate(
        client=client,
        request=request,
        response_type=GetFolderDescendantsResponse,
        page_size=250,
        max_items=limit,
    )
    for response in paginator:
        for result in response.results:
            yield result


def serialize_many(objects: list[HasRawData]) -> bytes:
    """
    Serialize a list of objects with raw_data to gzip-compressed JSON bytes.
    """
    return gzip.compress(orjson.dumps([obj.raw_data for obj in objects]))


def deserialize_many(b: bytes, klass: T.Type[T_RESPONSE]) -> list[T_RESPONSE]:
    """
    Deserialize gzip-compressed JSON bytes back to a list of objects.
    """
    return [klass(_raw_data=data) for data in orjson.loads(gzip.decompress(b))]


def get_pages_in_space_with_cache(
    client: Confluence,
    space_id: int,
    cache: CacheLike,
    cache_key: str | None = None,
    expire: int | None = 3600,
    force_refresh: bool = False,
    limit: int = 9999,
) -> list[GetPagesInSpaceResponseResult]:
    """
    Retrieves all pages from a Confluence space with disk caching.

    Uses orjson for fast serialization of raw API response data.

    :param client: Authenticated Confluence API client
    :param space_id: ID of the Confluence space to crawl
    :param cache: cache like instance for storing results
    :param cache_key: Manual override for cache key (auto-generated if None)
    :param expire: Cache expiration time in seconds (None for no expiration)
    :param force_refresh: If True, bypass cache and fetch fresh data
    :param limit: Maximum number of pages to fetch

    :returns: List of page results from the space
    """
    if cache_key is None:
        cache_key = f"get_pages_in_space@space-{space_id}"

    def fetch():
        return list(
            get_pages_in_space(
                client=client,
                space_id=space_id,
                limit=limit,
            )
        )

    def store(pages):
        cache.set(cache_key, serialize_many(pages), expire=expire)

    if force_refresh:
        pages = fetch()
        store(pages)
        return pages

    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return deserialize_many(cached_data, GetPagesInSpaceResponseResult)

    # Cache miss - fetch and cache
    pages = fetch()
    store(pages)
    return pages


def get_descendants_of_page_with_cache(
    client: Confluence,
    page_id: int,
    cache: CacheLike,
    cache_key: str | None = None,
    expire: int | None = 3600,
    force_refresh: bool = False,
    limit: int = 9999,
) -> list[GetPageDescendantsResponseResult]:
    """
    Retrieves all descendant pages of a Confluence page with disk caching.

    Uses orjson for fast serialization of raw API response data.

    :param client: Authenticated Confluence API client
    :param page_id: ID of the Confluence page whose descendants to fetch
    :param cache: cache like instance for storing results
    :param cache_key: Manual override for cache key (auto-generated if None)
    :param expire: Cache expiration time in seconds (None for no expiration)
    :param force_refresh: If True, bypass cache and fetch fresh data
    :param limit: Maximum number of descendant pages to fetch

    :returns: List of descendant page results
    """
    if cache_key is None:
        cache_key = f"get_descendants_of_page@{page_id}"

    def fetch():
        return list(
            get_descendants_of_page(
                client=client,
                page_id=page_id,
                limit=limit,
            )
        )

    def store(pages):
        cache.set(cache_key, serialize_many(pages), expire=expire)

    if force_refresh:
        pages = fetch()
        store(pages)
        return pages

    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return deserialize_many(cached_data, GetPageDescendantsResponseResult)

    # Cache miss - fetch and cache
    pages = fetch()
    store(pages)
    return pages


def get_descendants_of_folder_with_cache(
    client: Confluence,
    folder_id: int,
    cache: CacheLike,
    cache_key: str | None = None,
    expire: int | None = 3600,
    force_refresh: bool = False,
    limit: int = 9999,
) -> list[GetFolderDescendantsResponseResult]:
    """
    Retrieves all descendant entities of a Confluence folder with disk caching.

    Uses orjson for fast serialization of raw API response data.

    :param client: Authenticated Confluence API client
    :param folder_id: ID of the Confluence folder whose descendants to fetch
    :param cache: cache like instance for storing results
    :param cache_key: Manual override for cache key (auto-generated if None)
    :param expire: Cache expiration time in seconds (None for no expiration)
    :param force_refresh: If True, bypass cache and fetch fresh data
    :param limit: Maximum number of descendant entities to fetch

    :returns: List of descendant results (pages and folders)
    """
    if cache_key is None:
        cache_key = f"get_descendants_of_folder@{folder_id}"

    def fetch():
        return list(
            get_descendants_of_folder(
                client=client,
                folder_id=folder_id,
                limit=limit,
            )
        )

    def store(descendants):
        cache.set(cache_key, serialize_many(descendants), expire=expire)

    if force_refresh:
        descendants = fetch()
        store(descendants)
        return descendants

    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return deserialize_many(cached_data, GetFolderDescendantsResponseResult)

    # Cache miss - fetch and cache
    descendants = fetch()
    store(descendants)
    return descendants


def delete_pages_and_folders_in_space(
    client: Confluence,
    space_id: int,
    purge: bool = False,
    verbose: bool = True,
) -> None:
    """
    Deletes all pages and folders in a Confluence space.

    Uses :func:`~docpack_confluence.crawler.crawl_descendants` to fetch
    the complete hierarchy (handles depth > 5), then deletes from deepest
    level first to avoid "parent folder can't be deleted" errors.

    :param client: Authenticated Confluence API client
    :param space_id: ID of the Confluence space whose pages to delete
    :param purge: If True, permanently delete (skip trash)
    :param verbose: If True, print progress information

    **Algorithm**::

        Given hierarchy with max depth = 3:
            L1: [p1, f1]
            L2: [p2, f2, p3]
            L3: [p4, f3]

        Delete order:
        1. Delete all L3 entities: p4, f3
        2. Delete all L2 entities: p2, f2, p3
        3. Delete all L1 entities: p1, f1

        This ensures children are always deleted before parents.
    """
    from .crawler import crawl_descendants
    from .constants import DescendantTypeEnum

    space = get_space_by_id(client=client, space_id=space_id)
    homepage_id = int(space.homepageId)

    # Crawl complete hierarchy (handles depth > 5)
    if verbose:
        print("Crawling space hierarchy...")
    entities = crawl_descendants(
        client=client,
        root_id=homepage_id,
        root_type=DescendantTypeEnum.page,
        verbose=verbose,
    )

    if not entities:
        if verbose:
            print("No entities to delete.")
        return

    # Group entities by depth (len(lineage) = depth from root)
    # lineage = [self, parent, grandparent, ...], so len = depth
    from collections import defaultdict

    by_depth: dict[int, list] = defaultdict(list)
    for entity in entities:
        depth = len(entity.lineage)
        by_depth[depth].append(entity)

    # Get all depths sorted descending (deepest first)
    depths = sorted(by_depth.keys(), reverse=True)
    max_depth = depths[0] if depths else 0

    if verbose:
        print(f"Found {len(entities)} entities, max depth = {max_depth}")
        print(f"Deleting from depth {max_depth} down to 1...")

    deleted_count = 0
    for depth in depths:
        entities_at_depth = by_depth[depth]
        if verbose:
            print(f"  Depth {depth}: {len(entities_at_depth)} entities")

        for entity in entities_at_depth:
            node = entity.node
            try:
                if node.type == "page":
                    if verbose:
                        print(f"    Deleting page: {node.title} (id={node.id})")
                    path_params = DeletePageRequestPathParams(id=int(node.id))
                    query_params = DeletePageRequestQueryParams(purge=purge)
                    request = DeletePageRequest(
                        path_params=path_params,
                        query_params=query_params,
                    )
                    request.sync(client)
                elif node.type == "folder":
                    if verbose:
                        print(f"    Deleting folder: {node.title} (id={node.id})")
                    path_params = DeleteFolderRequestPathParams(id=int(node.id))
                    request = DeleteFolderRequest(path_params=path_params)
                    request.sync(client)
                else:
                    if verbose:
                        print(f"    Skipping unknown type: {node.type} ({node.title})")
                    continue
                deleted_count += 1
            except httpx.HTTPStatusError as e:
                status_code = e.response.status_code
                if status_code == 404:
                    # Already deleted (cascade from parent deletion)
                    if verbose:
                        print(f"      -> Already deleted (404)")
                else:
                    print(f"      -> ERROR {status_code}: {e.response.text}")
                    raise

    if verbose:
        print(f"Deleted {deleted_count} entities.")


# Type alias for requests that have a sync method
T_REQUEST = T.TypeVar("T_REQUEST")
T_RESPONSE_TYPE = T.TypeVar("T_RESPONSE_TYPE")


def execute_with_retry(
    request: T_REQUEST,
    client: Confluence,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    retry_on: set[int] | None = None,
    verbose: bool = True,
) -> T_RESPONSE_TYPE:
    """
    Execute a request with retry logic for specific HTTP status codes.

    Only retries when the response status code is in ``retry_on`` set.
    Other errors are raised immediately without retry.

    :param request: Request object with a `sync(client)` method
    :param client: Confluence API client
    :param max_retries: Maximum number of retry attempts
    :param initial_delay: Initial delay in seconds before first retry
    :param retry_on: Set of HTTP status codes that should trigger a retry.
        Default is {404} (parent not found, common timing issue).
    :param verbose: If True, print retry information

    :returns: Response from the successful request

    :raises httpx.HTTPStatusError: If all retries fail or error is not retryable

    **Example**::

        request = CreatePageRequest(body_params=body_params)
        response = execute_with_retry(request, client, retry_on={404, 503})
    """
    if retry_on is None:
        retry_on = {404}

    delay = initial_delay
    last_error: httpx.HTTPStatusError | None = None

    for attempt in range(max_retries):
        try:
            return request.sync(client)
        except httpx.HTTPStatusError as e:
            last_error = e
            status_code = e.response.status_code

            # Only retry on specific status codes
            if status_code not in retry_on:
                if verbose:
                    print(f"  ERROR: {status_code} (not retryable)")
                    print(f"  Response: {e.response.text}")
                raise

            # Check if we have retries left
            if attempt < max_retries - 1:
                if verbose:
                    print(
                        f"  RETRY ({attempt + 1}/{max_retries}): {status_code}, waiting {delay}s..."
                    )
                time.sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                # Final attempt failed
                if verbose:
                    print(f"  FAILED after {max_retries} attempts: {status_code}")
                    print(f"  Response: {e.response.text}")
                raise

    # Should never reach here, but satisfy type checker
    raise last_error  # type: ignore


def create_pages_and_folders(
    client: Confluence,
    space_id: int,
    hierarchy_specs: list[str],
    max_retries: int = 3,
    initial_delay: float = 1.0,
    retry_on: set[int] | None = None,
) -> dict[str, str]:
    """
    Create pages and folders in a Confluence space based on spec strings.

    Spec format:
    - "p1" → create page with title "p1" under homepage
    - "f1" → create folder with title "f1" under homepage
    - "p2/p3" → create page with title "p3" under "p2"
    - "p2/f2" → create folder with title "f2" under "p2"

    Naming convention:
    - Starts with "p" → page
    - Starts with "f" → folder

    :param client: Authenticated Confluence API client
    :param space_id: ID of the Confluence space
    :param hierarchy_specs: List of spec strings (must be sorted by dependency order)
    :param max_retries: Maximum number of retry attempts for failed requests
    :param initial_delay: Initial delay in seconds before first retry
    :param retry_on: Set of HTTP status codes that should trigger a retry.
        Default is {404} (parent not found).

    :returns: Dictionary mapping title to created entity ID
    """
    if retry_on is None:
        retry_on = {404}

    space = get_space_by_id(client=client, space_id=space_id)
    homepage_id = space.homepageId

    # Maps title to created entity's ID
    # e.g., "p1" -> "123456", "p3" -> "789012"
    title_to_id_map: dict[str, str] = {}

    for spec in hierarchy_specs:
        # Parse spec: "f3/f4/p5" -> parts=["f3", "f4", "p5"]
        # - title = parts[-1] = "p5"
        # - parent = parts[-2] = "f4" (or homepage if only one part)
        parts = spec.split("/")
        title = parts[-1]
        depth = len(parts)

        if len(parts) == 1:
            # Root level: parent is homepage
            parent_id = homepage_id
        else:
            # Nested: parent is the second-to-last element
            parent_title = parts[-2]
            parent_id = title_to_id_map[parent_title]

        # Determine if page or folder based on prefix
        is_page = title.startswith("p")

        if is_page:
            print(f"Creating {title} (page, L{depth}) ...")
            body_params = CreatePageRequestBodyParams(
                space_id=str(space_id),
                parent_id=str(parent_id),
                title=title,
                body={
                    "representation": "storage",
                    "value": "",  # Empty content
                },
            )
            request = CreatePageRequest(body_params=body_params)
        else:
            print(f"Creating {title} (folder, L{depth}) ...")
            body_params = CreateFolderRequestBodyParams(
                space_id=str(space_id),
                parent_id=str(parent_id),
                title=title,
            )
            request = CreateFolderRequest(body_params=body_params)

        response = execute_with_retry(
            request=request,
            client=client,
            max_retries=max_retries,
            initial_delay=initial_delay,
            retry_on=retry_on,
            verbose=True,
        )
        created_id = response.id
        print(f"  Created ID: {created_id}")

        # Store title as key for nested lookups
        title_to_id_map[title] = created_id

    return title_to_id_map
