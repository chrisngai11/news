import os
import sys
import json
import requests
import yfinance as yf
import feedparser
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

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
# 2. matplotlib 自動繪圖模組
# ==========================================
def generate_trend_chart(image_path="trend.png"):
    fig, axes = plt.subplots(3, 1, figsize=(10, 12), sharex=False)
    fig.patch.set_facecolor('#202225')

    # 子圖 1：四大指數
    ax1 = axes[0]
    ax1.set_facecolor('#2f3136')
    ax1.set_title("US Major Indices Performance (%)", fontsize=12, color='white', pad=10)
    has_data1 = False
    for name, info in STOCK_INDICES.items():
        try:
            data = yf.download(info["ticker"], period="5d", interval="15m", progress=False)
            if not data.empty and len(data) > 1:
                close = data["Close"]
                if hasattr(close, "iloc") and len(close.shape) > 1:
                    close = close.iloc[:, 0]
                base_val = float(close.dropna().iloc[0])
                if base_val > 0:
                    pct_change = ((close - base_val) / base_val) * 100
                    ax1.plot(data.index, pct_change, label
