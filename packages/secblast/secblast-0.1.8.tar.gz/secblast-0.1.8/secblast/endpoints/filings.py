"""Filing lookup and info endpoints."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from secblast.models.filing import DocumentInfo, FilingDetail, FilingInfo, Item8K, Section

if TYPE_CHECKING:
    from secblast.client import SecBlastClient


class FilingLookupResult(BaseModel):
    """Result from filing lookup."""

    count: int
    truncated: bool = False
    filings: list[FilingInfo] = []


class FilingsMixin:
    """Filing-related API methods."""

    def lookup_filings(
        self: "SecBlastClient",
        *,
        # Entity filters
        ciks: list[str] | None = None,
        tickers: list[str] | None = None,
        exchanges: list[str] | None = None,
        sics: list[str] | None = None,
        states: list[str] | None = None,
        # Filing filters
        form_types: list[str] | None = None,
        excluded_form_types: list[str] | None = None,
        date_from: date | str | None = None,
        date_to: date | str | None = None,
        items: list[str] | None = None,
        exclude_amendments: bool = False,
        # Sorting
        sort_by: str | None = None,
        sort_order: str = "desc",
        # Pagination
        from_: int = 0,
        to: int = 100,
    ) -> FilingLookupResult:
        """
        Search for SEC filings.

        Args:
            ciks: Filter by CIK numbers
            tickers: Filter by stock tickers
            exchanges: Filter by exchanges
            sics: Filter by SIC codes
            states: Filter by states
            form_types: Filter by form types (10-K, 10-Q, 8-K, etc.)
            excluded_form_types: Exclude these form types
            date_from: Minimum filing date (YYYY-MM-DD)
            date_to: Maximum filing date (YYYY-MM-DD)
            items: Filter by 8-K items (1.01, 2.02, etc.)
            exclude_amendments: Exclude amendment forms (10-K/A, 8-K/A, etc.)
            sort_by: Sort field (filing_date, acceptance_date_time, report_date, form, size, entity_name)
            sort_order: Sort order (asc or desc)
            from_: Start index (0-indexed)
            to: End index (exclusive), max 10000

        Returns:
            FilingLookupResult with matching filings
        """
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

        # Filing filters
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

        # Sorting
        if sort_by:
            params["sort_by"] = sort_by
        if sort_order != "desc":
            params["sort_order"] = sort_order

        # Pagination
        if from_ != 0:
            params["from"] = from_
        if to != 100:
            params["to"] = to

        data = self._request("POST", "/filing_lookup", json=params)
        return FilingLookupResult.model_validate(data)

    def get_filing_info(
        self: "SecBlastClient",
        accession_number: str,
    ) -> FilingDetail:
        """
        Get detailed information about a filing.

        Args:
            accession_number: The filing accession number (e.g., "0000320193-23-000077")

        Returns:
            FilingDetail with full filing information, documents, sections, and 8-K items
        """
        data = self._request(
            "POST",
            "/filing_info",
            json={"accession_number": accession_number},
        )
        return FilingDetail.model_validate(data)

    def get_filing_sections(
        self: "SecBlastClient",
        document_id: str,
        form_type: str = "10-K",
    ) -> list[Section]:
        """
        Get sections with HTML content for a 10-K or 10-Q filing.

        Args:
            document_id: The primary document ID
            form_type: Form type ("10-K" or "10-Q")

        Returns:
            List of sections with their HTML content
        """
        data = self._request(
            "POST",
            "/filing_sections",
            json={"document_id": document_id, "form_type": form_type},
        )
        sections_data = data.get("sections", [])
        return [Section.model_validate(s) for s in sections_data]

    def get_8k_items(
        self: "SecBlastClient",
        accession_numbers: list[str],
    ) -> dict[str, list[Item8K]]:
        """
        Batch fetch 8-K items for multiple filings.

        Args:
            accession_numbers: List of accession numbers (max 100)

        Returns:
            Dict mapping accession numbers to their 8-K items
        """
        if len(accession_numbers) > 100:
            raise ValueError("Maximum 100 accession numbers per request")

        data = self._request(
            "POST",
            "/8k_items",
            json={"accession_numbers": accession_numbers},
        )

        result: dict[str, list[Item8K]] = {}
        for acc_num, items in data.items():
            if isinstance(items, list):
                result[acc_num] = [Item8K.model_validate(item) for item in items]

        return result
