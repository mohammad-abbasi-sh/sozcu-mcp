"""MCP server: unofficial read-only access to sozcu.com.tr news."""
from __future__ import annotations

import json
import re
from datetime import datetime
from zoneinfo import ZoneInfo

from mcp.server.fastmcp import FastMCP

from . import http as _http
from . import news as _N

mcp = FastMCP("sozcu-mcp")

INSTRUCTIONS = """\
Unofficial read-only MCP server for sozcu.com.tr, Türkiye's #1 news
site (~76M visits/month) — headlines by category, latest news from the
dated all-news archive, full article text, keyword search over the
current archive, and the market ticker (USD/EUR/GBP/BTC/gold/rates).
Data comes from the site's server-rendered pages — no login, no API
key. Category pages (/<category>/: gundem, ekonomi, dunya, spor,
hayat, magazin, teknoloji, finans, otomotiv) list ~50 headlines each.
The all-news archive (/tum-haberler?date=DD-MM-YYYY&pageNumber=N)
lists 30 articles per page, newest first. Article pages carry title,
author ("Haber Merkezi"), publish/modify dates, description, image
and the full body text. Keyword search scans today's archive pages
(the site's own /arama search 301-redirects to the homepage, so there
is no server-side search to call) plus the homepage headlines. The
site has no "most read" section (both candidate URLs are 404), so the
market ticker from the page header is offered instead. Read-only;
transport uses Chrome TLS impersonation; requests are spaced ~0.8s
apart. Built by Mohammad Abbasi (mohammad-abbasi-sh) — https://almanibama.ir · https://mabbasi.ir — Turkey MCP
factory.\
"""

_TODAY = ZoneInfo("Europe/Istanbul")


def _err(e: Exception) -> str:
    return json.dumps({"error": str(e)}, ensure_ascii=False)


def _validate_limit(limit: int, lo: int = 1, hi: int = 30) -> int:
    if not lo <= limit <= hi:
        raise ValueError(f"limit must be between {lo} and {hi}")
    return limit


def _today_str() -> str:
    return datetime.now(_TODAY).strftime("%d-%m-%Y")


def _parse_date(date: str | None) -> str:
    if not date:
        return _today_str()
    date = date.strip()
    if not re.fullmatch(r"\d{2}-\d{2}-\d{4}", date):
        raise ValueError("date must be DD-MM-YYYY (e.g. 07-11-2026)")
    return date


@mcp.tool()
def sozcu_headlines(category: str = "gundem", limit: int = 10) -> str:
    """Top headlines in one Sözcü category. category: "gundem"
    (default), "ekonomi", "dunya", "spor", "hayat", "magazin",
    "teknoloji", "finans", "otomotiv". limit 1..30. Returns headlines
    (title, article URL, summary when the listing carries one)."""
    try:
        category = (category or "gundem").strip().lower()
        if category not in _N.CATEGORIES:
            raise ValueError(
                f"category must be one of {', '.join(_N.CATEGORIES)}"
            )
        _validate_limit(limit)
        html_text = _http.fetch_category_html(category)
        rows = _N.parse_listing(html_text)
    except (ValueError, _http.SozcuError) as e:
        return _err(e)
    return json.dumps(
        {
            "category": category,
            "count": min(limit, len(rows)),
            "headlines": rows[:limit],
        },
        ensure_ascii=False,
    )


@mcp.tool()
def sozcu_latest(limit: int = 10, date: str | None = None) -> str:
    """Latest Sözcü news from the dated all-news archive, newest first.
    limit 1..30 (paginates the archive, 30 articles per page); date:
    DD-MM-YYYY, default today (Europe/Istanbul). Returns articles
    (title, article URL, summary when present)."""
    try:
        _validate_limit(limit)
        day = _parse_date(date)
        rows: list[dict] = []
        seen: set[str] = set()
        page = 1
        while len(rows) < limit and page <= 3:
            html_text = _http.fetch_latest_html(day, page)
            batch = _N.parse_listing(html_text)
            fresh = [r for r in batch if r["url"] not in seen]
            if not fresh:
                break
            seen.update(r["url"] for r in fresh)
            rows.extend(fresh)
            page += 1
    except (ValueError, _http.SozcuError) as e:
        return _err(e)
    return json.dumps(
        {"date": day, "count": min(limit, len(rows)), "articles": rows[:limit]},
        ensure_ascii=False,
    )


@mcp.tool()
def sozcu_get_article(article_url: str) -> str:
    """Full text of one Sözcü article. article_url: the article's
    sozcu.com.tr URL (as returned by the headlines/latest/search
    tools, e.g. "https://www.sozcu.com.tr/10-meslek-grubu-icin-yesil-pasaport-meclis-yolunda-p376844").
    Returns title, author, publish/modify dates, description, image
    and the full body text."""
    try:
        if not article_url or not article_url.strip():
            raise ValueError("article_url must not be empty")
        html_text = _http.fetch_article_html(article_url.strip())
        data = _N.parse_article(html_text)
    except (ValueError, _http.SozcuError) as e:
        return _err(e)
    return json.dumps(data, ensure_ascii=False)


@mcp.tool()
def sozcu_search_news(query: str, limit: int = 10) -> str:
    """Keyword search over today's Sözcü news: scans the dated
    all-news archive (up to 3 pages, 30 articles each) plus the
    homepage headlines, matching the keyword in titles and summaries.
    query: e.g. "ekonomi", "deprem", "dolar". limit 1..30. Note: the
    site's own /arama search redirects to the homepage, so this
    searches the current archive instead of a search backend."""
    try:
        if not query or not query.strip():
            raise ValueError("query must not be empty")
        _validate_limit(limit)
        q = _N.tr_lower(query.strip())
        day = _today_str()
        rows: list[dict] = []
        seen: set[str] = set()
        for page in (1, 2, 3):
            html_text = _http.fetch_latest_html(day, page)
            for r in _N.parse_listing(html_text):
                if r["url"] in seen:
                    continue
                seen.add(r["url"])
                hay = _N.tr_lower(f"{r.get('title', '')} {r.get('summary', '')}")
                if q in hay:
                    rows.append(r)
            if len(rows) >= limit:
                break
        if len(rows) < limit:
            html_text = _http.fetch_home_html()
            for r in _N.parse_listing(html_text):
                if r["url"] in seen:
                    continue
                seen.add(r["url"])
                hay = _N.tr_lower(f"{r.get('title', '')} {r.get('summary', '')}")
                if q in hay:
                    rows.append(r)
    except (ValueError, _http.SozcuError) as e:
        return _err(e)
    return json.dumps(
        {"query": query.strip(), "date": day,
         "count": min(limit, len(rows)), "articles": rows[:limit]},
        ensure_ascii=False,
    )


@mcp.tool()
def sozcu_market_rates() -> str:
    """Market ticker from Sözcü's page header: DOLAR, EURO, STERLIN,
    BITCOIN, ALTIN, FAİZ with value, change and change % (TRY, except
    BITCOIN in USD). No arguments. Values are the site's live header
    quotes at fetch time."""
    try:
        html_text = _http.fetch_home_html()
        rows = _N.parse_ticker(html_text)
        if not rows:
            raise ValueError("no market ticker found on the homepage")
    except (ValueError, _http.SozcuError) as e:
        return _err(e)
    return json.dumps({"rates": rows}, ensure_ascii=False)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
