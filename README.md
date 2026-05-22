# IBA — Investment Banking Automation

Agentic platform to automate the grunt work of junior investment banking analysts. The goal is a system you can interact with to run financial analyses that would otherwise take hours of manual data gathering and Excel work.

## High-Level Goal

Junior IB analysts spend the majority of their time on repetitive, data-heavy tasks: pulling financials from SEC filings, computing trading multiples, building comps tables, and formatting outputs. IBA automates this pipeline — from raw data sourcing through structured financial outputs — so analysts can focus on the judgment-intensive work instead.

## Features

- **Comparable companies (trading comps)** — build a comps table for any target and peer set, with EV/Revenue, EV/EBITDA, and P/E multiples computed automatically
- **Financial data sourcing** — pulls annual 10-K data (income statement, balance sheet, cash flow) directly from SEC EDGAR with no third-party data vendor required
- **Market data** — real-time stock prices, market cap, and enterprise value via Tiingo

## Data Sources

| Source | What it provides | Notes |
|---|---|---|
| [SEC EDGAR XBRL API](https://data.sec.gov/api/xbrl/) | Annual financial statement data
| [Tiingo](https://www.tiingo.com/) | Stock prices 

## Setup

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root:
```
TIINGO_API_KEY=your_key_here
```