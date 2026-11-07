import os
import sys
import json
import requests
import yfinance as yf
import feedparser
import matplotlib.pyplot as plt

plt.style.use("dark_background")

H = "https://"
YH = H + "finance.yahoo.com/quote/"

INDICES = {
    "DJI": "^DJI",
    "S&P 500": "^GSPC",
    "NASDAQ": "^IXIC",
    "SOX": "^SOX"
}

OILS = {
    "WTI Oil": "CL=F",
    "Brent Oil": "BZ=F"
}

BONDS = {
    "US 10Y": "^TNX",
    "US 30Y": "^TYX"
}


def get_series(sym):
    df = yf.download(
        sym,
        period="5d",
        interval="15m",
        progress=False
    )
    if df.empty or len(df) < 2:
        return None
    c = df["Close"]
    if hasattr(c, "iloc"):
        if len(c.shape) > 1:
            c = c.iloc[:, 0]
    return c.dropna()


def make_chart(path):
    fig, axes = plt.subplots(
        3, 1, figsize=(8, 10)
    )
    bg1 = "#202225"
    bg2 = "#2f3136"
    fig.patch.set_facecolor(bg1)

    ax1 = axes[0]
    ax1.set_facecolor(bg2)
    ax1.set_title("Indices (%)")
    for k, sym in INDICES.items():
        try:
            s = get_series(sym)
            if s is not None:
                b = float(s.iloc[0])
                p = ((s - b) / b) * 100
                ax1.plot(s.index, p, label=k)
        except Exception:
            pass
    ax1.legend(loc="upper left")
    ax1.grid(True, alpha=0.3)

    ax2 = axes[1]
    ax2.set_facecolor(bg2)
    ax2.set_title("Crude Oil ($)")
    for k, sym in OILS.items():
        try:
            s = get_series(sym)
            if s is not None:
                ax2.plot(s.index, s, label=k)
        except Exception:
            pass
    ax2.legend(loc="upper left")
    ax2.grid(True, alpha=0.3)

    ax3 = axes[2]
    ax3.set_facecolor(bg2)
    ax3.set_title("Treasury Yields (%)")
    for k, sym in BONDS.items():
        try:
            s = get_series(sym)
            if s is not None:
                ax3.plot(s.index, s, label=k)
        except Exception:
            pass
    ax3.legend(loc="upper left")
    ax3.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(path, dpi=100)
    plt.close()
    return path


def get_market(title):
    out = ["## " + title, ""]

    out.append("### 1. 美股四大指數")
    for k, sym in INDICES.items():
        try:
            t = yf.Ticker(sym)
            h = t.history(period="5d")
            if len(h) >= 2:
                p = float(h["Close"].iloc[-2])
                r = h.iloc[-1]
                c = float(r["Close"])
                hi = float(r["High"])
                lo = float(r["Low"])
                d = c - p
                pct = (d / p) * 100
                u = YH + sym.replace("^", "%5E")
                out.append(f"**{k}**: {c:,.2f}")
                out.append(f"- 漲跌: {d:+.2f} ({pct:+.2f}%)")
                out.append(f"- 區間: {lo:,.2f} ~ {hi:,.2f}")
                out.append(f"- [Yahoo 報價]({u})")
        except Exception as e:
            out.append(f"- {k}: {e}")
    out.append("")

    out.append("### 2. 國際原油期貨")
    for k, sym in OILS.items():
        try:
            t = yf.Ticker(sym)
            h = t.history(period="5d")
            if len(h) >= 2:
                p = float(h["Close"].iloc[-2])
                r = h.iloc[-1]
                c = float(r["Close"])
                hi = float(r["High"])
                lo = float(r["Low"])
                d = c - p
                pct = (d / p) * 100
                u = YH + sym
                out.append(f"**{k}**: ${c:,.2f}")
                out.append(f"- 漲跌: {d:+.2f} ({pct:+.2f}%)")
                out.append(f"- 區間: ${lo:,.2f} ~ ${hi:,.2f}")
                out.append(f"- [Yahoo 報價]({u})")
        except Exception as e:
            out.append(f"- {k}: {e}")
    out.append("")

    out.append("### 3. 美債 10Y & 30Y 殖利率")
    for k, sym in BONDS.items():
        try:
            t = yf.Ticker(sym)
            h = t.history(period="5d")
            if len(h) >= 2:
                p = float(h["Close"].iloc[-2])
                r = h.iloc[-1]
                c = float(r["Close"])
                hi = float(r["High"])
                lo = float(r["Low"])
                bps = (c - p) * 100
                u = YH + sym.replace("^", "%5E")
                out.append(f"**{k}**: {c:.3f}%")
                out.append(f"- 變動: {bps:+.1f} bps")
                out.append(f"- 區間: {lo:.3f}% ~ {hi:.3f}%")
                out.append(f"- [Yahoo 報價]({u})")
        except Exception as e:
            out.append(f"- {k}: {e}")

    return "\n".join(out)


def get_news():
    u1 = H + "finance.yahoo.com/news/rssindex"
    u2 = H + "news.yahoo.com/rss/politics"
    u3 = H + "news.yahoo.com/rss/world"
    feeds = [
        ("財經", u1),
        ("政治", u2),
        ("國際", u3)
    ]
    out = ["## Yahoo 2小時即時快訊", ""]
    cnt = 0
    seen = set()
    for cat, u in feeds:
        try:
            fd = feedparser.parse(u)
            for e in fd.entries:
                t = e.get("title", "").strip()
                lk = e.get("link", "").strip()
                if t and t not in seen:
                    seen.add(t)
                    cnt += 1
                    out.append(f"**{cnt}. [{cat}] {t}**")
                    out.append(f"[閱讀原文]({lk})\n")
                if cnt >= 6:
                    break
        except Exception:
            continue
        if cnt >= 6:
            break
    if cnt == 0:
        return None
    return "\n".join(out)


def send_dc(text, img=None):
    if not text:
        return
    url = os.environ["DISCORD_WEBHOOK_URL"]
    msg = text[:1900]
    if img and os.path.exists(img):
        with open(img, "rb") as f:
            fl = {"file": ("chart.png", f, "image/png")}
            pl = {"content": msg, "flags": 4}
            dt = {"payload_json": json.dumps(pl)}
            r = requests.post(url, data=dt, files=fl)
            r.raise_for_status()
    else:
        pl = {"content": msg, "flags": 4}
        r = requests.post(url, json=pl)
        r.raise_for_status()


if __name__ == "__main__":
    m = sys.argv[1] if len(sys.argv) > 1 else "morning"
    if m == "morning":
        txt = get_market("09:00 美股收盤・原油・美債總結")
        pic = make_chart("m.png")
        send_dc(txt, pic)
    elif m == "intraday":
        txt = get_market("美股開盤 1 小時盤中速報")
        pic = make_chart("i.png")
        send_dc(txt, pic)
    else:
        txt = get_news()
        send_dc(txt, None)