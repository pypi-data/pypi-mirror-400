from __future__ import annotations

from typing import List, Optional

from .client import DuckDuckGoResult, DuckDuckGoSearch

_default_client: Optional[DuckDuckGoSearch] = None


async def top_n_result(query: str, n: int = 5) -> List[DuckDuckGoResult]:
    """
    Convenience async function.

    Usage:
        from duckduckgo_async_search import top_n_result
        items = await top_n_result("Capital of Bangladesh", n=5)
    """
    global _default_client
    if _default_client is None:
        _default_client = DuckDuckGoSearch()
    return await _default_client.top_n_result(query, n=n)
