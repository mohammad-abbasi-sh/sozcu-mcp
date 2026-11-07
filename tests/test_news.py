"""Offline tests for sozcu_mcp.news — recorded real sozcu.com.tr pages.

Fixtures are real pages fetched 2026-11-07 (curl-cffi chrome120):
- homepage.html: / (71 deduped article links; ticker DOLAR 50,15,
  EURO 55,92, STERLIN 67,01, BITCOIN 75958,14, ALTIN 6556,39,
  FAİZ 35,82).
- category-gundem.html: /gundem/ (25 articles).
- category-ekonomi.html: /ekonomi/ (25 articles).
- article.html: green-passport story p376844 (Haber Merkezi,
  published 2026-11-07T08:46:29+0300, 16 body paragraphs).
- latest.html: /tum-haberler?date=07-11-2026&pageNumber=1 (30 articles).
"""
import os
import unittest

from sozcu_mcp import news as N

FIX = os.path.join(os.path.dirname(__file__), "fixtures")


def _read(name: str) -> str:
    with open(os.path.join(FIX, name), encoding="utf-8") as f:
        return f.read()


class TestListingParse(unittest.TestCase):
    def test_gundem(self):
        rows = N.parse_listing(_read("category-gundem.html"))
        self.assertEqual(len(rows), 25)
        first = rows[0]
        self.assertEqual(
            first["title"],
            "Bit pazarından ayakkabı fiyatına aldığı ürün servet kazandırdı: 75 katı kârla sattı",
        )
        self.assertTrue(first["url"].endswith("-p376923"))

    def test_gundem_summary(self):
        rows = N.parse_listing(_read("category-gundem.html"))
        second = rows[1]
        self.assertEqual(second["title"], "Konya merkezli fuhuş operasyonunda 7 şüpheli tutuklandı")
        self.assertIn("262 bin TL", second["summary"])

    def test_ekonomi(self):
        rows = N.parse_listing(_read("category-ekonomi.html"))
        self.assertEqual(len(rows), 25)
        self.assertIn("otomotiv devi", rows[0]["title"])

    def test_homepage(self):
        rows = N.parse_listing(_read("homepage.html"))
        self.assertEqual(len(rows), 71)
        self.assertEqual(rows[0]["title"], "Galatasaray'dan Osimhen açıklaması! İşte son durumu")

    def test_latest(self):
        rows = N.parse_listing(_read("latest.html"))
        self.assertEqual(len(rows), 30)
        self.assertEqual(rows[0]["title"], "Iğdır'daki silahlı saldırıda 5 şüpheli tutuklandı")
        self.assertIn("5'i tutuklandı", rows[0]["summary"])

    def test_all_have_url_title(self):
        for name in ("category-gundem.html", "category-ekonomi.html",
                     "homepage.html", "latest.html"):
            for r in N.parse_listing(_read(name)):
                self.assertTrue(r["url"].startswith("https://www.sozcu.com.tr/"))
                self.assertTrue(r["title"])


class TestArticleParse(unittest.TestCase):
    def setUp(self):
        self.a = N.parse_article(_read("article.html"))

    def test_core(self):
        self.assertEqual(self.a["title"], "10 meslek grubu için yeşil pasaport Meclis yolunda")
        self.assertEqual(self.a["author"], "Haber Merkezi")
        self.assertEqual(self.a["date_published"], "2026-11-07T08:46:29+0300")
        self.assertEqual(self.a["date_text"], "07 Kasım 2026 - 08:46")

    def test_body(self):
        self.assertEqual(self.a["paragraph_count"], 16)
        self.assertIn("yeşil pasaport", self.a["body"])
        self.assertIn("PİLOTLARA 5 YIL UÇUŞ ŞARTI", self.a["body"])
        self.assertNotIn("Mega Ajans", self.a["body"])  # copyright dropped
        self.assertNotIn("emoji ile tepki ver", self.a["body"])

    def test_image_url(self):
        self.assertTrue(self.a["image"].startswith("https://sozcu01.sozcucdn.com/"))
        self.assertTrue(self.a["url"].endswith("-p376844"))

    def test_no_body(self):
        with self.assertRaises(ValueError):
            N.parse_article("<html><body>no article here</body></html>")


class TestTickerParse(unittest.TestCase):
    def test_all_six(self):
        rows = N.parse_ticker(_read("homepage.html"))
        self.assertEqual(len(rows), 6)
        by_name = {r["name"]: r for r in rows}
        self.assertEqual(by_name["DOLAR"]["value"], 50.15)
        self.assertEqual(by_name["DOLAR"]["change"], 0.1)
        self.assertEqual(by_name["DOLAR"]["change_pct"], 0.2)
        self.assertEqual(by_name["EURO"]["value"], 55.92)
        self.assertEqual(by_name["EURO"]["change"], -0.35)
        self.assertEqual(by_name["STERLIN"]["value"], 67.01)
        self.assertEqual(by_name["BITCOIN"]["value"], 75958.14)
        self.assertEqual(by_name["ALTIN"]["value"], 6556.39)
        self.assertEqual(by_name["FAİZ"]["value"], 35.82)


class TestTrLower(unittest.TestCase):
    def test_turkish(self):
        self.assertEqual(N.tr_lower("İstanbul"), "istanbul")
        self.assertEqual(N.tr_lower("IĞDIR"), "ığdır")
        self.assertEqual(N.tr_lower("Şoför"), "şoför")


if __name__ == "__main__":
    unittest.main()
