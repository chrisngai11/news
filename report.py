import os
import sys
import requests
import yfinance as yf
import feedparser

def get_morning_report():
    """免費抓取美股四大指數昨日的開盤、最高、最低、收盤與漲跌幅"""
    indices = {
        "道瓊工業指數 (DJI)": {"ticker": "^DJI", "url": "https://finance.yahoo.com/quote/%5EDJI"},
        "標普 500 指數 (S&P 500)": {"ticker": "^GSPC", "url": "https://finance.yahoo.com/quote/%5EGSPC"},
        "納斯達克綜合指數 (NASDAQ)": {"ticker": "^IXIC", "url": "https://finance.yahoo.com/quote/%5EIXIC"},
        "費城半導體指數 (SOX)": {"ticker": "^SOX", "url": "https://finance.yahoo.com/quote/%5ESOX"}
    }
    
    lines = ["## 📊 【09:00 美股四大指數昨日表現】\n"]
    
    for name, info in indices.items():
        try:
            ticker = yf.Ticker(info["ticker"])
            hist = ticker.history(period="5d")
            if len(hist) >= 2:
                prev_close = hist["Close"].iloc[-2]
                last_row = hist.iloc[-1]
                o = last_row["Open"]
                h = last_row["High"]
                l = last_row["Low"]
                c = last_row["Close"]
                change = c - prev_close
                change_pct = (change / prev_close) * 100
                symbol = "🟢 +" if change >= 0 else "🔴 "

                lines.append(f"### {name}")
                lines.append(f"- **收盤價：** {c:,.2f} ({symbol}{change:,.2f} / {change_pct:+.2f}%)")
                lines.append(f"- **開盤價：** {o:,.2f}")
                lines.append(f"- **盤中區間：** {l:,.2f} ~ {h:,.2f}")
                lines.append(f"- 🔗 [查看 Yahoo Finance 原始報價]({info['url']})\n")
        except Exception as e:
            lines.append(f"- **{name}：** 數據獲取異常 ({str(e)})\n")
            
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
            "flags": 4
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
