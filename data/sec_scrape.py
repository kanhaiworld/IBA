# module for scraping data from the SEC website

import requests
import pandas as pd

HEADERS = {'User-Agent': "kanhai.wadekar@gmail.com"}

# Key IB metrics with fallback XBRL tags (companies use different tag names)
METRICS = {
    "revenue": [
        ("us-gaap", "Revenues", "USD"),
        ("us-gaap", "RevenueFromContractWithCustomerExcludingAssessedTax", "USD"),
        ("us-gaap", "SalesRevenueNet", "USD"),
    ],
    "net_income": [
        ("us-gaap", "NetIncomeLoss", "USD"),
    ],
    "operating_income": [
        ("us-gaap", "OperatingIncomeLoss", "USD"),
    ],
    "gross_profit": [
        ("us-gaap", "GrossProfit", "USD"),
    ],
    "total_assets": [
        ("us-gaap", "Assets", "USD"),
    ],
    "total_liabilities": [
        ("us-gaap", "Liabilities", "USD"),
    ],
    "cash": [
        ("us-gaap", "CashAndCashEquivalentsAtCarryingValue", "USD"),
        ("us-gaap", "CashAndCashEquivalents", "USD"),
    ],
    "long_term_debt": [
        ("us-gaap", "LongTermDebt", "USD"),
        ("us-gaap", "LongTermDebtNoncurrent", "USD"),
    ],
    "operating_cash_flow": [
        ("us-gaap", "NetCashProvidedByUsedInOperatingActivities", "USD"),
    ],
    "capex": [
        ("us-gaap", "PaymentsToAcquirePropertyPlantAndEquipment", "USD"),
    ],
    "shares_outstanding": [
        ("dei", "EntityCommonStockSharesOutstanding", "shares"),
    ],
}


def get_cik_from_ticker(ticker):
    """
    Get the CIK value for a given company.

    Args:
        ticker (str): The stock ticker symbol of the company.

    Returns:
        str: The 10-digit CIK value, or None if not found.
    """
    url = "https://www.sec.gov/files/company_tickers.json"
    try:
        ticker = ticker.replace(".", "-").upper()
        cik_json = requests.get(url, headers=HEADERS).json()
        for item in cik_json.values():
            if item["ticker"] == ticker:
                return str(item["cik_str"]).zfill(10)
        raise ValueError(f"Ticker {ticker} not found in SEC database.")
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def extract_financial_metric(data, taxonomy, tag, unit="USD"):
    """
    Extract a single financial metric from raw SEC XBRL company facts data.

    Args:
        data (dict): Raw JSON response from the SEC XBRL companyfacts endpoint.
        taxonomy (str): XBRL taxonomy — either "us-gaap" or "dei".
        tag (str): The XBRL tag name (e.g. "Revenues", "NetIncomeLoss").
        unit (str): Unit type — "USD" for dollar amounts, "shares" for share counts.

    Returns:
        pd.DataFrame: Annual 10-K observations with columns [date, fiscal_year, <tag>],
                      or an empty DataFrame if the tag is not found.
    """
    try:
        observations = data["facts"][taxonomy][tag]["units"][unit]
        df = pd.DataFrame(observations)

        df = df[df["form"] == "10-K"]
        df = df[df["fp"] == "FY"]

        df = df.rename(columns={"end": "date", "val": tag, "fy": "fiscal_year"})
        df = df[["date", "fiscal_year", tag]]

        # keep the latest filing per fiscal year in case of amendments
        df = df.sort_values("date").drop_duplicates(subset=["fiscal_year"], keep="last")

        return df.reset_index(drop=True)

    except KeyError:
        return pd.DataFrame()
    except Exception as e:
        print(f"Error extracting {taxonomy}/{tag}: {e}")
        return pd.DataFrame()


def get_company_financials(cik):
    """
    Get key financial statement data for a company using its CIK.

    Pulls annual 10-K data for:
        Income statement: revenue, gross_profit, operating_income, net_income
        Balance sheet:    total_assets, total_liabilities, cash, long_term_debt
        Cash flow:        operating_cash_flow, capex
        Other:            shares_outstanding

    Args:
        cik (str): The 10-digit CIK value of the company.

    Returns:
        pd.DataFrame: One row per fiscal year, one column per metric.
                      Returns an empty DataFrame on failure.
    """
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"

    try:
        data = requests.get(url, headers=HEADERS).json()
    except Exception as e:
        print(f"Failed to fetch data for CIK {cik}: {e}")
        return pd.DataFrame()

    combined = None

    for metric_name, candidates in METRICS.items():
        for taxonomy, tag, unit in candidates:
            df = extract_financial_metric(data, taxonomy, tag, unit)
            if not df.empty:
                df = df.rename(columns={tag: metric_name})[["fiscal_year", metric_name]]
                combined = df if combined is None else combined.merge(df, on="fiscal_year", how="outer")
                break  # use first tag that returns data, ignore fallbacks

    if combined is None:
        return pd.DataFrame()

    return combined.sort_values("fiscal_year").reset_index(drop=True)


def get_financials_for_ticker(ticker):
    """
    Convenience wrapper — look up CIK from ticker and return financials.

    Args:
        ticker (str): Stock ticker symbol (e.g. "AAPL", "MSFT").

    Returns:
        pd.DataFrame: Annual financials, or an empty DataFrame on failure.
    """
    cik = get_cik_from_ticker(ticker)
    if cik is None:
        return pd.DataFrame()
    return get_company_financials(cik)