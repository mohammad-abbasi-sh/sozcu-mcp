# sozcu-mcp 🇹🇷

mcp-name: io.github.mohammad-abbasi-sh/sozcu-mcp

Unofficial **read-only** MCP server for sozcu.com.tr, Türkiye's #1 news site (~76M visits/month) — headlines by category, latest news from the dated archive, full article text, keyword search over the current archive, and the market ticker (USD/EUR/GBP/BTC/gold/rates).

> Built by Mohammad Abbasi as part of the "Turkey MCP factory" (Sepehr-style pipeline). Not affiliated with sozcu.com.tr.

## For AI agents

Add to your MCP client config (stdio):

```json
{
  "mcpServers": {
    "sozcu": {
      "command": "uvx",
      "args": ["sozcu-mcp"]
    }
  }
}
```

Or run locally: `python -m sozcu_mcp.server` (needs `mcp<2`, `curl-cffi`).

## Tools

| Tool | Description |
|------|-------------|
| `sozcu_headlines` | Top headlines in one category — `category`: "gundem" (default), "ekonomi", "dunya", "spor", "hayat", "magazin", "teknoloji", "finans", "otomotiv"; `limit` 1..30 |
| `sozcu_latest` | Latest news from the dated all-news archive, newest first — `limit` 1..30 (paginates, 30/page); `date` DD-MM-YYYY, default today (Europe/Istanbul) |
| `sozcu_get_article` | Full text of one article — `article_url` (as returned by the headlines/latest/search tools); returns title, author, publish/modify dates, description, image, full body |
| `sozcu_search_news` | Keyword search over today's news — scans the dated archive (up to 3 pages) + homepage headlines, matching titles and summaries; `limit` 1..30 |
| `sozcu_market_rates` | Market ticker from the page header: DOLAR, EURO, STERLIN, BITCOIN, ALTIN, FAİZ with value, change and change % |

Example output (`sozcu_get_article` / green-passport story, 7 Nov 2026):

```json
{"title": "10 meslek grubu için yeşil pasaport Meclis yolunda",
 "author": "Haber Merkezi", "date_published": "2026-11-07T08:46:29+0300",
 "date_text": "07 Kasım 2026 - 08:46", "paragraph_count": 16,
 "description": "Yeşil pasaport kapsamının genişletilmesi için Meclis'e sunulan teklifler dikkat çekti. …"}
```

Example output (`sozcu_market_rates`, 7 Nov 2026):

```json
{"rates": [{"name": "DOLAR", "value": 50.15, "change": 0.1, "change_pct": 0.2},
           {"name": "EURO", "value": 55.92, "change": -0.35, "change_pct": -0.62}, …]}
```

## How it works

sozcu.com.tr serves its homepage, category pages (`/<category>/`), article pages (`/<slug>-p<id>`) and the dated all-news archive (`/tum-haberler?date=DD-MM-YYYY&pageNumber=N`, 30 articles/page) fully server-rendered — no login, no API key, no session cookies. Category pages carry 25 headline links each in the fixtures (`/gundem/` 25, `/ekonomi/` 25 in the fixtures). Article pages carry title, author, publish/modify dates, description and image in meta tags, a `<time>` stamp, and the full body as consecutive `<p>` elements in the `articleBody` div (subheadings are ALL-CAPS paragraphs; the run ends at the reactions widget; the copyright paragraph is dropped). There is no JSON-LD on article pages. Two site features do NOT exist server-side and are documented, not faked: the site's own search (`/arama?query=...`) 301-redirects to the homepage for every query, so `sozcu_search_news` scans the dated archive instead; and there is no "most read" section anywhere (`/cok-okunanlar/` and `/en-cok-okunanlar/` are both 404), so the market ticker is offered as the fifth tool. Transport uses Chrome TLS impersonation (`curl-cffi`, `chrome120`); requests are spaced ~0.8s apart; everything is read-only.

## Install

```bash
uvx sozcu-mcp        # run directly (needs uv)
# or
pip install sozcu-mcp
sozcu-mcp    # starts the MCP server on stdio
```

## Tests

```bash
python -m venv .venv && .venv/bin/pip install -e .
.venv/bin/python -m unittest discover -s tests -v
```

Offline tests run on recorded fixtures (real pages fetched 2026-11-07); live tests hit sozcu.com.tr. 23/23 green at build time (12 offline + 11 live) plus an MCP stdio smoke test.

## Roadmap

- Author pages (columnists under /yazarlar/)
- "Son dakika" ticker stream (the /son-dakika/ page lists 11 items; a dedicated tool could poll it)
- Topic pages beyond the 9 supported categories

## License

MIT — see [LICENSE](LICENSE).

---

Built by [Mohammad Abbasi](https://github.com/mohammad-abbasi-sh) — [Almanibama](https://almanibama.ir) · [mabbasi.ir](https://mabbasi.ir)
