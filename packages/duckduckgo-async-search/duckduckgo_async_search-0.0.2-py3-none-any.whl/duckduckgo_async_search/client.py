from __future__ import annotations

import asyncio
import logging
import random
import time
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)

try:
    # Unofficial SERP wrapper (can rate-limit depending on IP/network)
    from duckduckgo_search import DDGS  # type: ignore
except Exception:  # pragma: no cover
    DDGS = None  # fallback still works

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


@dataclass(frozen=True)
class DuckDuckGoResult:
    title: str
    url: str
    snippet: str = ""
    source: str = ""  # e.g., "duckduckgo_search:lite" or "instant_answer_api"

    def to_dict(self) -> Dict[str, str]:
        d = asdict(self)
        return {
            "title": d.get("title", ""),
            "url": d.get("url", ""),
            "snippet": d.get("snippet", ""),
            "source": d.get("source", ""),
        }


class DuckDuckGoSearch:
    """Async DuckDuckGo search helper.

    Strategy:
      1) Try duckduckgo_search (unofficial SERP wrapper) if installed.
      2) Fallback to DuckDuckGo Instant Answer API JSON (more reliable, but not full SERP).
    """

    def __init__(
        self,
        *,
        user_agent: str = DEFAULT_USER_AGENT,
        request_timeout_s: float = 20.0,
        ddg_backends: Optional[List[str]] = None,
        ddg_pause_s: float = 1.0,
        ddg_max_attempts: int = 3,
        instant_answer_max_bytes: int = 2_000_000,
        debug: bool = False,
    ) -> None:
        self.user_agent = user_agent
        self.request_timeout_s = request_timeout_s
        self.ddg_backends = ddg_backends or ["lite", "html", "auto"]
        self.ddg_pause_s = ddg_pause_s
        self.ddg_max_attempts = max(1, int(ddg_max_attempts))
        self.instant_answer_max_bytes = instant_answer_max_bytes
        self.debug = debug

    # -----------------------------
    # Public async API
    # -----------------------------
    async def top_n_result(self, query: str, n: int = 5) -> List[DuckDuckGoResult]:
        """Return the top N result items (title, url, snippet, source)."""
        query = (query or "").strip()
        if not query:
            return []

        n = max(1, int(n))

        # 1) Unofficial SERP wrapper (best when it works)
        if DDGS is not None:
            try:
                return await asyncio.to_thread(self._search_via_duckduckgo_search_sync, query, n)
            except Exception as e:
                if self.debug:
                    logger.exception("duckduckgo_search failed; falling back. Error: %s", e)

        # 2) Instant Answer API (more reliable)
        return await self._search_via_instant_answer_api(query, n)

    # -----------------------------
    # Internal helpers
    # -----------------------------
    @staticmethod
    def _normalize_duckduckgo_search_rows(rows: List[Dict[str, Any]], source: str) -> List[DuckDuckGoResult]:
        out: List[DuckDuckGoResult] = []
        for r in rows:
            title = (r.get("title") or "").strip()
            url = (r.get("url") or r.get("href") or "").strip()
            snippet = (r.get("snippet") or r.get("body") or "").strip()
            if title and url:
                out.append(DuckDuckGoResult(title=title, url=url, snippet=snippet, source=source))
        return out

    def _sleep_with_backoff(self, attempt: int) -> None:
        # Exponential backoff with jitter
        base = self.ddg_pause_s * (2 ** max(0, attempt - 1))
        jitter = random.uniform(0, self.ddg_pause_s)
        time.sleep(base + jitter)

    def _search_via_duckduckgo_search_sync(self, query: str, max_results: int) -> List[DuckDuckGoResult]:
        if DDGS is None:
            raise RuntimeError("duckduckgo_search is not available.")

        last_err: Optional[Exception] = None

        for attempt in range(1, self.ddg_max_attempts + 1):
            for backend in self.ddg_backends:
                try:
                    raw: List[Dict[str, Any]] = []
                    with DDGS(headers={"User-Agent": self.user_agent}) as ddgs:
                        for r in ddgs.text(query, max_results=max_results, backend=backend):
                            if isinstance(r, dict):
                                raw.append(r)

                    norm = self._normalize_duckduckgo_search_rows(raw, source=f"duckduckgo_search:{backend}")
                    if norm:
                        return norm[:max_results]
                except Exception as e:
                    last_err = e
                    if self.debug:
                        logger.warning("backend=%s attempt=%s failed: %s", backend, attempt, e)

            self._sleep_with_backoff(attempt)

        raise RuntimeError(f"duckduckgo_search failed after {self.ddg_max_attempts} attempts: {last_err}")

    async def _search_via_instant_answer_api(self, query: str, limit: int) -> List[DuckDuckGoResult]:
        url = "https://api.duckduckgo.com/"
        params = {
            "q": query,
            "format": "json",
            "no_redirect": "1",
            "no_html": "1",
            "skip_disambig": "0",
        }

        headers = {"User-Agent": self.user_agent}

        async with httpx.AsyncClient(
            timeout=self.request_timeout_s,
            headers=headers,
            follow_redirects=True,
        ) as client:
            r = await client.get(url, params=params)
            r.raise_for_status()

            # Prevent huge payload surprises
            content = r.content
            if len(content) > self.instant_answer_max_bytes:
                raise RuntimeError(
                    f"Instant Answer API response too large ({len(content)} bytes) > {self.instant_answer_max_bytes}"
                )

            data = r.json()

        return self._extract_instant_answer_links(data, limit)

    @staticmethod
    def _extract_instant_answer_links(data: Dict[str, Any], limit: int) -> List[DuckDuckGoResult]:
        results: List[DuckDuckGoResult] = []

        def add_item(text: str, first_url: str) -> None:
            title = (text or "").strip()
            url = (first_url or "").strip()
            if not url:
                return
            if not title:
                title = url
            results.append(DuckDuckGoResult(title=title, url=url, snippet="", source="instant_answer_api"))

        # Direct results list
        for it in (data.get("Results") or []):
            if not isinstance(it, dict):
                continue
            add_item(it.get("Text", ""), it.get("FirstURL", ""))
            if len(results) >= limit:
                return results[:limit]

        # Related topics can be nested
        def walk_related(items: Any):
            for obj in items or []:
                if isinstance(obj, dict) and "Topics" in obj:
                    yield from walk_related(obj.get("Topics"))
                else:
                    yield obj

        for it in walk_related(data.get("RelatedTopics") or []):
            if not isinstance(it, dict):
                continue
            add_item(it.get("Text", ""), it.get("FirstURL", ""))
            if len(results) >= limit:
                break

        return results[:limit]
