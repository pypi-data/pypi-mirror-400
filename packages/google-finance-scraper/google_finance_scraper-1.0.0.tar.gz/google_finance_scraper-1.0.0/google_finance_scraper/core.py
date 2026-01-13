import aiohttp
import asyncio
import random
import re
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd

# ===================== PANDAS DISPLAY SETTINGS =====================

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 160)
pd.set_option("display.max_colwidth", 60)

# ===================== CONFIG =====================

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/118.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/120.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; Mobile) Chrome/118.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) Chrome/118.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) Chrome/119.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Firefox/118.0",
]

# ===================== UTILITIES =====================

def truncate_text(text, max_len=60):
    if pd.isna(text):
        return text
    text = str(text)
    return text if len(text) <= max_len else text[:max_len - 3] + "..."

def parse_price(text):
    """
    Extract numeric value from:
    ₹3,245.70 | $271.01 | 83.25 | €102.4
    """
    if not text:
        return None
    match = re.search(r"[-+]?[0-9]*\.?[0-9]+", text.replace(",", ""))
    return float(match.group()) if match else None

# ===================== STOCK DATA FUNCTION =====================

async def get_stock_data(symbol: str) -> pd.DataFrame:
    """
    Fetch stock/forex/crypto data from Google Finance
    symbol examples:
    TCS:NSE | AAPL:NASDAQ | TSLA:NASDAQ | USD-INR | BTC-USD
    """
    url = f"https://www.google.com/finance/quote/{symbol}"
    headers = {"User-Agent": random.choice(USER_AGENTS)}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, timeout=10) as r:
            html = await r.text()
            soup = BeautifulSoup(html, "html.parser")

            name_el = soup.find("div", class_="zzDege")
            name = name_el.get_text(strip=True) if name_el else symbol

            price_el = soup.find("div", class_="YMlKec fxKbKc")
            if not price_el:
                return pd.DataFrame()

            live_price = parse_price(price_el.text)

            values = [v.get_text(strip=True) for v in soup.find_all("div", class_="P6K39c")]

            opening_price = parse_price(values[0]) if len(values) > 0 else live_price

            low_price, high_price = opening_price, live_price
            if len(values) > 1 and "-" in values[1]:
                low, high = values[1].split("-")
                low_price = parse_price(low)
                high_price = parse_price(high)

            change_price = (
                live_price - opening_price
                if live_price is not None and opening_price is not None
                else 0
            )

            percent_change = (
                (change_price / opening_price) * 100
                if opening_price not in (0, None)
                else 0
            )

            trend = (
                "bullish" if change_price > 0
                else "bearish" if change_price < 0
                else "neutral"
            )

            stock_dict = {
                "name": name,
                "symbol": symbol,
                "live_price": live_price,
                "live_price_raw": price_el.text.strip(),
                "change_price": change_price,
                "percent_change": percent_change,
                "trend": trend,
                "opening_price": opening_price,
                "closing_price": opening_price,
                "low": low_price,
                "high": high_price,
                "day_range": values[1] if len(values) > 1 else "N/A",
                "volume": values[4] if len(values) > 4 else "N/A",
                "market_cap": values[3] if len(values) > 3 else "N/A",
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            return pd.DataFrame([stock_dict])

# ===================== NEWS FUNCTION =====================

async def get_stock_news(symbol: str) -> pd.DataFrame:
    """
    Fetch ALL available news for a symbol
    """
    url = f"https://www.google.com/finance/quote/{symbol}"
    headers = {"User-Agent": random.choice(USER_AGENTS)}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, timeout=10) as r:
            html = await r.text()
            soup = BeautifulSoup(html, "html.parser")

            news_items = []
            cards = soup.find_all("div", class_="yY3Lee")

            for card in cards:
                headline_elem = card.find("div", class_="Yfwt5")
                source_elem = card.find("div", class_="sfyJob")
                time_elem = card.find("div", class_="Adak")
                link_elem = card.find("a", href=True)

                if not headline_elem:
                    continue

                headline = headline_elem.get_text(strip=True)

                url_link = ""
                if link_elem:
                    href = link_elem["href"]
                    if href.startswith("./"):
                        url_link = "https://www.google.com" + href[1:]
                    elif href.startswith("/"):
                        url_link = "https://www.google.com" + href
                    else:
                        url_link = href

                snippet_elem = card.find("div", class_="AoCdqe")
                snippet = (
                    snippet_elem.get_text(strip=True)
                    if snippet_elem
                    else f"Latest news about {symbol}: {headline}"
                )

                news_items.append({
                    "headline": headline,
                    "source": source_elem.get_text(strip=True) if source_elem else "Financial News",
                    "time": time_elem.get_text(strip=True) if time_elem else "Recent",
                    "snippet": snippet,
                    "url": url_link
                })

            news_df = pd.DataFrame(news_items)

            if not news_df.empty:
                news_df["headline"] = news_df["headline"].apply(lambda x: truncate_text(x, 70))
                news_df["snippet"] = news_df["snippet"].apply(lambda x: truncate_text(x, 80))
                news_df["url"] = news_df["url"].apply(lambda x: truncate_text(x, 60))

            return news_df

