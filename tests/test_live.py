"""Live tests for sozcu_mcp — real requests to sozcu.com.tr.

Requires network + Chrome TLS impersonation (curl-cffi). The server
is polite by design (~0.8s between requests), so this file takes
~20s. Run: python -m unittest discover -s tests -v

Headlines change during the day; tests assert structure and sane
ranges, not exact titles.
"""
import json
import unittest

from sozcu_mcp import http as H
from sozcu_mcp import news as N


class TestLiveHeadlines(unittest.TestCase):
    def test_gundem(self):
        html_text = H.fetch_category_html("gundem")
        rows = N.parse_listing(html_text)
        self.assertGreater(len(rows), 10)
        self.assertIn("-p", rows[0]["url"])

    def test_ekonomi(self):
        html_text = H.fetch_category_html("ekonomi")
        rows = N.parse_listing(html_text)
        self.assertGreater(len(rows), 10)

    def test_unknown_category_404(self):
        with self.assertRaises(H.SozcuError):
            H.fetch_category_html("xyzabcqwerty")


class TestLiveLatest(unittest.TestCase):
    def test_today(self):
        html_text = H.fetch_latest_html("07-11-2026", 1)
        rows = N.parse_listing(html_text)
        self.assertEqual(len(rows), 30)


class TestLiveArticle(unittest.TestCase):
    def test_green_passport(self):
        html_text = H.fetch_article_html(
            "https://www.sozcu.com.tr/10-meslek-grubu-icin-yesil-pasaport-meclis-yolunda-p376844"
        )
        a = N.parse_article(html_text)
        self.assertEqual(a["title"], "10 meslek grubu için yeşil pasaport Meclis yolunda")
        self.assertEqual(a["author"], "Haber Merkezi")
        self.assertGreater(a["paragraph_count"], 10)


class TestLiveTicker(unittest.TestCase):
    def test_rates(self):
        html_text = H.fetch_home_html()
        rows = N.parse_ticker(html_text)
        self.assertEqual(len(rows), 6)
        by_name = {r["name"]: r for r in rows}
        self.assertGreater(by_name["DOLAR"]["value"], 40)
        self.assertLess(by_name["DOLAR"]["value"], 60)


class TestLiveServerTools(unittest.TestCase):
    """End-to-end: call the MCP tool functions and check JSON output."""

    def test_headlines_tool(self):
        from sozcu_mcp.server import sozcu_headlines

        out = json.loads(sozcu_headlines("gundem", limit=3))
        self.assertNotIn("error", out)
        self.assertEqual(out["count"], 3)

    def test_latest_tool(self):
        from sozcu_mcp.server import sozcu_latest

        out = json.loads(sozcu_latest(limit=5, date="07-11-2026"))
        self.assertNotIn("error", out)
        self.assertEqual(out["count"], 5)

    def test_article_tool(self):
        from sozcu_mcp.server import sozcu_get_article

        out = json.loads(
            sozcu_get_article(
                "https://www.sozcu.com.tr/10-meslek-grubu-icin-yesil-pasaport-meclis-yolunda-p376844"
            )
        )
        self.assertNotIn("error", out)
        self.assertIn("yeşil pasaport", out["body"])

    def test_search_tool(self):
        from sozcu_mcp.server import sozcu_search_news

        out = json.loads(sozcu_search_news("pasaport", limit=5))
        self.assertNotIn("error", out)
        self.assertGreaterEqual(out["count"], 1)

    def test_bad_category_error(self):
        from sozcu_mcp.server import sozcu_headlines

        out = json.loads(sozcu_headlines("nope"))
        self.assertIn("error", out)


if __name__ == "__main__":
    unittest.main()
