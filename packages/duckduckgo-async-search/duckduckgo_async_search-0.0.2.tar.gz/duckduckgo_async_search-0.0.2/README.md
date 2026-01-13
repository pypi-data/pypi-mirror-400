# duckduckgo-async-search - PIP Package

Async DuckDuckGo search helper:
- Tries `duckduckgo-search` (DDGS SERP wrapper) first
- Falls back to DuckDuckGo Instant Answer API JSON if SERP is rate-limited or unavailable

## Install

```bash
pip install duckduckgo-async-search
```

## Usage

No config/API is needed to use this library.

### Simple Import

```python
import asyncio
from DuckDuckGoAsyncSearch import top_n_result

async def main():
    query = "Capital of Bangladesh"
    items = await top_n_result(query, n=5)
    for it in items:
        print(it.title, it.url)

asyncio.run(main())
```

### Standard Import

```python
!pip install duckduckgo-async-search

from duckduckgo_async_search import DuckDuckGoSearch

async def main():
    client = DuckDuckGoSearch()
    items = await client.top_n_result("Capital of Bangladesh", n=5)

    for it in items:
        print(it.title, it.url, "|", it.source)
        print("--------------------------")

await main()
```

## Notes

- SERP wrappers can be rate-limited depending on your IP/network.
- Instant Answer API is more reliable but does not always reflect “top web results”.

## Contribution

Contributions are welcome and encouraged 🎉  

The source code is publicly available here:  
👉 https://github.com/AbrarJahin/pip-duckduckgo_async_search

### How to contribute
1. Fork the repository to your own GitHub account  
2. Create a new branch for your changes  
3. Make your changes and commit them with clear messages  
4. Push the branch to your fork  
5. Open a Pull Request (PR) to this repository  

All PRs will be reviewed and tested. If everything looks good, the changes will be merged.

### What you can contribute
- Bug fixes
- Performance or reliability improvements
- Documentation improvements
- New features or enhancements
- Test coverage

By contributing, you agree that your contributions will be licensed under the same open-source license as this project.
