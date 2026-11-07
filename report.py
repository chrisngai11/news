import os
import sys
import json
import requests
import yfinance as yf
import feedparser
import matplotlib.pyplot as plt

plt.style.use('dark_background')

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

def generate_trend_chart(image_path="trend.png"):
    fig, axes = plt.subplots(3, 1, figsize=(10, 11))
    fig.patch.set_facecolor('#202225')

    # 1. 四大指數
    ax1 = axes[0]
    ax1.set_facecolor('#2f3136')
    ax1.set_title("Major Indices (%)", color='white', fontsize=11)
    has1 = False
    for name, info in STOCK_INDICES.items():
        try:
            df = yf.download(info["ticker"], period="5d", interval="15m", progress=False)
            if not df.empty and len(df) > 1:
                c = df["Close"]
                if hasattr(c, "iloc") and len(c.shape) > 1:
                    c = c.iloc[:, 0]
                c_clean = c.dropna()
                base = float(c_clean.iloc[0])
                if base > 0:
                    pct = ((c - base) / base) * 100
                    ax1.plot(df.index, pct, label=name)
                    has1 = True
        except Exception:
            pass
    if has1:
        ax1.axhline(0, color='gray', linestyle='--', linewidth=0.8)
        ax1.legend(loc="upper left", fontsize=8)
    ax1.grid(True, linestyle=':', alpha=0.3)

    # 2. 原油
    ax2 = axes[1]
    ax2.set_facecolor('#2f3136')
    ax2.set_title("Crude Oil ($)", color='white', fontsize=11)
    has2 = False
    for name, info in COMMODITIES.items():
        try:
            df = yf.download(info["ticker"], period="5d", interval="15m", progress=False)
            if not df.empty and len(df) > 1:
                c = df["Close"]
                if hasattr(c, "iloc") and len(c.shape) > 1:
                    c = c.iloc[:, 0]
                ax2.plot(df.index, c, label=name)
                has2 = True
        except Exception:
            pass
    if has2:
        ax2.legend(loc="upper left", fontsize=8)
    ax2.grid(True, linestyle=':', alpha=0.3)

    # 3. 美債利率
    ax3 = axes[2]
    ax3.set_facecolor('#2f3136')
    ax3.set_title("Treasury Yields (%)", color='white', fontsize=11)
    has3 = False
    for name, info in TREASURIES.items():
        try:
            df = yf.download(info["ticker"], period="5d", interval="15m", progress=False)
            if not df.empty and len(df) > 1:
                c = df["Close"]
                if hasattr(c, "iloc") and len(c.shape) > 1:
                    c = c.iloc[:, 0]
                ax3.plot(df.index, c, label=name)
                has3 = True
        except Exception:
            pass
    if has3:
        ax3.legend(loc="upper left", fontsize=8)
    ax3.grid(True, linestyle=':', alpha=0.3)

    plt.tight_layout()
    plt.savefig(image_path, dpi=110, facecolor=fig.get
