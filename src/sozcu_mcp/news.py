"""Stdlib parsing for sozcu.com.tr server-rendered news pages.

Verified live 2026-11-07 against real pages (fixtures in tests/):
- Category pages (/gundem/ 103KB, 52 article links; /ekonomi/ 104KB):
  article anchors href="https://www.sozcu.com.tr/<slug>-p<id>" whose
  inner text is the headline, sometimes followed by a summary line.
  Image anchors carry the same href with empty text — deduped.
- Homepage (264KB): 91 relative article links, same -p<id> shape,
  plus the market ticker in the header (currency-item blocks: DOLAR
  50,15 +0,10 (%0,20), EURO, STERLIN, BITCOIN, ALTIN, FAİZ).
- Article page (149KB): <title> + H1, meta datePublished/dateModified
  / author ("Haber Merkezi") / description, og:title + og:image,
  <time> "07 Kasım 2026 - 08:46", and the body in
  <div class="article-body " property="articleBody"> as consecutive
  <p> elements (ALL-CAPS <p>s are subheadings); the run ends at the
  reactions div; the last <p> is the copyright notice (dropped).
  No JSON-LD on article pages.
- Dated archive /tum-haberler?date=DD-MM-YYYY&pageNumber=N (102KB):
  30 article links per page, same -p<id> shape.
"""
from __future__ import annotations

import html
import re

CATEGORIES = (
    "gundem", "ekonomi", "dunya", "spor", "hayat", "magazin",
    "teknoloji", "finans", "otomotiv",
)

_TR_UPPER_TO_LOWER = str.maketrans({
    "İ": "i", "I": "ı", "Ş": "ş", "Ğ": "ğ",
    "Ü": "ü", "Ö": "ö", "Ç": "ç",
})


def tr_lower(s: str) -> str:
    """Turkish-aware lowercase (str.lower() mangles İ -> i + dot)."""
    return s.translate(_TR_UPPER_TO_LOWER).lower()


def _clean(text: str | None) -> str:
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def _parse_tr_number(raw: str | None) -> float | None:
    """Turkish number -> float ("50,15" -> 50.15, "0,10" -> 0.1)."""
    if raw is None:
        return None
    s = str(raw).strip().replace("%", "").replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


# ---------------------------------------------------------------- listings

_ARTICLE_RE = re.compile(
    r'<a\b[^>]*href="([^"]+-p\d+)"[^>]*>(.*?)</a>', re.S
)


def parse_listing(html_text: str) -> list[dict]:
    """Article links on a listing page -> [{url, title, summary?}]."""
    by_url: dict[str, dict] = {}
    for href, inner in _ARTICLE_RE.findall(html_text):
        url = href if href.startswith("http") else "https://www.sozcu.com.tr" + href
        # Keep line breaks: headline is the first text node, the rest
        # (if any) is the summary.
        text = html.unescape(re.sub(r"<[^>]+>", "\n", inner))
        lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
        if not lines:
            continue  # image anchor; the text anchor carries the headline
        title = lines[0]
        summary = " ".join(lines[1:]).strip()
        row = {"url": url, "title": title}
        if summary and summary != title:
            row["summary"] = summary[:400]
        prev = by_url.get(url)
        if prev is None or (len(title) > len(prev.get("title", ""))):
            by_url[url] = row
    return list(by_url.values())


# ---------------------------------------------------------------- article

def parse_article(html_text: str) -> dict:
    """Article page -> title, author, dates, description, image, body."""
    out: dict = {}
    m = re.search(r"<h1[^>]*>(.*?)</h1>", html_text, re.S)
    if m:
        out["title"] = _clean(m.group(1))
    if not out.get("title"):
        m = re.search(r"<title>(.*?)</title>", html_text, re.S)
        if m:
            out["title"] = _clean(m.group(1)).split(" - Sözcü")[0]

    def _meta(name: str) -> str | None:
        mm = re.search(
            rf'<meta[^>]+(?:property|name)="{re.escape(name)}"[^>]+content="([^"]*)"',
            html_text,
        )
        return html.unescape(mm.group(1)) if mm else None

    out["description"] = _meta("description") or _meta("og:description") or ""
    out["author"] = _meta("author") or ""
    out["date_published"] = _meta("datePublished") or ""
    out["date_modified"] = _meta("dateModified") or ""
    out["image"] = _meta("og:image") or ""
    m = re.search(r"<time[^>]*>([^<]+)</time>", html_text)
    if m:
        out["date_text"] = _clean(m.group(1))
    m = re.search(
        r'<meta property="og:url" content="([^"]+)"', html_text
    ) or re.search(r'<link rel="canonical" href="([^"]+)"', html_text)
    if m:
        out["url"] = m.group(1)

    # Body: <p> run inside the articleBody div, up to the reactions div.
    i = html_text.find('property="articleBody"')
    if i < 0:
        raise ValueError("no article body found on this page")
    end = html_text.find('class="reactions', i)
    region = html_text[i:end if end > 0 else len(html_text)]
    paras = []
    for pm in re.finditer(r"<p[^>]*>(.*?)</p>", region, re.S):
        text = _clean(pm.group(1))
        if not text:
            continue
        if text.startswith("www.sozcu.com.tr"):
            continue  # copyright notice, not body text
        paras.append(text)
    if not paras:
        raise ValueError("no article body paragraphs found on this page")
    out["body"] = "\n\n".join(paras)
    out["paragraph_count"] = len(paras)
    return {k: v for k, v in out.items() if v not in (None, "")}


# ---------------------------------------------------------------- ticker

_TICKER_RE = re.compile(
    r'<a href="https://www\.sozcu\.com\.tr/finans/[^"]+"\s+class="currency-item[^"]*">'
    r'.*?<span[^>]*class="currency-item-name[^"]*"[^>]*>([^<]+)</span>'
    r'.*?<span[^>]*class="currency-item-value[^"]*"[^>]*>([^<]+)</span>'
    r'.*?<span\s+class="currency-item-range">([^<]+)</span>'
    r'\s*<span\s+class="currency-item-range">\(([^)]+)\)</span>',
    re.S,
)


def parse_ticker(html_text: str) -> list[dict]:
    """Market ticker in the page header -> [{name, value, change,
    change_pct}] with Turkish numbers parsed to floats. The page
    carries the ticker twice (header + secondary strip); deduped by
    name, first occurrence wins."""
    rows = []
    seen: set[str] = set()
    for name, value, change, pct in _TICKER_RE.findall(html_text):
        name = _clean(name)
        if name in seen:
            continue
        seen.add(name)
        rows.append(
            {
                "name": name,
                "value": _parse_tr_number(value),
                "change": _parse_tr_number(change),
                "change_pct": _parse_tr_number(pct),
            }
        )
    return rows
