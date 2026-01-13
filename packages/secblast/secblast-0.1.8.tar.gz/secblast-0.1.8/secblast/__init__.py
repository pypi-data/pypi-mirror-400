"""
SecBlast - Python SDK for the SecBlast SEC Filing API.

Example:
    ```python
    from secblast import SecBlastClient

    client = SecBlastClient(api_key="your-api-key")

    # Look up a company
    entity = client.get_entity(ticker="AAPL")

    # Search filings
    filings = client.lookup_filings(
        tickers=["AAPL"],
        form_types=["10-K"],
    )

    # Full-text search
    results = client.fulltext_search("material contract")

    # Get financial data
    balance_sheet = client.get_balance_sheet(cik="320193")

    # Get financial data in table format for easy rendering
    balance_table = client.get_balance_sheet(cik="320193", format="table")
    for row in balance_table.rows:
        print(f"{row.label}: {row.values}")
    ```
"""

from secblast.async_client import AsyncSecBlastClient
from secblast.client import SecBlastClient
from secblast.exceptions import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    SecBlastError,
    ServerError,
    ValidationError,
)
from secblast.models import (
    Address,
    AllFinancialsResponse,
    BalanceSheet,
    CashFlow,
    DocumentInfo,
    EntityInfo,
    FactValue,
    FilingInfo,
    FinancialFiling,
    FinancialStatement,
    FinancialStatementTable,
    FormerName,
    HistoricalValue,
    HistoryResponse,
    IncomeStatement,
    Item8K,
    LineItem,
    Period,
    RawFact,
    RawStatement,
    RawXbrlResponse,
    SearchHit,
    SearchResult,
    Section,
    TableRow,
    XBRLFact,
)

__version__ = "0.2.0"

__all__ = [
    # Client
    "SecBlastClient",
    "AsyncSecBlastClient",
    # Exceptions
    "SecBlastError",
    "AuthenticationError",
    "RateLimitError",
    "ValidationError",
    "NotFoundError",
    "ServerError",
    # Models - Entity
    "EntityInfo",
    "Address",
    "FormerName",
    # Models - Filing
    "FilingInfo",
    "DocumentInfo",
    "Item8K",
    "Section",
    # Models - Search
    "SearchHit",
    "SearchResult",
    # Models - Financials (Statements)
    "FinancialStatement",
    "FinancialStatementTable",
    "BalanceSheet",
    "IncomeStatement",
    "CashFlow",
    "AllFinancialsResponse",
    # Models - Financials (Components)
    "Period",
    "FactValue",
    "LineItem",
    "TableRow",
    "FinancialFiling",
    "XBRLFact",
    # Models - Financials (History)
    "HistoricalValue",
    "HistoryResponse",
    # Models - Financials (Raw)
    "RawFact",
    "RawStatement",
    "RawXbrlResponse",
]
