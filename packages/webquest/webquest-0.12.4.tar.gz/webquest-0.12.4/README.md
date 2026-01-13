<p align="center">
  <img src="https://github.com/mustafametesengul/webquest/raw/main/docs/images/logo.svg" alt="WebQuest Logo" width="260">
</p>

# WebQuest

WebQuest is an extensible Python toolkit for high-level web scraping, built around a generic Playwright-based scraper interface for quickly building, running, and reusing custom scrapers.

For detailed usage instructions and API reference, please visit the [documentation](https://mustafametesengul.github.io/webquest/).

To use WebQuest as a Model Context Protocol (MCP) server, please visit the [WebQuest MCP repository](https://github.com/mustafametesengul/webquest-mcp).

**Scrapers**

- **[Any Article:](https://mustafametesengul.github.io/webquest/scrapers/any_article/)** Extracts readable content from arbitrary web articles.
- **[DuckDuckGo Search:](https://mustafametesengul.github.io/webquest/scrapers/duckduckgo_search/)** General web search using DuckDuckGo.
- **[Google News Search:](https://mustafametesengul.github.io/webquest/scrapers/google_news_search/)** News-focused search via Google News.
- **[YouTube Search:](https://mustafametesengul.github.io/webquest/scrapers/youtube_search/)** Search YouTube videos, channels, posts, and shorts.
- **[YouTube Transcript:](https://mustafametesengul.github.io/webquest/scrapers/youtube_transcript/)** Fetch transcripts for YouTube videos.

**Browsers**

- **[Hyperbrowser:](https://mustafametesengul.github.io/webquest/browsers/hyperbrowser/)** A cloud-based browser service for running Playwright scrapers without managing infrastructure.

## Installation

Installing using pip:

```bash
pip install webquest
```

Installing using uv:

```bash
uv add webquest
```

## Usage

To use **Hyperbrowser**, you need to set the `HYPERBROWSER_API_KEY` environment variable.

Example usage of the DuckDuckGo Search scraper:

```python
import asyncio

from webquest.browsers import Hyperbrowser
from webquest.scrapers import DuckDuckGoSearch


async def main() -> None:
    scraper = DuckDuckGoSearch(browser=Hyperbrowser())

    response = await scraper.run(
        scraper.request_model(query="Pizza Toppings"),
    )
    print(response.model_dump_json(indent=4))


if __name__ == "__main__":
    asyncio.run(main())
```

You can also run multiple requests at the same time:

```python
import asyncio

from webquest.browsers import Hyperbrowser
from webquest.scrapers import DuckDuckGoSearch


async def main() -> None:
    scraper = DuckDuckGoSearch(browser=Hyperbrowser())

    responses = await scraper.run(
        scraper.request_model(query="Pizza Toppings"),
        scraper.request_model(query="AI News"),
    )
    for response in responses:
        print(response.model_dump_json(indent=4))


if __name__ == "__main__":
    asyncio.run(main())
```

## Disclaimer

This tool is for educational and research purposes only. The developers of WebQuest are not responsible for any misuse of this tool. Scraping websites may violate their Terms of Service. Users are solely responsible for ensuring their activities comply with all applicable laws and website policies.
