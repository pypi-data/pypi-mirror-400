"""SecBlast async API client."""

from __future__ import annotations

from datetime import date
from typing import Any, Literal, overload

import httpx

from secblast.endpoints.documents import DocumentContent
from secblast.endpoints.entities import EntityLookupResult
from secblast.endpoints.filings import FilingLookupResult
from secblast.endpoints.search import QueryType
from secblast.exceptions import (
    AuthenticationError,
    RateLimitError,
    SecBlastError,
    ServerError,
    ValidationError,
)
from secblast.models import (
    BalanceSheet,
    CashFlow,
    EntityInfo,
    FinancialFiling,
    IncomeStatement,
    Item8K,
    SearchResult,
    Section,
)
from secblast.models.filing import FilingDetail
from secblast.models.financials import (
    AllFinancialsResponse,
    FinancialStatementTable,
    HistoryResponse,
    RawXbrlResponse,
)

DEFAULT_BASE_URL = "https://api.secblast.com/v2"
DEFAULT_TIMEOUT = 60.0


class AsyncSecBlastClient:
    """
    Async SecBlast API client for accessing SEC filing data.

    Example:
        ```python
        import asyncio
        from secblast import AsyncSecBlastClient

        async def main():
            async with AsyncSecBlastClient(api_key="your-api-key") as client:
                entity = await client.get_entity(ticker="AAPL")
                print(entity.name)

        asyncio.run(main())
        ```
    """

    def __init__(
        self,
        api_key: str,
        *,
        timeout: float = DEFAULT_TIMEOUT,
        http_client: httpx.AsyncClient | None = None,
    ):
        """
        Initialize the async SecBlast client.

        Args:
            api_key: Your SecBlast API key
            timeout: Request timeout in seconds
            http_client: Custom httpx.AsyncClient instance
        """
        self.api_key = api_key
        self.base_url = DEFAULT_BASE_URL
        self.timeout = timeout

        if http_client is not None:
            self._client = http_client
            self._owns_client = False
        else:
            self._client = httpx.AsyncClient(timeout=timeout)
            self._owns_client = True

    async def __aenter__(self) -> "AsyncSecBlastClient":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._owns_client:
            await self._client.aclose()

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json: dict | None = None,
    ) -> dict:
        """Make an async API request and return JSON response."""
        url = f"{self.base_url}{path}"

        body = {"api_key": self.api_key}
        if json:
            body.update(json)

        response = await self._client.request(method, url, json=body)
        return self._handle_response(response)

    async def _request_raw(
        self,
        method: str,
        path: str,
        *,
        json: dict | None = None,
    ) -> bytes:
        """Make an async API request and return raw bytes."""
        url = f"{self.base_url}{path}"

        body = {"api_key": self.api_key}
        if json:
            body.update(json)

        response = await self._client.request(method, url, json=body)

        if response.status_code >= 400:
            self._handle_error(response)

        return response.content

    def _handle_response(self, response: httpx.Response) -> dict:
        """Handle API response and raise appropriate exceptions."""
        if response.status_code >= 400:
            self._handle_error(response)

        try:
            return response.json()
        except Exception as e:
            raise SecBlastError(f"Failed to parse response: {e}")

    def _handle_error(self, response: httpx.Response) -> None:
        """Raise appropriate exception based on response status."""
        try:
            data = response.json()
            message = data.get("error", str(data))
        except Exception:
            message = response.text or f"HTTP {response.status_code}"

        status = response.status_code

        if status == 401:
            raise AuthenticationError(message)
        elif status == 429:
            limit_type = "bandwidth" if "byte" in message.lower() else "requests"
            raise RateLimitError(message, limit_type=limit_type)
        elif status == 400:
            raise ValidationError(message)
        elif status >= 500:
            raise ServerError(message, status_code=status)
        else:
            raise SecBlastError(message, status_code=status)

    # ==================== Entity Methods ====================

    async def lookup_entities(
        self,
        *,
        ciks: list[str] | None = None,
        tickers: list[str] | None = None,
        index_tickers: list[str] | None = None,
        exchanges: list[str] | None = None,
        entity_types: list[str] | None = None,
        name_includes: list[str] | None = None,
        name_excludes: list[str] | None = None,
        sics: list[str] | None = None,
        states: list[str] | None = None,
        eins: list[str] | None = None,
        from_: int = 0,
        to: int = 100,
    ) -> EntityLookupResult:
        """Search for SEC entities (companies, filers)."""
        # Note: entity_lookup takes params at top level (no entity_query wrapper)
        params: dict = {}
        if ciks:
            params["ciks"] = ciks
        if tickers:
            params["tickers"] = tickers
        if index_tickers:
            params["index_tickers"] = index_tickers
        if exchanges:
            params["exchanges"] = exchanges
        if entity_types:
            params["entity_types"] = entity_types
        if name_includes:
            params["name_includes"] = name_includes
        if name_excludes:
            params["name_excludes"] = name_excludes
        if sics:
            params["sics"] = sics
        if states:
            params["states"] = states
        if eins:
            params["eins"] = eins
        if from_ != 0:
            params["from"] = from_
        if to != 100:
            params["to"] = to

        data = await self._request("POST", "/entity_lookup", json=params)
        return EntityLookupResult.model_validate(data)

    async def get_entity(
        self,
        *,
        cik: str | None = None,
        ticker: str | None = None,
    ) -> EntityInfo | None:
        """Get a single entity by CIK or ticker."""
        if not cik and not ticker:
            raise ValueError("Must provide either cik or ticker")

        result = await self.lookup_entities(
            ciks=[cik] if cik else None,
            tickers=[ticker] if ticker else None,
            to=1,
        )
        return result.entities[0] if result.entities else None

    # ==================== Filing Methods ====================

    async def lookup_filings(
        self,
        *,
        ciks: list[str] | None = None,
        tickers: list[str] | None = None,
        exchanges: list[str] | None = None,
        sics: list[str] | None = None,
        states: list[str] | None = None,
        form_types: list[str] | None = None,
        excluded_form_types: list[str] | None = None,
        date_from: date | str | None = None,
        date_to: date | str | None = None,
        items: list[str] | None = None,
        exclude_amendments: bool = False,
        sort_by: str | None = None,
        sort_order: str = "desc",
        from_: int = 0,
        to: int = 100,
    ) -> FilingLookupResult:
        """Search for SEC filings."""
        params: dict = {}

        # Entity filters at top level
        if ciks:
            params["ciks"] = ciks
        if tickers:
            params["tickers"] = tickers
        if exchanges:
            params["exchanges"] = exchanges
        if sics:
            params["sics"] = sics
        if states:
            params["states"] = states

        if form_types:
            params["form_types"] = form_types
        if excluded_form_types:
            params["excluded_form_types"] = excluded_form_types
        if date_from:
            params["date_from"] = str(date_from)
        if date_to:
            params["date_to"] = str(date_to)
        if items:
            params["items"] = items
        if exclude_amendments:
            params["exclude_amendments"] = True
        if sort_by:
            params["sort_by"] = sort_by
        if sort_order != "desc":
            params["sort_order"] = sort_order
        if from_ != 0:
            params["from"] = from_
        if to != 100:
            params["to"] = to

        data = await self._request("POST", "/filing_lookup", json=params)
        return FilingLookupResult.model_validate(data)

    async def get_filing_info(self, accession_number: str) -> FilingDetail:
        """Get detailed information about a filing."""
        data = await self._request(
            "POST",
            "/filing_info",
            json={"accession_number": accession_number},
        )
        return FilingDetail.model_validate(data)

    async def get_filing_sections(
        self,
        document_id: str,
        form_type: str = "10-K",
    ) -> list[Section]:
        """Get sections with HTML content for a 10-K or 10-Q filing."""
        data = await self._request(
            "POST",
            "/filing_sections",
            json={"document_id": document_id, "form_type": form_type},
        )
        return [Section.model_validate(s) for s in data.get("sections", [])]

    async def get_8k_items(
        self,
        accession_numbers: list[str],
    ) -> dict[str, list[Item8K]]:
        """Batch fetch 8-K items for multiple filings."""
        if len(accession_numbers) > 100:
            raise ValueError("Maximum 100 accession numbers per request")

        data = await self._request(
            "POST",
            "/8k_items",
            json={"accession_numbers": accession_numbers},
        )

        result: dict[str, list[Item8K]] = {}
        for acc_num, items in data.items():
            if isinstance(items, list):
                result[acc_num] = [Item8K.model_validate(item) for item in items]
        return result

    # ==================== Search Methods ====================

    async def fulltext_search(
        self,
        query: str,
        *,
        query_type: QueryType | Literal["match", "match_phrase", "query_string"] = QueryType.MATCH,
        ciks: list[str] | None = None,
        form_types: list[str] | None = None,
        accession_numbers: list[str] | None = None,
        date_from: date | str | None = None,
        date_to: date | str | None = None,
        sort_by: Literal["filing_date", "_score"] = "filing_date",
        sort_order: Literal["asc", "desc"] = "desc",
        from_: int = 0,
        to: int = 100,
    ) -> SearchResult:
        """Full-text search across SEC documents."""
        params: dict = {"query": query}

        if isinstance(query_type, QueryType):
            query_type = query_type.value
        if query_type != "match":
            params["query_type"] = query_type

        if ciks:
            params["ciks"] = ciks
        if form_types:
            params["form_types"] = form_types
        if accession_numbers:
            params["accession_numbers"] = accession_numbers
        if date_from:
            params["date_from"] = str(date_from)
        if date_to:
            params["date_to"] = str(date_to)
        if sort_by != "filing_date":
            params["sort_by"] = sort_by
        if sort_order != "desc":
            params["sort_order"] = sort_order
        if from_ != 0:
            params["from"] = from_
        if to != 100:
            params["to"] = to

        data = await self._request("POST", "/fulltext_search", json=params)
        return SearchResult.model_validate(data)

    # ==================== Document Methods ====================

    @overload
    async def get_document(
        self,
        document_id: str,
        *,
        output_format: Literal["raw"] = "raw",
        convert_xml_to_json: bool = False,
    ) -> bytes: ...

    @overload
    async def get_document(
        self,
        document_id: str,
        *,
        output_format: Literal["json"],
        convert_xml_to_json: bool = False,
    ) -> DocumentContent: ...

    async def get_document(
        self,
        document_id: str,
        *,
        output_format: Literal["raw", "json"] = "raw",
        convert_xml_to_json: bool = False,
    ) -> bytes | DocumentContent:
        """Fetch a document by ID."""
        params: dict = {"document_id": document_id}

        if output_format == "json":
            params["output_format"] = "json"
            if convert_xml_to_json:
                params["convert_xml_to_json"] = True
            data = await self._request("POST", "/document", json=params)
            return DocumentContent.model_validate(data)
        else:
            return await self._request_raw("POST", "/document", json=params)

    async def get_pdf(
        self,
        *,
        document_id: str | None = None,
        accession_number: str | None = None,
    ) -> bytes:
        """Generate a PDF from a document or entire filing."""
        if document_id and accession_number:
            raise ValueError("Provide either document_id or accession_number, not both")
        if not document_id and not accession_number:
            raise ValueError("Must provide either document_id or accession_number")

        params: dict = {}
        if document_id:
            params["document_id"] = document_id
        else:
            params["accession_number"] = accession_number

        return await self._request_raw("POST", "/pdf", json=params)

    # ==================== Financial Methods ====================

    async def get_all_financials(
        self,
        cik: str,
        accession_number: str | None = None,
    ) -> AllFinancialsResponse:
        """Get all financial statements (balance sheet, income statement, cash flow)."""
        params: dict = {"cik": cik}
        if accession_number:
            params["accession_number"] = accession_number
        data = await self._request("POST", "/financials", json=params)
        return AllFinancialsResponse.model_validate(data)

    @overload
    async def get_balance_sheet(
        self,
        cik: str,
        accession_number: str | None = None,
        *,
        format: Literal["default"] = "default",
    ) -> BalanceSheet: ...

    @overload
    async def get_balance_sheet(
        self,
        cik: str,
        accession_number: str | None = None,
        *,
        format: Literal["table"],
    ) -> FinancialStatementTable: ...

    async def get_balance_sheet(
        self,
        cik: str,
        accession_number: str | None = None,
        *,
        format: Literal["default", "table"] = "default",
    ) -> BalanceSheet | FinancialStatementTable:
        """Get balance sheet data for a company."""
        params: dict = {"cik": cik}
        if accession_number:
            params["accession_number"] = accession_number
        if format == "table":
            params["format"] = "table"

        data = await self._request("POST", "/financials/balance-sheet", json=params)

        if format == "table":
            return FinancialStatementTable.model_validate(data)
        return BalanceSheet.model_validate(data)

    @overload
    async def get_income_statement(
        self,
        cik: str,
        accession_number: str | None = None,
        *,
        format: Literal["default"] = "default",
    ) -> IncomeStatement: ...

    @overload
    async def get_income_statement(
        self,
        cik: str,
        accession_number: str | None = None,
        *,
        format: Literal["table"],
    ) -> FinancialStatementTable: ...

    async def get_income_statement(
        self,
        cik: str,
        accession_number: str | None = None,
        *,
        format: Literal["default", "table"] = "default",
    ) -> IncomeStatement | FinancialStatementTable:
        """Get income statement data for a company."""
        params: dict = {"cik": cik}
        if accession_number:
            params["accession_number"] = accession_number
        if format == "table":
            params["format"] = "table"

        data = await self._request("POST", "/financials/income-statement", json=params)

        if format == "table":
            return FinancialStatementTable.model_validate(data)
        return IncomeStatement.model_validate(data)

    @overload
    async def get_cash_flow(
        self,
        cik: str,
        accession_number: str | None = None,
        *,
        format: Literal["default"] = "default",
    ) -> CashFlow: ...

    @overload
    async def get_cash_flow(
        self,
        cik: str,
        accession_number: str | None = None,
        *,
        format: Literal["table"],
    ) -> FinancialStatementTable: ...

    async def get_cash_flow(
        self,
        cik: str,
        accession_number: str | None = None,
        *,
        format: Literal["default", "table"] = "default",
    ) -> CashFlow | FinancialStatementTable:
        """Get cash flow statement data for a company."""
        params: dict = {"cik": cik}
        if accession_number:
            params["accession_number"] = accession_number
        if format == "table":
            params["format"] = "table"

        data = await self._request("POST", "/financials/cash-flow", json=params)

        if format == "table":
            return FinancialStatementTable.model_validate(data)
        return CashFlow.model_validate(data)

    async def get_raw_financials(
        self,
        cik: str,
        accession_number: str | None = None,
    ) -> RawXbrlResponse:
        """Get raw XBRL data organized by statement type."""
        params: dict = {"cik": cik}
        if accession_number:
            params["accession_number"] = accession_number
        data = await self._request("POST", "/financials/raw", json=params)
        return RawXbrlResponse.model_validate(data)

    async def list_financial_filings(self, cik: str) -> list[FinancialFiling]:
        """List available 10-K/10-Q filings for a company."""
        data = await self._request("POST", "/financials/filings", json={"cik": cik})
        return [FinancialFiling.model_validate(f) for f in data.get("filings", [])]

    async def get_financial_history(
        self,
        cik: str,
        concepts: list[str],
    ) -> HistoryResponse:
        """Get historical values for XBRL concepts across filings."""
        concepts_str = ",".join(concepts)
        data = await self._request(
            "POST",
            "/financials/history",
            json={"cik": cik, "concepts": concepts_str},
        )
        return HistoryResponse.model_validate(data)

    async def export_financials_excel(
        self,
        cik: str,
        accession_number: str | None = None,
    ) -> bytes:
        """Export financial data to Excel format."""
        params: dict = {"cik": cik}
        if accession_number:
            params["accession_number"] = accession_number
        return await self._request_raw(
            "POST",
            "/financials/export/excel",
            json=params,
        )

    async def health_check(self) -> bool:
        """Check if the API is healthy."""
        try:
            data = await self._request("GET", "/health")
            return data.get("status") == "ok"
        except Exception:
            return False
