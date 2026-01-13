# duckduckgo-async-search

A tiny, easy-to-use **async** wrapper around DuckDuckGo search with best-effort fallbacks.

## Why this exists

The popular `duckduckgo-search` / `DDGS` interface is convenient, but it is effectively
**synchronous/blocking** (network + parsing happen in the calling thread). In async apps
(FastAPI, agents, notebooks, concurrent pipelines), that can block the event loop and
slow down unrelated tasks.

This library provides a **non-blocking async API**:

- You call `await DuckDuckGoSearch().top_n_result(...)`
- Under the hood, blocking SERP calls run in a **background worker thread**
  (via `asyncio.to_thread`) so the main event loop stays responsive
- Requests can run in parallel with other async tasks

## Fallback strategy (best-effort reliability)

DuckDuckGo can rate-limit or intermittently fail depending on IP/network conditions.
To improve reliability, searches use a two-stage approach:

1) **Primary: `duckduckgo-search` (DDGS) SERP results**
   - Tries multiple backends (default: `lite`, `html`, `auto`)
   - Retries with exponential backoff + jitter (configurable)
   - Returns normalized items (title, url, snippet) and a `source` tag like
     `duckduckgo_search:lite`

2) **Fallback: DuckDuckGo Instant Answer API (JSON)**
   - More stable / less likely to rate-limit
   - Not a full web SERP, but returns useful links from `Results` and `RelatedTopics`
   - Returns items with `source="instant_answer_api"`

## Output

`top_n_result()` returns `List[DuckDuckGoResult]` where each item includes:

- `title: str`
- `url: str`
- `snippet: str` (when available)
- `source: str` (which backend produced the item)

## Install

```bash
pip install duckduckgo-async-search
```

Colab:

```bash
!pip install duckduckgo-async-search
```

## Usage

### Jupyter / Colab

```python
from duckduckgo_async_search import top_n_result

async def main():
    items = await top_n_result("World's largest mangrove forest", n=5)
    for item in items:
        print(item.title)
        print(item.url)
        print(item.snippet)
        print(item.source)
        print("-" * 30)

await main()
```

### Python script (.py)

```python
import asyncio
from duckduckgo_async_search import top_n_result

async def main():
    items = await top_n_result("World's largest mangrove forest", n=5)
    for item in items:
        print(item.title, item.url, item.source)

if __name__ == "__main__":
    asyncio.run(main())
```

### Class usage

```python
from duckduckgo_async_search import DuckDuckGoSearch

async def main():
    client = DuckDuckGoSearch(
        request_timeout_s = 20.0,
        ddg_backends = None,   # e.g., ["lite", "html", "auto"]
        ddg_pause_s = 1.0,                   # pause between attempts - 2.0 or 3.0
        ddg_max_attempts = 3,                  # total attempts across all backends
        instant_answer_max_bytes = 2_000_000,
        html_fallback_max_bytes = 2_500_000,
        debug = False
    )
    items = await client.top_n_result("World's largest beach", n=10)
    for item in items:
        print(item.title, item.url, item.source)

await main()
```

## Notes

- SERP wrappers can be rate-limited depending on your IP/network.
- Instant Answer API is more reliable but may not reflect “top web results”.

## License

MIT License — free for personal and commercial use, modification, and distribution.

## Contributing

Source:
https://github.com/AbrarJahin/pip-duckduckgo_async_search
