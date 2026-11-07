"""HTTP layer for sozcu_mcp.

sozcu.com.tr serves its homepage, category pages (/gundem/, /ekonomi/,
/dunya/, /spor/, ...), article pages (/<slug>-p<id>) and the dated
all-news archive (/tum-haberler?date=DD-MM-YYYY&pageNumber=N) fully
server-rendered — no login, no API key, no session cookies needed.
Plain HTTP 200 with a browser UA (verified live 2026-11-07). The
transport still uses curl-cffi chrome120 impersonation, the same proven
pattern as the other Turkey-factory servers. Requests are kept gentle
(one at a time, ~0.8s apart) and read-only.

Caveats found while probing (2026-11-07): the site's own search
(/arama?query=...) 301-redirects to the homepage for every query —
the server-side search is dead (only a stale JSON-LD urlTemplate
mentions it) — so keyword search here scans the dated news archive
instead. There is no "most read" section anywhere on the site
(/cok-okunanlar/ and /en-cok-okunanlar/ are both 404); the market
ticker (DOLAR/EURO/...) in the page header is offered instead.
"""
from __future__ import annotations

import time
from urllib.parse import quote

from curl_cffi import requests as _r

BASE = "https://www.sozcu.com.tr"
TIMEOUT = 30.0
MIN_INTERVAL = 0.8  # seconds between requests — be polite

_HEADERS = {
    "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
}

_last_fetch = 0.0


class SozcuError(RuntimeError):
    pass


def _get(url: str) -> str:
    global _last_fetch
    wait = MIN_INTERVAL - (time.monotonic() - _last_fetch)
    if wait > 0:
        time.sleep(wait)
    try:
        resp = _r.get(url, impersonate="chrome120", headers=_HEADERS, timeout=TIMEOUT)
    except Exception as e:
        raise SozcuError(f"network error fetching {url}: {e}") from e
    finally:
        _last_fetch = time.monotonic()
    if resp.status_code == 403:
        raise SozcuError(
            "sozcu.com.tr refused the request (HTTP 403, bot wall) — try again later"
        )
    if resp.status_code == 429:
        raise SozcuError(
            "sozcu.com.tr rate-limited the request (HTTP 429) — try again later"
        )
    if resp.status_code in (404, 410):
        raise SozcuError(
            f"page not found (HTTP {resp.status_code}): {url} — check the "
            "category / article URL"
        )
    if resp.status_code != 200:
        raise SozcuError(f"unexpected HTTP {resp.status_code} fetching {url}")
    return resp.text


def fetch_home_html() -> str:
    return _get(f"{BASE}/")


def fetch_category_html(category: str) -> str:
    """Category listing: /<category>/ (gundem, ekonomi, dunya, ...)."""
    return _get(f"{BASE}/{quote(category)}/")


def fetch_article_html(article_url: str) -> str:
    """Article page (full URL or path)."""
    if article_url.startswith("http"):
        url = article_url
    else:
        url = f"{BASE}/{article_url.lstrip('/')}"
    if "sozcu.com.tr" not in url:
        raise SozcuError(f"not a sozcu.com.tr URL: {article_url}")
    return _get(url)


def fetch_latest_html(date_str: str, page: int = 1) -> str:
    """Dated all-news archive: /tum-haberler?date=DD-MM-YYYY&pageNumber=N."""
    return _get(f"{BASE}/tum-haberler?date={quote(date_str)}&pageNumber={page}")
