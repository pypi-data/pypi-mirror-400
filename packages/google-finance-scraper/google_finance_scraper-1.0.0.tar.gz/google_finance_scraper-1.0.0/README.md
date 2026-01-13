# 📈 Google Finance Scraper

A fast, lightweight, and educational Python package to fetch **stock market data and news**
from **Google Finance**, returning clean and ready-to-use **pandas DataFrames**.

This project is built mainly for **learning, analysis, and educational purposes**, while also being
useful for dashboards, research, and personal market tools.

---

## ✨ Key Features

- 📊 Fetch **live stock data** (price, change, high/low, volume, etc.)
- 📰 Fetch **latest stock-related news**
- 🌍 Supports **Indian, US, Forex, and Crypto markets**
- 🔁 Separate functions for **stock data** and **news**
- ⚡ Async-based for better performance
- 🧠 Clean **pandas DataFrame** output
- 🧪 Ideal for students, beginners, and developers learning market data analysis

---

## 🚀 Installation

Install the package directly using pip:

```bash
pip install google-finance-scraper
```
---
## 🧠 Symbol Format (Very Important)

Google Finance uses the following symbol format:
```bash
SYMBOL:EXCHANGE    // TCS:NSE , AAPL:NASDAQ
```

## 📊 Fetch Stock Data 

### ✅ Syntax
```bash
import asyncio
from google_finance_scraper import get_stock_data

stock_df = asyncio.run(get_stock_data("SYMBOL:EXCHANGE"))
print(stock_df)

```

## 📰 Fetch Stock News
### ✅ Syntax
```bash
import asyncio
from google_finance_scraper import get_stock_news

news_df = asyncio.run(get_stock_news("SYMBOL:EXCHANGE"))
print(news_df)
```

