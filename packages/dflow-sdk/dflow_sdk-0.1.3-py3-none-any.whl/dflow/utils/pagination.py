"""Pagination utilities for DFlow API responses."""

from collections.abc import AsyncGenerator, Callable, Generator
from typing import Any, TypeVar

T = TypeVar("T")
TResponse = TypeVar("TResponse")


def paginate(
    fetch_page: Callable[[dict[str, Any]], TResponse],
    get_items: Callable[[TResponse], list[T]],
    get_cursor: Callable[[TResponse], str | None] | None = None,
    max_items: int | None = None,
    page_size: int | None = None,
) -> Generator[T, None, None]:
    """Create a generator that automatically paginates through all results.

    Example:
        >>> from dflow.utils import paginate
        >>>
        >>> # Iterate through all markets
        >>> for market in paginate(
        ...     lambda params: dflow.markets.get_markets(**params),
        ...     get_items=lambda r: r.markets,
        ... ):
        ...     print(market.ticker, market.yes_price)
        >>>
        >>> # With a limit
        >>> for event in paginate(
        ...     lambda params: dflow.events.get_events(**params),
        ...     get_items=lambda r: r.events,
        ...     max_items=100,
        ... ):
        ...     print(event.title)

    Args:
        fetch_page: Function that fetches a page given pagination params
        get_items: Function to extract items array from response
        get_cursor: Function to extract cursor from response (default: r.cursor)
        max_items: Maximum number of items to fetch in total (default: unlimited)
        page_size: Number of items per page (default: API default)

    Yields:
        Individual items from each page
    """
    if get_cursor is None:

        def get_cursor(r: Any) -> str | None:
            return getattr(r, "cursor", None)

    cursor: str | None = None
    items_yielded = 0

    while True:
        params: dict[str, Any] = {}
        if cursor:
            params["cursor"] = cursor
        if page_size:
            params["limit"] = page_size

        response = fetch_page(params)
        items = get_items(response)

        for item in items:
            yield item
            items_yielded += 1

            if max_items is not None and items_yielded >= max_items:
                return

        cursor = get_cursor(response)
        if not cursor:
            break


def collect_all(
    fetch_page: Callable[[dict[str, Any]], TResponse],
    get_items: Callable[[TResponse], list[T]],
    get_cursor: Callable[[TResponse], str | None] | None = None,
    max_items: int | None = None,
    page_size: int | None = None,
) -> list[T]:
    """Collect all items from a paginated endpoint into a list.

    Example:
        >>> from dflow.utils import collect_all
        >>>
        >>> # Get all markets as a list
        >>> all_markets = collect_all(
        ...     lambda params: dflow.markets.get_markets(**params),
        ...     get_items=lambda r: r.markets,
        ... )
        >>> print(f"Found {len(all_markets)} markets")

    Args:
        fetch_page: Function that fetches a page given pagination params
        get_items: Function to extract items array from response
        get_cursor: Function to extract cursor from response
        max_items: Maximum number of items to fetch in total
        page_size: Number of items per page

    Returns:
        List of all items
    """
    return list(
        paginate(
            fetch_page=fetch_page,
            get_items=get_items,
            get_cursor=get_cursor,
            max_items=max_items,
            page_size=page_size,
        )
    )


def count_all(
    fetch_page: Callable[[dict[str, Any]], TResponse],
    get_items: Callable[[TResponse], list[T]],
    get_cursor: Callable[[TResponse], str | None] | None = None,
) -> int:
    """Count total items from a paginated endpoint without storing them.

    Example:
        >>> from dflow.utils import count_all
        >>>
        >>> total = count_all(
        ...     lambda params: dflow.markets.get_markets(**params),
        ...     get_items=lambda r: r.markets,
        ... )
        >>> print(f"Total markets: {total}")

    Args:
        fetch_page: Function that fetches a page given pagination params
        get_items: Function to extract items array from response
        get_cursor: Function to extract cursor from response

    Returns:
        Total count of items
    """
    count = 0
    for _ in paginate(
        fetch_page=fetch_page,
        get_items=get_items,
        get_cursor=get_cursor,
    ):
        count += 1
    return count


def find_first(
    fetch_page: Callable[[dict[str, Any]], TResponse],
    get_items: Callable[[TResponse], list[T]],
    predicate: Callable[[T], bool],
    get_cursor: Callable[[TResponse], str | None] | None = None,
) -> T | None:
    """Find the first item matching a predicate from a paginated endpoint.

    Example:
        >>> from dflow.utils import find_first
        >>>
        >>> # Find a specific market
        >>> market = find_first(
        ...     lambda params: dflow.markets.get_markets(**params),
        ...     get_items=lambda r: r.markets,
        ...     predicate=lambda m: "Bitcoin" in m.title,
        ... )
        >>> if market:
        ...     print(f"Found: {market.ticker}")

    Args:
        fetch_page: Function that fetches a page given pagination params
        get_items: Function to extract items array from response
        predicate: Function to test each item
        get_cursor: Function to extract cursor from response

    Returns:
        The first matching item, or None if not found
    """
    for item in paginate(
        fetch_page=fetch_page,
        get_items=get_items,
        get_cursor=get_cursor,
    ):
        if predicate(item):
            return item
    return None


async def paginate_async(
    fetch_page: Callable[[dict[str, Any]], Any],
    get_items: Callable[[TResponse], list[T]],
    get_cursor: Callable[[TResponse], str | None] | None = None,
    max_items: int | None = None,
    page_size: int | None = None,
) -> AsyncGenerator[T, None]:
    """Async version of paginate.

    Example:
        >>> from dflow.utils import paginate_async
        >>>
        >>> async for market in paginate_async(
        ...     lambda params: async_client.markets.get_markets(**params),
        ...     get_items=lambda r: r.markets,
        ... ):
        ...     print(market.ticker)

    Args:
        fetch_page: Async function that fetches a page given pagination params
        get_items: Function to extract items array from response
        get_cursor: Function to extract cursor from response
        max_items: Maximum number of items to fetch in total
        page_size: Number of items per page

    Yields:
        Individual items from each page
    """
    if get_cursor is None:

        def get_cursor(r: Any) -> str | None:
            return getattr(r, "cursor", None)

    cursor: str | None = None
    items_yielded = 0

    while True:
        params: dict[str, Any] = {}
        if cursor:
            params["cursor"] = cursor
        if page_size:
            params["limit"] = page_size

        response = await fetch_page(params)
        items = get_items(response)

        for item in items:
            yield item
            items_yielded += 1

            if max_items is not None and items_yielded >= max_items:
                return

        cursor = get_cursor(response)
        if not cursor:
            break
