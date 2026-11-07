import os
import sys
import requests
import yfinance as yf
import feedparser

def get_morning_report():
    """免費抓取美股四大指數、原油價格以及美債 10年/30年 殖利率昨日表現"""
    
    # 1. 美股四大指數
    stock_indices = {
        "道瓊工業指數 (DJI)": {"ticker": "^DJI", "url": "https://finance.yahoo.com/quote/%5EDJI"},
        "標普 500 指數 (S&P 500)": {"ticker": "^GSPC", "url": "https://finance.yahoo.com/quote/%5EGSPC"},
        "納斯達克綜合指數 (NASDAQ)": {"ticker": "^IXIC", "url": "https://finance.yahoo.com/quote/%5EIXIC"},
        "費城半導體指數 (SOX)": {"ticker": "^SOX", "url": "https://finance.yahoo.com/quote/%5ESOX"}
    }

    # 2. 能源商品（原油）
    commodities = {
        "WTI 輕原油期貨": {"ticker": "CL=F", "url": "https://finance.yahoo.com/quote/CL=F"},
        "布蘭特原油期貨 (Brent)": {"ticker": "BZ=F", "url": "https://finance.yahoo.com/quote/BZ=F"}
    }

    # 3. 美債長天期殖利率（^TNX 與 ^TYX 報價為年化殖利率百分比）
    treasuries = {
        "美國 10 年期公債殖利率 (US10Y)": {"ticker": "^TNX", "url": "https://finance.yahoo.com/quote/%5ETNX"},
        "美國 30 年期公債殖利率 (US30Y)": {"ticker": "^TYX", "url": "https://finance.yahoo.com/quote/%5ETYX"}
    }
    
    lines = ["## 📊 【09:00 美股四大指數、原油與長天期美債利率表現】\n"]

    # --- 區塊一：四大指數 ---
    lines.append("### 📈 美股四大指數")
    for name, info in stock_indices.items():
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
                lines.append(f"- **收盤價：** {c:,.2f} ({symbol}{change:,.2f} / {change_pct:+.2f}%)")
                lines.append(f"- **盤中區間：** {l:,.2f} ~ {h:,.2f} (開盤: {o:,.2f})")
                lines.append(f"- 🔗 [查看 Yahoo Finance 報價]({info['url']})")
        except Exception as e:
            lines.append(f"- **{name}：** 數據獲取異常 ({str(e)})")
    lines.append("")

    # --- 區塊二：原油價格 ---
    lines.append("### 🛢️ 國際原油價格")
    for name, info in commodities.items():
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
                lines.append(f"- **最新價格：** ${c:,.2f} / 桶 ({symbol}${change:,.2f} / {change_pct:+.2f}%)")
                lines.append(f"- **盤中區間：** ${l:,.2f} ~ ${h:,.2f}")
                lines.append(f"- 🔗 [查看 Yahoo Finance 報價]({info['url']})")
        except Exception as e:
            lines.append(f"- **{name}：** 數據獲取異常 ({str(e)})")
    lines.append("")

    # --- 區塊三：美債 10 年 & 30 年殖利率 ---
    lines.append("### 🏛️ 美債長天期殖利率")
    for name, info in treasuries.items():
        try:
            ticker = yf.Ticker(info["ticker"])
            hist = ticker.history(period="5d")
            if len(hist) >= 2:
                prev_close = hist["Close"].iloc[-2]
                last_row = hist.iloc[-1]
                c = last_row["Close"]
                h = last_row["High"]
                l = last_row["Low"]
                change = c - prev_close
                bps = change * 100  # 1% = 100 基點 (bps)
                symbol = "🔺 +" if change >= 0 else "🔻 "

                lines.append(f"**{name}**")
                lines.append(f"- **最新殖利率：** {c:.3f}% ({symbol}{bps:+.1f} bps)")
                lines.append(f"- **盤中區間：** {l:.3f}% ~ {h:.3f}%")
                lines.append(f"- 🔗 [查看 Yahoo Finance 報價]({info['url']})")
        except Exception as e:
            lines.append(f"- **{name}：** 數據獲取異常 ({str(e)})")
            
    return "\n".join(lines)

def get_noon_report():
    """免費抓取過去 24 小時美國最新財經與國際政經新聞 RSS"""
    rss_feeds = [
        ("CNBC 美國經濟與市場", "https://search.cnbc.com/rs/search/view.html?partnerId=2000&keywords=us%20economy&sort=date"),
        ("Yahoo Finance 最新市場動態", "https://finance.yahoo.com/news/rssindex")
    ]
    
    lines = ["## 🌍 【13:00 美股最新政經與地緣消息】\n"]
    
    count = 0
    seen_titles = set()
    
    for source_name, url in rss_feeds:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                title = entry.get("title", "").strip()
                link = entry.get("link", "").strip()
                summary = entry.get("summary", "").strip()
                
                summary = summary.replace("<p>", "").replace("</p>", "").replace("<b>", "").replace("</b>", "")
                if len(summary) > 120:
                    summary = summary[:120] + "..."
                    
                if title and title not in seen_titles:
                    seen_titles.add(title)
                    count += 1
                    lines.append(f"**{count}. {title}**")
                    if summary:
                        lines.append(f"> {summary}")
                    lines.append(f"🔗 [閱讀完整報導]({link})\n")
                    
                if count >= 8:
                    break
        except Exception:
            continue
        if count >= 8:
            break

    if count == 0:
        lines.append("暫無最新新聞源更新，請稍後重試。")
        
    return "\n".join(lines)

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

def send_discord(message):
    webhook_url = os.environ["DISCORD_WEBHOOK_URL"]
    chunks = split_message_for_discord(message)
    
    for chunk in chunks:
        payload = {
            "content": chunk,
            "flags": 4  # 隱藏預覽圖卡，避免版面雜亂
        }
        resp = requests.post(webhook_url, json=payload)
        resp.raise_for_status()

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "morning"
    if mode == "morning":
        content = get_morning_report()
    else:
        content = get_noon_report()
    send_discord(content)
