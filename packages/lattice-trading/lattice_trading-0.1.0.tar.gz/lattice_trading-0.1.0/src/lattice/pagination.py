
from __future__ import annotations

from collections.abc import AsyncIterator, Callable, Iterable, Iterator
from typing import Any, Optional, TypeVar

T = TypeVar("T")


def paginate_offset(
    fetch_page: Callable[[int, int], tuple[Iterable[T], int, int, Optional[int]]],
    *,
    limit: int = 50,
    offset: int = 0,
    max_pages: Optional[int] = None,
) -> Iterator[T]:
    page_count = 0
    while True:
        items, page_limit, page_offset, total = fetch_page(limit, offset)
        items_list = list(items)
        for item in items_list:
            yield item
        next_offset = page_offset + page_limit
        if total is not None and next_offset >= total:
            break
        if len(items_list) < page_limit:
            break
        offset = next_offset
        page_count += 1
        if max_pages is not None and page_count >= max_pages:
            break


async def paginate_cursor(
    fetch_page: Callable[[Optional[str]], Any],
    *,
    cursor: Optional[str] = None,
    max_pages: Optional[int] = None,
) -> AsyncIterator[T]:
    page_count = 0
    next_cursor = cursor
    while True:
        page = await fetch_page(next_cursor)
        items = page.get("items", [])
        for item in items:
            yield item
        has_more = page.get("hasMore")
        next_cursor = page.get("nextCursor")
        if not has_more or not next_cursor:
            break
        page_count += 1
        if max_pages is not None and page_count >= max_pages:
            break
