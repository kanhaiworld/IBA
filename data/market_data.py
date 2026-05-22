import os
import requests
import pandas as pd
from dotenv import load_dotenv
from .sec_scrape import get_financials_for_ticker

load_dotenv()
TIINGO_API_KEY = os.getenv("TIINGO_API_KEY")


def get_latest_price(ticker):
    """
    Fetch the most recent closing price for a ticker from Tiingo.

    Args:
        ticker (str): Stock ticker symbol (e.g. "AAPL").

    Returns:
        float: Latest closing price, or None if unavailable.
    """
    try:
        url = f"https://api.tiingo.com/tiingo/daily/{ticker.lower()}/prices"
        response = requests.get(url, headers={"Authorization": f"Token {TIINGO_API_KEY}"})
        response.raise_for_status()
        data = response.json()
        if not data:
            return None
        return float(data[0]["close"])
    except Exception as e:
        print(f"Error fetching price for {ticker}: {e}")
        return None


def get_market_data(ticker):
    """
    Compute market data for a given ticker using Tiingo prices and SEC share counts.

    Args:
        ticker (str): Stock ticker symbol (e.g. "AAPL").

    Returns:
        dict: stock_price, shares_outstanding, market_cap.
              Values are None if unavailable.
    """
    stock_price = get_latest_price(ticker)

    financials = get_financials_for_ticker(ticker)
    if financials.empty or "shares_outstanding" not in financials.columns:
        shares = None
    else:
        shares = financials["shares_outstanding"].iloc[-1]
        shares = None if pd.isna(shares) else int(shares)

    market_cap = round(stock_price * shares) if stock_price and shares else None

    return {
        "stock_price": stock_price,
        "shares_outstanding": shares,
        "market_cap": market_cap,
    }


def get_enterprise_value(ticker):
    """
    Compute Enterprise Value for a given ticker.

    EV = market_cap + long_term_debt - cash

    Uses Tiingo prices, SEC share counts, and SEC balance sheet data.

    Args:
        ticker (str): Stock ticker symbol (e.g. "AAPL").

    Returns:
        float: Enterprise value in USD, or None if any component is unavailable.
    """
    market_data = get_market_data(ticker)
    financials = get_financials_for_ticker(ticker)

    market_cap = market_data["market_cap"]

    if financials.empty or market_cap is None:
        return None

    long_term_debt = financials["long_term_debt"].iloc[-1]
    cash = financials["cash"].iloc[-1]

    if pd.isna(long_term_debt) or pd.isna(cash):
        return None

    return market_cap + long_term_debt - cash


if __name__ == "__main__":
    print("--- Market Data ---")
    print(get_market_data("AAPL"))

    print("\n--- Enterprise Value ---")
    ev = get_enterprise_value("AAPL")
    if ev:
        print(f"AAPL EV: ${ev:,.0f}")
    else:
        print("AAPL EV: unavailable")