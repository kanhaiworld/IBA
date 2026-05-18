import time
import yfinance as yf
import pandas as pd
from sec_scrape import get_financials_for_ticker



def _get_yf_ticker(ticker, retries=3, delay=3):
    """
    Fetch ticker and verify it exists using yf.download (much more reliable).
    Avoids Yahoo rate-limiting issues that break Ticker().history().
    """
    for attempt in range(retries):
        try:
            df = yf.download(
                ticker,
                period="5d",        # small request reduces blocking
                progress=False,
                threads=False,      # VERY IMPORTANT: prevents throttling
            )

            if not df.empty:
                return yf.Ticker(ticker)

        except Exception:
            pass

        if attempt < retries - 1:
            time.sleep(delay)

    return None



def get_market_data(ticker):
    """
    Fetch market data from Yahoo Finance using stable endpoints.
    Returns:
        dict: market_cap, stock_price, shares_outstanding, beta
    """
    stock = _get_yf_ticker(ticker)

    if stock is None:
        print(f"Could not fetch market data for {ticker}")
        return {
            "market_cap": None,
            "stock_price": None,
            "shares_outstanding": None,
            "beta": None,
        }

    try:
        price_df = yf.download(
            ticker,
            period="1d",
            progress=False,
            threads=False,
        )
        stock_price = float(price_df["Close"].iloc[-1])
    except Exception:
        stock_price = None

    try:
        shares_series = stock.get_shares_full()
        shares = shares_series.iloc[-1]
    except Exception:
        shares = None

    market_cap = round(stock_price * shares) if stock_price and shares else None

    try:
        beta = stock.info.get("beta")
    except Exception:
        beta = None

    return {
        "market_cap": market_cap,
        "stock_price": stock_price,
        "shares_outstanding": shares,
        "beta": beta,
    }


def get_enterprise_value(ticker):
    """
    EV = Market Cap + Long Term Debt - Cash
    Uses:
        • Live market data (Yahoo)
        • Latest annual balance sheet (SEC)
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
    print("\n--- Market Data ---")
    market_data = get_market_data("MSFT")
    print(market_data)

    print("\n--- Enterprise Value ---")
    ev = get_enterprise_value("MSFT")

    if ev:
        print(f"MSFT EV: ${ev:,.0f}")
    else:
        print("MSFT EV: unavailable")