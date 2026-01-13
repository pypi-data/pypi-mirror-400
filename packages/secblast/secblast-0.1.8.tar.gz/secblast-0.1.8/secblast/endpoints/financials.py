"""Financial data endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, overload

from secblast.models.financials import (
    AllFinancialsResponse,
    BalanceSheet,
    CashFlow,
    FinancialFiling,
    FinancialStatement,
    FinancialStatementTable,
    HistoryResponse,
    IncomeStatement,
    RawXbrlResponse,
)

if TYPE_CHECKING:
    from secblast.client import SecBlastClient


class FinancialsMixin:
    """Financial data API methods."""

    def get_all_financials(
        self: "SecBlastClient",
        cik: str,
        accession_number: str | None = None,
    ) -> AllFinancialsResponse:
        """
        Get all financial statements (balance sheet, income statement, cash flow).

        Args:
            cik: Company CIK number
            accession_number: Specific filing accession number (optional)

        Returns:
            AllFinancialsResponse with all three statements
        """
        params: dict = {"cik": cik}
        if accession_number:
            params["accession_number"] = accession_number

        data = self._request("POST", "/financials", json=params)
        return AllFinancialsResponse.model_validate(data)

    @overload
    def get_balance_sheet(
        self: "SecBlastClient",
        cik: str,
        accession_number: str | None = None,
        *,
        format: Literal["default"] = "default",
    ) -> BalanceSheet: ...

    @overload
    def get_balance_sheet(
        self: "SecBlastClient",
        cik: str,
        accession_number: str | None = None,
        *,
        format: Literal["table"],
    ) -> FinancialStatementTable: ...

    def get_balance_sheet(
        self: "SecBlastClient",
        cik: str,
        accession_number: str | None = None,
        *,
        format: Literal["default", "table"] = "default",
    ) -> BalanceSheet | FinancialStatementTable:
        """
        Get balance sheet data for a company.

        Args:
            cik: Company CIK number
            accession_number: Specific filing accession number (optional)
            format: Response format:
                - "default": Nested structure with line_items containing period values
                - "table": Flat structure with columns and rows for easy table rendering

        Returns:
            BalanceSheet (default format) or FinancialStatementTable (table format)

        Example:
            # Default format with line items
            bs = client.get_balance_sheet("320193")
            print(bs.total_assets)

            # Table format for easy rendering
            bs_table = client.get_balance_sheet("320193", format="table")
            for row in bs_table.rows:
                print(f"{row.label}: {row.values}")
        """
        params: dict = {"cik": cik}
        if accession_number:
            params["accession_number"] = accession_number
        if format == "table":
            params["format"] = "table"

        data = self._request("POST", "/financials/balance-sheet", json=params)

        if format == "table":
            return FinancialStatementTable.model_validate(data)
        return BalanceSheet.model_validate(data)

    @overload
    def get_income_statement(
        self: "SecBlastClient",
        cik: str,
        accession_number: str | None = None,
        *,
        format: Literal["default"] = "default",
    ) -> IncomeStatement: ...

    @overload
    def get_income_statement(
        self: "SecBlastClient",
        cik: str,
        accession_number: str | None = None,
        *,
        format: Literal["table"],
    ) -> FinancialStatementTable: ...

    def get_income_statement(
        self: "SecBlastClient",
        cik: str,
        accession_number: str | None = None,
        *,
        format: Literal["default", "table"] = "default",
    ) -> IncomeStatement | FinancialStatementTable:
        """
        Get income statement data for a company.

        Args:
            cik: Company CIK number
            accession_number: Specific filing accession number (optional)
            format: Response format ("default" or "table")

        Returns:
            IncomeStatement (default format) or FinancialStatementTable (table format)

        Example:
            income = client.get_income_statement("320193")
            print(income.revenue)
            print(income.net_income)
        """
        params: dict = {"cik": cik}
        if accession_number:
            params["accession_number"] = accession_number
        if format == "table":
            params["format"] = "table"

        data = self._request("POST", "/financials/income-statement", json=params)

        if format == "table":
            return FinancialStatementTable.model_validate(data)
        return IncomeStatement.model_validate(data)

    @overload
    def get_cash_flow(
        self: "SecBlastClient",
        cik: str,
        accession_number: str | None = None,
        *,
        format: Literal["default"] = "default",
    ) -> CashFlow: ...

    @overload
    def get_cash_flow(
        self: "SecBlastClient",
        cik: str,
        accession_number: str | None = None,
        *,
        format: Literal["table"],
    ) -> FinancialStatementTable: ...

    def get_cash_flow(
        self: "SecBlastClient",
        cik: str,
        accession_number: str | None = None,
        *,
        format: Literal["default", "table"] = "default",
    ) -> CashFlow | FinancialStatementTable:
        """
        Get cash flow statement data for a company.

        Args:
            cik: Company CIK number
            accession_number: Specific filing accession number (optional)
            format: Response format ("default" or "table")

        Returns:
            CashFlow (default format) or FinancialStatementTable (table format)

        Example:
            cf = client.get_cash_flow("320193")
            operating = cf.get_value("NetCashProvidedByUsedInOperatingActivities")
        """
        params: dict = {"cik": cik}
        if accession_number:
            params["accession_number"] = accession_number
        if format == "table":
            params["format"] = "table"

        data = self._request("POST", "/financials/cash-flow", json=params)

        if format == "table":
            return FinancialStatementTable.model_validate(data)
        return CashFlow.model_validate(data)

    def get_raw_financials(
        self: "SecBlastClient",
        cik: str,
        accession_number: str | None = None,
    ) -> RawXbrlResponse:
        """
        Get raw XBRL data organized by statement type.

        Returns complete raw XBRL data for a filing, useful for advanced analysis
        or when you need data not included in the structured statement endpoints.

        Args:
            cik: Company CIK number
            accession_number: Specific filing accession number (optional)

        Returns:
            RawXbrlResponse with complete XBRL facts organized by statement type
        """
        params: dict = {"cik": cik}
        if accession_number:
            params["accession_number"] = accession_number

        data = self._request("POST", "/financials/raw", json=params)
        return RawXbrlResponse.model_validate(data)

    def list_financial_filings(
        self: "SecBlastClient",
        cik: str,
    ) -> list[FinancialFiling]:
        """
        List available 10-K/10-Q filings with processed XBRL data.

        Use this to discover which filings are available before requesting
        specific statements.

        Args:
            cik: Company CIK number

        Returns:
            List of financial filings

        Example:
            filings = client.list_financial_filings("320193")
            for f in filings:
                print(f"{f.form_type} - {f.filing_date} - {f.accession_number}")
        """
        data = self._request("POST", "/financials/filings", json={"cik": cik})
        filings_data = data.get("filings", [])
        return [FinancialFiling.model_validate(f) for f in filings_data]

    def get_financial_history(
        self: "SecBlastClient",
        cik: str,
        concepts: list[str],
    ) -> HistoryResponse:
        """
        Get historical values for XBRL concepts across all available filings.

        Use this endpoint to chart financial metrics over time.

        Common concepts include:
        - Assets: Total assets
        - Liabilities: Total liabilities
        - StockholdersEquity: Total stockholders' equity
        - RevenueFromContractWithCustomerExcludingAssessedTax: Revenue
        - NetIncomeLoss: Net income
        - EarningsPerShareBasic: Basic EPS
        - EarningsPerShareDiluted: Diluted EPS

        Args:
            cik: Company CIK number
            concepts: List of XBRL concept names

        Returns:
            HistoryResponse with values across time for each concept

        Example:
            history = client.get_financial_history(
                "320193",
                ["Assets", "NetIncomeLoss", "RevenueFromContractWithCustomerExcludingAssessedTax"]
            )
            for concept, values in history.concepts.items():
                print(f"{concept}:")
                for v in values:
                    print(f"  {v.period_end}: {v.value:,.0f}")
        """
        concepts_str = ",".join(concepts)
        data = self._request(
            "POST",
            "/financials/history",
            json={"cik": cik, "concepts": concepts_str},
        )
        return HistoryResponse.model_validate(data)

    def export_financials_excel(
        self: "SecBlastClient",
        cik: str,
        accession_number: str | None = None,
    ) -> bytes:
        """
        Export financial data to Excel format (.xlsx).

        Includes balance sheet, income statement, and cash flow data.

        Args:
            cik: Company CIK number
            accession_number: Specific filing accession number (optional)

        Returns:
            Excel file binary data (.xlsx)

        Example:
            excel_data = client.export_financials_excel("320193")
            with open("apple_financials.xlsx", "wb") as f:
                f.write(excel_data)
        """
        params: dict = {"cik": cik}
        if accession_number:
            params["accession_number"] = accession_number

        return self._request_raw(
            "POST",
            "/financials/export/excel",
            json=params,
        )
