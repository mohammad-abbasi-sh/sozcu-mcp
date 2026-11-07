# sozcu-mcp 🇹🇷

mcp-name: io.github.mohammad-abbasi-sh/sozcu-mcp

sozcu.com.tr için resmi olmayan **salt okunur** MCP sunucusu — Türkiye'nin 1 numaralı haber sitesi (~76 milyon ziyaret/ay): kategoriye göre manşetler, tarihli arşivden en son haberler, haberin tam metni, güncel arşivde anahtar kelime araması ve piyasa göstergeleri (dolar/euro/sterlin/bitcoin/altın/faiz).

> Mohammad Abbasi tarafından "Turkey MCP factory" (Sepehr tarzı hat) kapsamında geliştirildi. sozcu.com.tr ile bağlantısı yoktur.

## Yapay zekâ ajanları için

MCP istemci yapılandırmanıza ekleyin (stdio):

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

Veya yerelde çalıştırın: `python -m sozcu_mcp.server` (`mcp<2`, `curl-cffi` gerekir).

## Araçlar

| Araç | Açıklama |
|------|-------------|
| `sozcu_headlines` | Bir kategorideki manşetler — `category`: "gundem" (varsayılan), "ekonomi", "dunya", "spor", "hayat", "magazin", "teknoloji", "finans", "otomotiv"; `limit` 1..30 |
| `sozcu_latest` | Tarihli tüm-haberler arşivinden en son haberler, yeniden eskiye — `limit` 1..30 (sayfalar, 30/sayfa); `date` GG-AA-YYYY, varsayılan bugün (Europe/Istanbul) |
| `sozcu_get_article` | Bir haberin tam metni — `article_url` (headlines/latest/search araçlarının döndürdüğü URL); başlık, yazar, yayın/değişiklik tarihleri, açıklama, görsel, tam metin |
| `sozcu_search_news` | Bugünün haberlerinde anahtar kelime araması — tarihli arşivi (3 sayfaya kadar) + ana sayfa manşetlerini tarar; `limit` 1..30 |
| `sozcu_market_rates` | Sayfa başlığındaki piyasa göstergeleri: DOLAR, EURO, STERLIN, BITCOIN, ALTIN, FAİZ (değer, değişim, değişim %) |

## Nasıl çalışır

sozcu.com.tr ana sayfasını, kategori sayfalarını (`/<kategori>/`), haber sayfalarını (`/<slug>-p<id>`) ve tarihli tüm-haberler arşivini (`/tum-haberler?date=GG-AA-YYYY&pageNumber=N`, 30 haber/sayfa) tamamen sunucu taraflı gösterir — giriş, API anahtarı ve çerez gerekmez. Kategori sayfalarında 25 manşet bağlantısı vardır (`/gundem/` 25, `/ekonomi/` 25). Haber sayfalarında başlık, yazar, yayın/değişiklik tarihleri, açıklama ve görsel meta etiketlerdedir; tam metin `articleBody` div'indeki ardışık `<p>` öğeleridir (ara başlıklar BÜYÜK HARFLİ paragraflardır; metin tepkiler (reactions) bölümünde biter; telif paragrafı atılır). Haber sayfalarında JSON-LD yoktur. Sitenin iki özelliği sunucu tarafında yoktur ve uydurulmaz, belgelenir: sitenin kendi araması (`/arama?query=...`) her sorguda ana sayfaya yönlenir, bu yüzden `sozcu_search_news` tarihli arşivi tarar; ve sitede hiç "en çok okunan" bölümü yoktur (`/cok-okunanlar/` ve `/en-cok-okunanlar/` ikisi de 404), bu yüzden beşinci araç olarak piyasa göstergeleri sunulur. Aktarım Chrome TLS taklidi kullanır (`curl-cffi`, `chrome120`); istekler ~0,8 sn arayla; her şey salt okunurdur.

## Kurulum

```bash
uvx sozcu-mcp        # doğrudan çalıştır (uv gerekir)
# veya
pip install sozcu-mcp
sozcu-mcp    # MCP sunucusunu stdio üzerinde başlatır
```

## Testler

```bash
python -m venv .venv && .venv/bin/pip install -e .
.venv/bin/python -m unittest discover -s tests -v
```

Çevrimdışı testler kaydedilmiş gerçek sayfalarla çalışır (2026-11-07'de çekildi); canlı testler sozcu.com.tr'ye bağlanır. 23/23 yeşil (12 çevrimdışı + 11 canlı) + MCP stdio duman testi.

## Yol haritası

- Yazar sayfaları (`/yazarlar/` altındaki köşe yazarları)
- "Son dakika" akışı (`/son-dakika/` sayfası 11 öğe listeler)
- Desteklenen 9 kategorinin dışındaki konu sayfaları

## Lisans

MIT — bkz. [LICENSE](LICENSE).
