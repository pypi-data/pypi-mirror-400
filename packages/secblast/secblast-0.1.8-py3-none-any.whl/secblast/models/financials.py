"""Financial data models."""

from __future__ import annotations

from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, Field


class XBRLFact(BaseModel):
    """Individual XBRL fact/concept."""

    concept: str
    value: str | float | int | None = None
    unit: str | None = None
    decimals: int | None = None
    start_date: date | None = Field(None, alias="startDate")
    end_date: date | None = Field(None, alias="endDate")
    instant: date | None = None
    segment: dict | None = None

    model_config = {"populate_by_name": True}


class FinancialFiling(BaseModel):
    """Financial filing reference."""

    accession_number: str = Field(alias="accession_number")
    form_type: str = Field(alias="form_type")
    filing_date: date = Field(alias="filing_date")
    period_end: date | None = Field(None, alias="period_end")
    fiscal_year: int | None = Field(None, alias="fiscal_year")
    fiscal_period: str | None = Field(None, alias="fiscal_period")

    model_config = {"populate_by_name": True}


class Period(BaseModel):
    """A reporting period from the XBRL filing."""

    period_end: date
    period_start: date | None = None
    period_type: Literal["instant", "duration"]


class FactValue(BaseModel):
    """A single value for a financial concept at a specific period."""

    period_end: date
    period_start: date | None = None
    value: float | int
    unit: str


class LineItem(BaseModel):
    """A financial line item with its values across periods."""

    concept: str
    label: str
    values: list[FactValue] = []


class TableRow(BaseModel):
    """A row in the table format response."""

    concept: str
    label: str
    values: list[float | int | None] = []
    unit: str


class FinancialStatement(BaseModel):
    """
    A complete financial statement with all line items (default format).

    Line items are ordered by presentation order from the SEC filing.
    """

    cik: str
    accession_number: str
    filing_date: date
    form_type: str
    statement_type: Literal["balance_sheet", "income_statement", "cash_flow"]
    short_name: str | None = None
    periods: list[Period] = []
    line_items: list[LineItem] = []

    def get_value(self, concept: str, period_end: date | str | None = None) -> float | None:
        """
        Get the value for a specific concept and period.

        Args:
            concept: XBRL concept name
            period_end: Specific period end date (uses most recent if not provided)

        Returns:
            The value or None if not found
        """
        for item in self.line_items:
            if item.concept == concept:
                if not item.values:
                    return None
                if period_end is None:
                    return item.values[0].value if item.values else None
                period_str = str(period_end)
                for v in item.values:
                    if str(v.period_end) == period_str:
                        return v.value
        return None

    @property
    def total_assets(self) -> float | None:
        """Total assets value (for balance sheets)."""
        return self.get_value("Assets")

    @property
    def total_liabilities(self) -> float | None:
        """Total liabilities value (for balance sheets)."""
        return self.get_value("Liabilities")

    @property
    def total_equity(self) -> float | None:
        """Total stockholders' equity value (for balance sheets)."""
        return self.get_value("StockholdersEquity")

    @property
    def net_income(self) -> float | None:
        """Net income value (for income statements)."""
        return self.get_value("NetIncomeLoss")

    @property
    def revenue(self) -> float | None:
        """Revenue value (for income statements)."""
        # Try common revenue concepts
        for concept in [
            "RevenueFromContractWithCustomerExcludingAssessedTax",
            "Revenues",
            "SalesRevenueNet",
            "Revenue",
        ]:
            val = self.get_value(concept)
            if val is not None:
                return val
        return None


class FinancialStatementTable(BaseModel):
    """
    A financial statement in table format for easy rendering.

    Columns are period dates, rows are line items with values aligned to columns.
    Rows are ordered by presentation order from the SEC filing.
    """

    cik: str
    accession_number: str
    filing_date: date
    form_type: str
    statement_type: Literal["balance_sheet", "income_statement", "cash_flow"]
    short_name: str | None = None
    columns: list[str] = []  # Period end dates as strings
    rows: list[TableRow] = []

    def get_value(self, concept: str, column_index: int = 0) -> float | None:
        """
        Get the value for a specific concept and column.

        Args:
            concept: XBRL concept name
            column_index: Column index (0 = most recent)

        Returns:
            The value or None if not found
        """
        for row in self.rows:
            if row.concept == concept:
                if column_index < len(row.values):
                    return row.values[column_index]
        return None

    def to_dataframe(self):
        """
        Convert to a pandas DataFrame.

        Returns:
            pandas.DataFrame with concepts as index, periods as columns

        Raises:
            ImportError: If pandas is not installed
        """
        try:
            import pandas as pd
        except ImportError:
            raise ImportError("pandas is required for to_dataframe(). Install with: pip install pandas")

        data = {row.concept: row.values for row in self.rows}
        df = pd.DataFrame(data, index=self.columns).T
        df.columns = self.columns
        return df


class AllFinancialsResponse(BaseModel):
    """Combined response with all three financial statements."""

    cik: str
    balance_sheet: FinancialStatement | None = None
    income_statement: FinancialStatement | None = None
    cash_flow: FinancialStatement | None = None
    filings: list[FinancialFiling] = []


class HistoricalValue(BaseModel):
    """A historical value for a concept."""

    period_end: date
    value: float | int
    filing_date: date
    accession_number: str
    form_type: str


class HistoryResponse(BaseModel):
    """Historical values for requested concepts."""

    cik: str
    concepts: dict[str, list[HistoricalValue]] = {}


class RawFact(BaseModel):
    """A raw XBRL fact value."""

    value: float | int | None = None
    unit: str | None = None
    period_end: date | None = None
    period_start: date | None = None
    decimals: int | None = None


class RawStatement(BaseModel):
    """A statement with raw XBRL facts."""

    role_uri: str | None = None
    short_name: str | None = None
    long_name: str | None = None
    facts: dict[str, list[RawFact]] = {}


class RawXbrlResponse(BaseModel):
    """Complete raw XBRL data for a filing."""

    cik: str
    accession_number: str
    filing_date: date
    form_type: str
    statements: dict[str, list[RawStatement]] = {}


# Legacy aliases for backwards compatibility
class BalanceSheet(FinancialStatement):
    """Balance sheet data (alias for FinancialStatement)."""

    statement_type: Literal["balance_sheet"] = "balance_sheet"


class IncomeStatement(FinancialStatement):
    """Income statement data (alias for FinancialStatement)."""

    statement_type: Literal["income_statement"] = "income_statement"


class CashFlow(FinancialStatement):
    """Cash flow statement data (alias for FinancialStatement)."""

    statement_type: Literal["cash_flow"] = "cash_flow"
