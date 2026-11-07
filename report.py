import os
import sys
import time
import requests
import yfinance as yf
import feedparser
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# 設定圖表深色風格，適配 Discord 深色介面
plt.style.use('dark_background')

# ==========================================
# 1. 監控資產標的設定
# ==========================================
STOCK_INDICES = {
    "道瓊工業 (DJI)": {"ticker": "^DJI", "url": "https://finance.yahoo.com/quote/%5EDJI"},
    "標普 500 (GSPC)": {"ticker": "^GSPC", "url": "https://finance.yahoo.com/quote/%5EGSPC"},
    "納斯達克 (IXIC)": {"ticker": "^IXIC", "url": "https://finance.yahoo.com/quote/%5EIXIC"},
    "費城半導體 (SOX)": {"ticker": "^SOX", "url": "https://finance.yahoo.com/quote/%5ESOX"}
}

COMMODITIES = {
    "WTI 原油": {"ticker": "CL=F", "url": "https://finance.yahoo.com/quote/CL=F"},
    "布蘭特原油": {"ticker": "BZ=F", "url": "https://finance.yahoo.com/quote/BZ=F"}
}

TREASURIES = {
    "美債 10Y": {"ticker": "^TNX", "url": "https://finance.yahoo.com/quote/%5ETNX"},
    "美債 30Y": {"ticker": "^TYX", "url": "https://finance.yahoo.com/quote/%5ETYX"}
}

