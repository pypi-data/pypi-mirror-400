# chesscom-guru

**Async Python client for the Chess.com Public API.**

- **Async-first** (built on `aiohttp`)
- **Automatic retries** for transient failures (429 + 5xx) via `backoff`
- **Library-safe logging** (no files written; you control handlers/levels)
- **Game archive fetching** with optional UTC time filtering + concurrency control

---

## Install

> Requires Python 3.9+ and an async runtime (uses `aiohttp`).

```bash
pip install chesscom-guru
```

---

## Quickstart

```python
import asyncio
import aiohttp

from chesscom_guru import ChesscomAPI

async def main():
    async with aiohttp.ClientSession() as session:
        api = ChesscomAPI(session, user_agent="my-app/1.0")
        # or:
        api = ChesscomAPI(session, headers={"User-Agent": "my-app/1.0"})

        profile = await api.get_player("erik")
        print(profile.get("username"), profile.get("country"))

        data = await api.get_games("erik", max_concurrency=8)
        print("months fetched:", len(data["months"]))

        # Each month payload contains a "games" list
        first_month = next(iter(data["months"].values()))
        print("games in first month:", len(first_month.get("games", [])))

asyncio.run(main())
```

---

## What you get back from `get_games()`

`get_games()` returns a dict shaped like:

```python
{
  "username": "erik",
  "archives": ["https://api.chess.com/pub/player/erik/games/2024/06", ...],
  "months": {
    "<archive_url>": {
      # month payload from chess.com
      "games": [{...}, {...}, ...]
    },
    ...
  },
  "errors": {
    "<archive_url>": "<repr(exception)>",
    ...
  },
  "from_ts": "2024-01-01T00:00:00+00:00" | None,
  "to_ts": "2024-06-30T23:59:59+00:00" | None,
}
```

- **`months`** is keyed by the monthly archive URL.
- **`errors`** includes per-month failures (fetch exceptions) without killing the whole run.

---

## Time filtering (UTC)

You can provide `from_ts` and/or `to_ts` to filter games by **game `end_time`**.

- If you pass a **naive datetime** (no `tzinfo`), the library assumes it is **UTC**.
- Filtering happens in two stages:
  1) filters monthly archive URLs by `(year, month)` derived from your timestamps  
  2) filters games within those months by `end_time`

```python
from datetime import datetime, timezone

from_ts = datetime(2024, 1, 1, tzinfo=timezone.utc)
to_ts   = datetime(2024, 6, 30, 23, 59, 59, tzinfo=timezone.utc)

data = await api.get_games("erik", from_ts=from_ts, to_ts=to_ts)
```

---

## Concurrency

`max_concurrency` controls how many monthly archive requests run at once:

```python
data = await api.get_games("erik", max_concurrency=5)
```

---

## Logging

This library does **not** configure logging by default. If you want to see logs, configure
logging in your application:

```python
import logging
logging.basicConfig(level=logging.WARNING)
```

---

## Supported methods

- `get_player(username)`
- `get_archives(username)`
- `get_games(username, max_concurrency=10, from_ts=None, to_ts=None, user_agent, headers)`

---

## License

PolyForm Noncommercial 1.0.0 — free for noncommercial use.  
For commercial licensing, contact: **richramsell@proton.me**.
