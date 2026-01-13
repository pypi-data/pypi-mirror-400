from __future__ import annotations

import asyncio
import logging
import random
import time
import inspect
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Iterable

import httpx

try:
    # New package name (recommended)
    from ddgs import DDGS  # type: ignore
except Exception:
    try:
        # Backward-compat (older installs)
        from duckduckgo_search import DDGS  # type: ignore
    except Exception:
        DDGS = None  # type: ignore

logger = logging.getLogger(__name__)

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
    source: str = ""  # e.g., "ddgs:auto", "duckduckgo_search:lite", "ddg_html_fallback", "instant_answer_api"

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
      1) Try DDGS (ddgs package OR legacy duckduckgo_search) if installed.
      2) Try DuckDuckGo HTML SERP fallback (no external deps).
      3) Fallback to DuckDuckGo Instant Answer API JSON (reliable, but not full SERP).
    """

    def __init__(
        self,
        *,
        user_agent: str = DEFAULT_USER_AGENT,
        request_timeout_s: float = 20.0,
        ddg_backends: Optional[List[str]] = None,   # e.g., ["lite", "html", "auto"]
        ddg_pause_s: float = 1.0,                   # pause between attempts - 2.0 or 3.0
        ddg_max_attempts: int = 3,                  # total attempts across all backends
        instant_answer_max_bytes: int = 2_000_000,
        html_fallback_max_bytes: int = 2_500_000,
        debug: bool = False,
    ) -> None:
        self.user_agent = user_agent
        self.request_timeout_s = request_timeout_s
        self.ddg_backends = ddg_backends or ["lite", "html", "auto"]
        self.ddg_pause_s = ddg_pause_s
        self.ddg_max_attempts = max(1, int(ddg_max_attempts))
        self.instant_answer_max_bytes = instant_answer_max_bytes
        self.html_fallback_max_bytes = html_fallback_max_bytes
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

        errors: List[str] = []

        # 1) DDGS (ddgs / duckduckgo_search)
        if DDGS is not None:
            try:
                out = await asyncio.to_thread(self._search_via_ddgs_sync, query, n)
                if out:
                    return out[:n]
            except Exception as e:
                msg = f"DDGS failed: {e}"
                errors.append(msg)
                logger.warning("DDGS SERP failed; trying HTML fallback. Error: %s", e)

        # 2) HTML SERP fallback (no third-party deps)
        try:
            out2 = await self._search_via_duckduckgo_html_fallback(query, n)
            if out2:
                return out2[:n]
        except Exception as e:
            msg = f"HTML fallback failed: {e}"
            errors.append(msg)
            logger.warning("HTML fallback failed; trying Instant Answer API. Error: %s", e)

        # 3) Instant Answer fallback (often empty for normal web queries)
        try:
            out3 = await self._search_via_instant_answer_api(query, n)
            if out3:
                return out3[:n]
        except Exception as e:
            msg = f"Instant Answer failed: {e}"
            errors.append(msg)

        # If everything returned nothing, raise something actionable
        if errors:
            raise RuntimeError(
                "Search returned 0 items. Attempts:\n- " + "\n- ".join(errors)
            )
        return []

    # -----------------------------
    # Internal helpers
    # -----------------------------
    @staticmethod
    def _normalize_rows(rows: List[Dict[str, Any]], source: str) -> List[DuckDuckGoResult]:
        out: List[DuckDuckGoResult] = []
        for r in rows:
            title = (r.get("title") or "").strip()
            url = (r.get("url") or r.get("href") or "").strip()
            snippet = (r.get("snippet") or r.get("body") or r.get("description") or "").strip()
            if title and url:
                out.append(DuckDuckGoResult(title=title, url=url, snippet=snippet, source=source))
        return out

    def _sleep_with_backoff(self, attempt: int) -> None:
        # Exponential backoff with jitter
        base = self.ddg_pause_s * (2 ** max(0, attempt - 1))
        jitter = random.uniform(0, self.ddg_pause_s)
        time.sleep(base + jitter)

    # -----------------------------
    # DDGS (ddgs or duckduckgo_search)
    # -----------------------------
    def _make_ddgs(self):
        """
        Create DDGS instance compatible with both:
          - ddgs (deedy5): DDGS(proxy=None, timeout=..., verify=...)
          - duckduckgo_search (legacy): DDGS(headers=..., proxy=..., timeout=..., verify=...)
        We only pass parameters that the installed DDGS supports.
        """
        if DDGS is None:
            raise RuntimeError("DDGS is not available (install 'ddgs').")

        sig = inspect.signature(DDGS)  # type: ignore
        kwargs: Dict[str, Any] = {}

        # Some variants support 'headers' (legacy), many do not (ddgs deedy5)
        if "headers" in sig.parameters:
            kwargs["headers"] = {"User-Agent": self.user_agent}

        # Some support timeout/verify/proxy. Add only if accepted.
        if "timeout" in sig.parameters:
            # ddgs expects seconds or a tuple in some versions; pass float seconds.
            kwargs["timeout"] = float(self.request_timeout_s)

        if "verify" in sig.parameters:
            kwargs["verify"] = True

        # proxy support (optional) - only if your users set it; not stored in this class today.

        return DDGS(**kwargs)  # type: ignore

    def _ddgs_text_rows(self, ddgs: Any, query: str, max_results: int, backend: str) -> List[Dict[str, Any]]:
        """
        Normalize differing ddgs / duckduckgo_search method signatures & return types.
        ddgs (deedy5):
            ddgs.text(query, max_results=..., backend=...) -> list[dict]
        duckduckgo_search (legacy):
            ddgs.text(keywords=..., max_results=..., backend=...) -> iterable[dict]
        """
        # Try ddgs signature first
        try:
            raw = ddgs.text(query, max_results=max_results, backend=backend)
        except TypeError:
            # Try legacy signature
            raw = ddgs.text(keywords=query, max_results=max_results, backend=backend)

        if raw is None:
            return []
        if isinstance(raw, list):
            return [r for r in raw if isinstance(r, dict)]
        # generator/iterable
        rows: List[Dict[str, Any]] = []
        try:
            for r in raw:  # type: ignore[assignment]
                if isinstance(r, dict):
                    rows.append(r)
        except Exception:
            # If iteration itself fails, treat as no rows (caller will retry)
            return []
        return rows

    def _search_via_ddgs_sync(self, query: str, max_results: int) -> List[DuckDuckGoResult]:
        if DDGS is None:
            raise RuntimeError("DDGS is not available (install 'ddgs').")

        last_err: Optional[Exception] = None

        for attempt in range(1, self.ddg_max_attempts + 1):
            for backend in self.ddg_backends:
                try:
                    with self._make_ddgs() as ddgs:
                        raw_rows = self._ddgs_text_rows(ddgs, query, max_results=max_results, backend=backend)

                    norm = self._normalize_rows(raw_rows, source=f"ddgs:{backend}")
                    if norm:
                        return norm[:max_results]
                except Exception as e:
                    last_err = e
                    if self.debug:
                        logger.warning("DDGS backend=%s attempt=%s failed: %s", backend, attempt, e)

            self._sleep_with_backoff(attempt)

        raise RuntimeError(f"DDGS failed after {self.ddg_max_attempts} attempts: {last_err}")

    # -----------------------------
    # HTML fallback (no deps)
    # -----------------------------
    async def _search_via_duckduckgo_html_fallback(self, query: str, limit: int) -> List[DuckDuckGoResult]:
        """
        Fetch and parse DuckDuckGo's HTML results page.
        This is a best-effort fallback and may break if DDG changes markup.
        """
        # Use the html endpoint your earlier attempts hit (works sometimes; rate limits are possible)
        url = "https://html.duckduckgo.com/html/"
        headers = {"User-Agent": self.user_agent, "Accept-Language": "en-US,en;q=0.9"}

        async with httpx.AsyncClient(
            timeout=self.request_timeout_s,
            headers=headers,
            follow_redirects=True,
        ) as client:
            # Use POST like common scrapers do
            r = await client.post(url, data={"q": query})
            r.raise_for_status()

            content = r.content
            if len(content) > self.html_fallback_max_bytes:
                raise RuntimeError(
                    f"HTML fallback response too large ({len(content)} bytes) > {self.html_fallback_max_bytes}"
                )

            html = r.text

        # Minimal parsing without BeautifulSoup:
        # Extract result links: look for <a rel="nofollow" class="result__a" href="...">TITLE</a>
        # Snippet: <a ...> plus <a class="result__snippet"...> or <div class="result__snippet">
        results: List[DuckDuckGoResult] = []

        def _strip_tags(s: str) -> str:
            # very small tag stripper
            out = []
            in_tag = False
            for ch in s:
                if ch == "<":
                    in_tag = True
                    continue
                if ch == ">":
                    in_tag = False
                    continue
                if not in_tag:
                    out.append(ch)
            return "".join(out).replace("&amp;", "&").replace("&quot;", '"').replace("&#x27;", "'").strip()

        # Split by result blocks
        blocks = html.split('class="result__body"')
        for b in blocks[1:]:
            # link
            href = ""
            title = ""
            snippet = ""

            # find result__a
            idx = b.find('class="result__a"')
            if idx != -1:
                # find href="..."
                href_i = b.rfind('href="', 0, idx)
                if href_i != -1:
                    href_j = b.find('"', href_i + 6)
                    if href_j != -1:
                        href = b[href_i + 6 : href_j].strip()

                # title between > ... </a>
                gt = b.find(">", idx)
                if gt != -1:
                    end_a = b.find("</a>", gt)
                    if end_a != -1:
                        title = _strip_tags(b[gt + 1 : end_a])

            # snippet
            snip_key = 'class="result__snippet"'
            sidx = b.find(snip_key)
            if sidx != -1:
                gt = b.find(">", sidx)
                if gt != -1:
                    end = b.find("</", gt)
                    if end != -1:
                        snippet = _strip_tags(b[gt + 1 : end])

            if title and href:
                results.append(DuckDuckGoResult(title=title, url=href, snippet=snippet, source="ddg_html_fallback"))
                if len(results) >= limit:
                    break

        return results[:limit]

    # -----------------------------
    # Instant Answer fallback
    # -----------------------------
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

        for it in (data.get("Results") or []):
            if not isinstance(it, dict):
                continue
            add_item(it.get("Text", ""), it.get("FirstURL", ""))
            if len(results) >= limit:
                return results[:limit]

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