# ==========================================
# 2. 自動繪製走勢圖模組
# ==========================================
def generate_trend_chart(image_path="trend.png"):
    """抓取盤中分時走勢並繪製多子圖趨勢圖"""
    fig, axes = plt.subplots(3, 1, figsize=(10, 12), sharex=False)
    fig.patch.set_facecolor('#202225')  # Discord 背景底色

    # 1. 四大指數走勢 (標準化為 % 變動，便於放在同一張圖對比)
    ax1 = axes[0]
    ax1.set_facecolor('#2f3136')
    ax1.set_title("US Major Indices Intraday Performance (%)", fontsize=12, color='white', pad=10)
    for name, info in STOCK_INDICES.items():
        try:
            data = yf.download(info["ticker"], period="1d", interval="5m", progress=False)
            if not data.empty and len(data) > 1:
                close = data["Close"].squeeze()
                pct_change = ((close - close.iloc[0]) / close.iloc[0]) * 100
                ax1.plot(data.index, pct_change, label=name, linewidth=1.5)
        except Exception:
            pass
    ax1.axhline(0, color='gray', linestyle='--', linewidth=0.8, alpha=0.7)
    ax1.legend(loc="upper left", fontsize=9, framealpha=0.3)
    ax1.grid(True, linestyle=':', alpha=0.3)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

    # 2. 原油期貨走勢
    ax2 = axes[1]
    ax2.set_facecolor('#2f3136')
    ax2.set_title("Crude Oil Futures Price ($ / Barrel)", fontsize=12, color='white', pad=10)
    for name, info in COMMODITIES.items():
        try:
            data = yf.download(info["ticker"], period="1d", interval="5m", progress=False)
            if not data.empty:
                close = data["Close"].squeeze()
                ax2.plot(data.index, close, label=name, linewidth=1.5)
        except Exception:
            pass
    ax2.legend(loc="upper left", fontsize=9, framealpha=0.3)
    ax2.grid(True, linestyle=':', alpha=0.3)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

    # 3. 美國公債殖利率走勢
    ax3 = axes[2]
    ax3.set_facecolor('#2f3136')
    ax3.set_title("US Treasury Yields (10Y & 30Y Yield %)", fontsize=12, color='white', pad=10)
    for name, info in TREASURIES.items():
        try:
            data = yf.download(info["ticker"], period="1d", interval="5m", progress=False)
            if not data.empty:
                close = data["Close"].squeeze()
                ax3.plot(data.index, close, label=name, linewidth=1.5)
        except Exception:
            pass
    ax3.legend(loc="upper left", fontsize=9, framealpha=0.3)
    ax3.grid(True, linestyle=':', alpha=0.3)
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

    plt.tight_layout()
    plt.savefig(image_path, dpi=120, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    return image_path

# ==========================================
# 3. 數據文字摘要模組
# ==========================================
def fetch_market_overview(header_title):
    lines = [f"## {header_title}\n"]

    lines.append("### 📈 美股四大指數表現")
    for name, info in STOCK_INDICES.items():
        try:
            ticker = yf.Ticker(info["ticker"])
            hist = ticker.history(period="5d")
            if len(hist) >= 2:
                prev_close = hist["Close"].iloc[-2]
                last_row = hist.iloc[-1]
                o, h, l, c = last_row["Open"], last_row["High"], last_row["Low"], last_row["Close"]
                change = c - prev_close
                change_pct = (change / prev_close) * 100
                symbol = "🟢 +" if change >= 0 else "🔴 "

                lines.append(f"**{name}**")
                lines.append(f"- **現價/收盤：** {c:,.2f} ({symbol}{change:,.2f} / {change_pct:+.2f}%)")
                lines.append(f"- **今日區間：** {l:,.2f} ~ {h:,.2f} (開盤: {o:,.2f})")
                lines.append(f"- 🔗 [Yahoo 原始報價]({info['url']})")
        except Exception as e:
            lines.append(f"- **{name}：** 數據獲取異常 ({str(e)})")
    lines.append("")

    lines.append("### 🛢️ 國際原油價格變動")
    for name, info in COMMODITIES.items():
        try:
            ticker = yf.Ticker(info["ticker"])
            hist = ticker.history(period="5d")
            if len(hist) >= 2:
                prev_close = hist["Close"].iloc[-2]
                last_row = hist.iloc[-1]
                h, l, c = last_row["High"], last_row["Low"], last_row["Close"]
                change = c - prev_close
                change_pct = (change / prev_close) * 100
                symbol = "🟢 +" if change >= 0 else "🔴 "

                lines.append(f"**{name}**")
                lines.append(f"- **最新報價：** ${c:,.2f} / 桶 ({symbol}${change:,.2f} / {change_pct:+.2f}%)")
                lines.append(f"- **今日區間：** ${l:,.2f} ~${h:,.2f}")
                lines.append(f"- 🔗 [Yahoo 原始報價]({info['url']})")
        except Exception as e:
            lines.append(f"- **{name}：** 數據獲取異常 ({str(e)})")
    lines.append("")

    lines.append("### 🏛️ 美國 10 年 & 30 年公債殖利率")
    for name, info in TREASURIES.items():
        try:
            ticker = yf.Ticker(info["ticker"])
            hist = ticker.history(period="5d")
            if len(hist) >= 2:
                prev_close = hist["Close"].iloc[-2]
                last_row = hist.iloc[-1]
                c, h, l = last_row["Close"], last_row["High"], last_row["Low"]
                change = c - prev_close
                bps = change * 100
                symbol = "🔺 +" if change >= 0 else "🔻 "

                lines.append(f"**{name}**")
                lines.append(f"- **最新殖利率：** {c:.3f}% ({symbol}{bps:+.1f} bps)")
                lines.append(f"- **今日區間：** {l:.3f}% ~ {h:.3f}%")
                lines.append(f"- 🔗 [Yahoo 原始報價]({info['url']})")
        except Exception as e:
            lines.append(f"- **{name}：** 數據獲取異常 ({str(e)})")

    return "\n".join(lines)

# ==========================================
# 4. 每 2 小時 Yahoo 綜合新聞模組
# ==========================================
def fetch_yahoo_recent_news():
    yahoo_feeds = [
        ("Yahoo 財經與經濟", "https://finance.yahoo.com/news/rssindex"),
        ("Yahoo 美國政治", "https://news.yahoo.com/rss/politics"),
        ("Yahoo 國際地緣與軍事", "https://news.yahoo.com/rss/world"),
        ("CNBC 經濟與民生", "https://search.cnbc.com/rs/search/view.html?partnerId=2000&keywords=economy&sort=date")
    ]

    lines = ["## ⚡ 【Yahoo 新聞 即時快訊：經濟・股市・政治・地緣・民生】\n"]
    count = 0
    seen_titles = set()

    for category, url in yahoo_feeds:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                title = entry.get("title", "").strip()
                link = entry.get("link", "").strip()
                summary = entry.get("summary", "").strip()

                summary = summary.replace("<p>", "").replace("</p>", "").replace("<b>", "").replace("</b>", "")
                if len(summary) > 130:
                    summary = summary[:130] + "..."

                if title and title not in seen_titles:
                    seen_titles.add(title)
                    count += 1
                    lines.append(f"**{count}. [{category}] {title}**")
                    if summary:
                        lines.append(f"> {summary}")
                    lines.append(f"🔗 [閱讀完整報導]({link})\n")

                if count >= 6:
                    break
        except Exception:
            continue
        if count >= 6:
            break

    if count == 0:
        return None

    return "\n".join(lines)

# ==========================================
# 5. Discord 發送（支援純文字或帶圖片）
# ==========================================
def split_message_for_discord(text, max_len=1900):
    chunks = []
    while len(text) > max_len:
        split_idx = text.rfind("\n", 0, max_len)
        if split_idx == -1:
            split_idx = max_len
        chunks.append(text[:split_idx])
        text = text[split_idx:].lstrip("\n")
    if text:
        chunks.append(text)
    return chunks

def send_discord(message, image_path=None):
    if not message:
        return
    webhook_url = os.environ["DISCORD_WEBHOOK_URL"]
    chunks = split_message_for_discord(message)

    # 發送前幾段文字
    for chunk in chunks[:-1]:
        requests.post(webhook_url, json={"content": chunk, "flags": 4}).raise_for_status()

    # 最後一段附帶圖片一起發出
    last_chunk = chunks[-1]
    if image_path and os.path.exists(image_path):
        with open(image_path, "rb") as f:
            files = {"file": (os.path.basename(
