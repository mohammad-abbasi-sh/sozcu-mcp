# sozcu-mcp 🇹🇷

mcp-name: io.github.mohammad-abbasi-sh/sozcu-mcp

سرور MCP غیررسمی و **فقط‌خواندنی** برای sozcu.com.tr — سایت خبری شمارهٔ ۱ ترکیه (`/gundem/` ‏۲۵، و نرخ‌های بازار (دلار/یورو/پوند/بیت‌کوین/طلا/بهره).

> ساختهٔ محمد عباسی در چارچوب «کارخانهٔ MCP ترکیه» (خط لوله به سبک سپهر). وابسته به sozcu.com.tr نیست.

## برای ایجنت‌های هوش مصنوعی

به پیکربندی کلاینت MCP خود اضافه کنید (stdio):

```json
{
  "mcpServers": {
    "sozcu": {
      "command": "uvx",
      "args": ["sozcu-mcp==0.1.1"]
    }
  }
}
```

یا به‌صورت محلی اجرا کنید: `python -m sozcu_mcp.server` (`/gundem/` ‏۲۵، `chrome120`)؛ درخواست‌ها با فاصلهٔ ~۰٫۸ ثانیه؛ همه‌چیز فقط‌خواندنی است.

## نصب

```bash
uvx sozcu-mcp==0.1.1        # اجرای مستقیم (نیازمند uv)
# یا
pip install sozcu-mcp==0.1.1
sozcu-mcp    # سرور MCP را روی stdio راه می‌اندازد
```

## تست‌ها

```bash
python -m venv .venv && .venv/bin/pip install -e .
.venv/bin/python -m unittest discover -s tests -v
```

تست‌های آفلاین روی صفحات واقعیِ ضبط‌شده اجرا می‌شوند (دریافت‌شده در ۲۰۲۶-۱۱-۰۷)؛ تست‌های زنده به sozcu.com.tr وصل می‌شوند. ۲۳/۲۳ سبز (۱۲ آفلاین + ۱۱ زنده) + تست دود MCP روی stdio.

## نقشهٔ راه

- صفحات نویسندگان (ستون‌نویسان در `/yazarlar/`)
- جریان «Son dakika» (صفحهٔ `/son-dakika/` ‏۱۱ مورد فهرست می‌کند)
- صفحات موضوعی فراتر از ۹ دستهٔ پشتیبانی‌شده

## مجوز

MIT — ببینید [LICENSE](LICENSE).

---

Built by [Mohammad Abbasi](https://github.com/mohammad-abbasi-sh) — [Almanibama](https://almanibama.ir) · [mabbasi.ir](https://mabbasi.ir)
