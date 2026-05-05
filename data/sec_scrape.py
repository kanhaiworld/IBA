# module for scraping data  from the SEC website 

import requests 
import pandas as pd 

#
# Create a requests header - basically define User-Agent and an email 
#
HEADERS = {'User-Agent': "kanhai.wadekar@gmail.com"}

def get_cik_from_ticker(ticker): 
    """
    Get the CIK value for a given compny. 

    Args: 
        ticker (str): The stock ticker symbol of the company.
    
    Returns:
        str: The CIK value associated with the given ticker symbol.
    """
    url = f"https://www.sec.gov/files/company_tickers.json" 

    try: 
        # some tickers have a dot, replace with dash 
        ticker = ticker.replace(".", "-").upper()

        cik_json = requests.get(url, headers=HEADERS).json()    

        for item in cik_json.values(): 
            if item["ticker"] == ticker: 
                # cik has to be 10 digits so pad with leading zeros 
                cik = str(item["cik_str"]).zfill(10) 
                return cik
        
        raise ValueError(f"Ticker {ticker} not found in SEC database.")

    except Exception as e: 
        print(f"An error occurred: {e}")
        return pd.DataFrame() # return empty dataframe if error occurs

def extract_financial_metric(data, taxonomy, tag, unit="USD"):
    try: 
        shares = data["facts"]["dei"]["EntityCommonStockSharesOutstanding"]["units"]["shares"] # list of dictionaries
        df = pd.DataFrame(shares)
        # print(df.head())
        
        # only want the annual numbers (10-K FY)
        df = df[df["form"] == "10-K"]
        df = df[df["fp"] == "FY"]

        # rename columns for clarity 
        df = df.rename(columsns={
            "end": "date",
            "val": "shares_outstanding",
            "fy": "fiscal_year"
        })

        # keep date, fiscal year and shares outstanding columns 
        df = df[["date", "fiscal_year", "shares_outstanding"]]
        df = df.sort_values("date")

        return df

    except Exception as e:
        print(f"An error occurred: {e}")
        return pd.DataFrame() # return empty dataframe if error occurs


def get_company_financials(cik): 
    """
    Get the financial data for a given company using its CIK value. 
    Datapoints include: 
        - Revenue
        - Net income
        - Assets
        - Liabilities
        - Cash flow items
        - Shares outstanding
        - Quarterly + annual history

    facts
        ├── us-gaap (financial statements)
        ├── dei (company info / shares / etc)
    
    Financial metrics follow this shape: 
    facts
    └── taxonomy (us-gaap / dei)
        └── metric name (Revenue, NetIncome, Assets...)
            └── units (USD, shares, etc)
                    └── list of observations over time    

    Parameters: 
        cik (str): The CIK value of the company.
    
    Returns:
        pd.DataFrame: A DataFrame containing the financial data for the company.
    """

    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"

    try: 
        data = requests.get(url, headers=HEADERS).json() 
        
        shares = data["facts"]["dei"]["EntityCommonStockSharesOutstanding"]["units"]["shares"] # list of dictionaries
        df = pd.DataFrame(shares)
        # print(df.head())
        
        # only want the annual numbers (10-K FY)
        df = df[df["form"] == "10-K"]
        df = df[df["fp"] == "FY"]

        # rename columns for clarity 
        df = df.rename(columsns={
            "end": "date",
            "val": "shares_outstanding",
            "fy": "fiscal_year"
        })

        # keep date, fiscal year and shares outstanding columns 
        df = df[["date", "fiscal_year", "shares_outstanding"]]
        df = df.sort_values("date")

        return df

    except Exception as e: 
        print(f"An error occurred: {e}")    
        return pd.DataFrame() # return empty dataframe if error occurs