import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

config = {
    "FMP_API_KEY": os.getenv("FMP_API_KEY"),
    "REDIS_URL": os.getenv("REDIS_URL")
}

FMP_STOCKS_SEARCH = {
    "search": "https://financialmodelingprep.com/stable/search-name"
}
FMP_FINANCIALS = {
    "balance_sheet": "https://financialmodelingprep.com/stable/balance-sheet-statement",
    "income_statement": "https://financialmodelingprep.com/stable/income-statement",
    "cash_flow": "https://financialmodelingprep.com/stable/cash-flow-statement",
}
FMP_MARKET = {
    "market_cap": "https://financialmodelingprep.com/stable/market-capitalization",
    "profile": "https://financialmodelingprep.com/stable/profile",
}

FMP_GROWTH = {
    "income_growth": "https://financialmodelingprep.com/stable/income-statement-growth",
    "balance_sheet_growth": "https://financialmodelingprep.com/stable/balance-sheet-statement-growth?",
    "cash_flow_growth": "https://financialmodelingprep.com/stable/cash-flow-statement-growth?",
    "financial_growth": "https://financialmodelingprep.com/stable/financial-growth?",
}
FMP_RATIOS = {
    "ratios": "https://financialmodelingprep.com/stable/ratios",
    "key_metrics": "https://financialmodelingprep.com/stable/key-metrics",
}
FMP_COMPANY = {
    "profile": "https://financialmodelingprep.com/stable/profile",
}
REDIS_URL = os.getenv("REDIS_URL")