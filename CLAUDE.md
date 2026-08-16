# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python bot that crawls the latest finance news from Taiwanese news sites (UDN, ChinaTimes, Ettoday, CTEE, LTN, Cnyes, Yahoo Stock), summarizes and extracts stock-related keywords via OpenAI, and pushes formatted messages to a Telegram group/channel via the Telegram Bot API. Despite the repo name ("ScrapyNewsBot"), the Scrapy framework was removed in a past refactor (see commit `c0a9fca`) — the crawlers are now plain custom classes scheduled with APScheduler. `readme.md` still describes the old Scrapy-based setup and is out of date; trust the code, not the README.

## Setup & Running

```bash
pip install -r requirements.txt
cp .env.example .env   # then fill in TG_TOKEN, TG_CHAT_ID, OPENAI_API_KEY
python main.py          # starts the APScheduler-driven crawl loop (blocking)
```

Config is loaded from environment variables via `python-dotenv` in `config.py` (`TG_TOKEN`, `TG_CHAT_ID`, `OPENAI_API_KEY`, `LOGS_DIR`, default `logs`). There is no settings file to edit — everything comes from `.env`.

Selenium-based crawlers (ChinaTimes, CTEE, LTN) require a local Chrome + matching ChromeDriver on PATH; `webdriver.Chrome()` is invoked headless with no explicit driver path.

## Testing

There is no pytest suite/config — `tests/test_simple_crawler.py` is a standalone script that exercises crawlers directly against live websites (no mocking):

```bash
python tests/test_simple_crawler.py
```

Edit the `if __name__ == '__main__':` block at the bottom of that file to toggle which crawlers/pipeline get exercised. Because it hits real sites (and, for `test_full_pipeline`, real OpenAI/Telegram APIs), run it selectively and expect it to need `.env` configured.

## Architecture

Three-layer pipeline, orchestrated by `main.py`'s `NewsManager`:

1. **Crawlers** (`crawlers/`) — each site has its own `*Crawler(NewsCrawler)` subclass implementing `get_latest_news() -> Optional[Dict]`, returning `{'url', 'title', 'content', 'published_at'}` for the single most recent article, or `None` on failure. `crawlers/base_crawler.py` (`NewsCrawler` ABC) provides shared plumbing:
   - `self.session` — a `requests.Session` with a randomized User-Agent (rotated from `USER_AGENTS`) for sites scrapeable via plain HTTP (`fetch_page()` → BeautifulSoup, or `self.session.get(...).json()` directly for a JSON API).
   - `browser_session()` — a context manager yielding a headless Selenium Chrome `driver`, for JS-rendered sites; paired with `fetch_page_with_browser(driver, url)`. Use this (not `fetch_page`) for sites that render content client-side (currently ChinaTimes, CTEE, LTN use this; UDN, Ettoday, and Yahoo use RSS + `fetch_page`; Cnyes calls its frontend's public JSON API directly and needs neither).
   - New crawlers should follow whichever pattern (RSS/requests, JSON API, or Selenium) matches how the target site actually serves content — prefer a plain HTTP/JSON approach over Selenium whenever the site's list/article pages are server-rendered (check with `curl`/`requests` before reaching for `browser_session()`), since it's far cheaper to run and less prone to breaking on markup/class-name changes. Always return `None` at every failure point rather than raising, since `NewsManager`/`NewsProcessor` expect `Optional[Dict]`.

2. **Processor** (`processors/news_processor.py`) — `NewsProcessor.process_news(news_item, crawler_name)` is the single entry point tying crawlers to output. It: dedupes against `logs/previous.log` (a rolling JSON list of the last ~20 processed items, keyed on URL), filters out specific unwanted content (e.g. articles by a specific author), calls OpenAI for a summary + finance keyword extraction, formats an HTML Telegram message (title as link, summary, keywords, timestamp), and sends it. Returns `True`/`False` for success/skip — never raises out to the caller.

3. **Services** (`services/`) — thin API wrappers:
   - `OpenAIService` — `summarize_news()` and `extract_finance_keywords()`, both built on a shared `_make_request()` (model `gpt-4o-mini`, low temperature, 30s timeout, swallows exceptions and returns `""`/empty).
   - `TelegramNotifier` — `send_message()` (auto-chunks text over 4096 chars via `text_slicer`), `send_photo()`, `send_file()`, `get_update()` (useful for discovering `chat_id` during setup).

`main.py`'s `NewsManager` wires one crawler instance + one shared `NewsProcessor` together and registers each crawler with APScheduler on its own polling interval (`scheduler.add_job(..., 'interval', seconds=N)` per site — currently 60–100s, staggered to avoid hammering all sites simultaneously). To add a new source: write a crawler subclass, add it to `NewsManager.crawlers`, and register a scheduled job for it (see the commented-out `ctee` job in `main.py` for the pattern of temporarily disabling a source).

State is file-based, not a database: dedup history lives in `logs/previous.log` (JSON array, git-ignored).
