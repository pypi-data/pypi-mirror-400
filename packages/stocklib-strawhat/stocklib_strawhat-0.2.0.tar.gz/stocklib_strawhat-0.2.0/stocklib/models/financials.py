from pydantic import BaseModel, Field
from typing import Literal

class IncomeStatement(BaseModel):
    revenue: float = Field(description="Total revenue")
    gross_profit: float = Field(description="Gross profit (revenue minus cost of goods sold)")
    operating_income: float = Field(description="Operating income (EBIT)")
    net_income: float = Field(description="Net income (profit after all expenses)")
    eps: float = Field(description="Earnings per share")


class BalanceSheet(BaseModel):
    total_assets: float = Field(description="Total assets")
    total_liabilities: float = Field(description="Total liabilities")
    total_equity: float = Field(description="Total equity (assets minus liabilities)")
    cash_and_equivalents: float = Field(description="Cash and cash equivalents")
    total_debt: float = Field(description="Total debt")


class CashFlow(BaseModel):
    operating_cash_flow: float = Field(description="Cash flow from operations")
    free_cash_flow: float = Field(description="Free cash flow (operating cash flow minus capital expenditure)")
    capital_expenditure: float = Field(description="Capital expenditure (CAPEX)")


class FinancialsMetadata(BaseModel):
    fiscal_year: int = Field(description="Fiscal year")
    period: Literal["Q1", "Q2", "Q3", "Q4", "FY"] = Field(description="Reporting period (quarter or full year)")


class Financials(BaseModel):
    income_statement: IncomeStatement = Field(description="Income statement data")
    balance_sheet: BalanceSheet = Field(description="Balance sheet data")
    cash_flow: CashFlow = Field(description="Cash flow statement data")
    metadata: FinancialsMetadata = Field(description="Financials metadata")
