import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
from data.market_data import get_enterprise_value, get_market_data
from data.sec_scrape import get_financials_for_ticker


def run_comps(target, peers):
    """
    Build a comparable companies table for a target and its peers.

    Args:
        target (str): Ticker for the target company (e.g. "AAPL").
        peers (list[str]): Tickers for peer companies (e.g. ["MSFT", "GOOGL"]).

    Returns:
        pd.DataFrame: One row per company with columns:
                      ticker, ev, revenue, operating_income, net_income,
                      ev_revenue, ev_ebitda_proxy, pe_ratio.
    """
    tickers = [target] + peers
    rows = []

    for ticker in tickers:
        ev = get_enterprise_value(ticker)
        market_data = get_market_data(ticker)
        financials = get_financials_for_ticker(ticker)

        if financials.empty:
            print(f"No financials for {ticker}, skipping.")
            continue

        latest = financials.iloc[-1]
        revenue = latest.get("revenue")
        operating_income = latest.get("operating_income")
        net_income = latest.get("net_income")
        market_cap = market_data["market_cap"]

        rows.append({
            "ticker": ticker,
            "ev": ev,
            "market_cap": market_cap,
            "revenue": revenue,
            "operating_income": operating_income,
            "net_income": net_income,
            "ev_revenue": round(ev / revenue, 2) if ev and revenue else None,
            "ev_ebitda_proxy": round(ev / operating_income, 2) if ev and operating_income else None,
            "pe_ratio": round(market_cap / net_income, 2) if market_cap and net_income else None,
        })

    df = pd.DataFrame(rows).set_index("ticker")
    return df


if __name__ == "__main__":
    df = run_comps("AAPL", ["MSFT", "GOOG", "META"])
    print(df.to_string())
