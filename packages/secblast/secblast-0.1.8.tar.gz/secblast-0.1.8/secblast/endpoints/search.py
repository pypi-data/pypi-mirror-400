"""Full-text search endpoints."""

from __future__ import annotations

from datetime import date
from enum import Enum
from typing import TYPE_CHECKING, Literal

from secblast.models.search import SearchResult

if TYPE_CHECKING:
    from secblast.client import SecBlastClient


class QueryType(str, Enum):
    """Search query types."""

    MATCH = "match"
    MATCH_PHRASE = "match_phrase"
    QUERY_STRING = "query_string"


class SearchMixin:
    """Search-related API methods."""

    def fulltext_search(
        self: "SecBlastClient",
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
        """
        Full-text search across SEC documents using Elasticsearch.

        Args:
            query: Search query string
            query_type: Type of query:
                - match: Standard full-text (word splitting, stemming)
                - match_phrase: Exact phrase matching
                - query_string: Lucene syntax (AND, OR, NOT, wildcards)
            ciks: Filter by CIK numbers
            form_types: Filter by form types
            accession_numbers: Filter by accession number prefixes
            date_from: Minimum filing date
            date_to: Maximum filing date
            sort_by: Sort field ("filing_date" or "_score")
            sort_order: Sort order ("asc" or "desc")
            from_: Start index (0-indexed)
            to: End index (exclusive), max 10000

        Returns:
            SearchResult with hits and entity information

        Examples:
            # Standard search
            client.fulltext_search("material contract")

            # Exact phrase
            client.fulltext_search("material contract", query_type="match_phrase")

            # Lucene syntax
            client.fulltext_search("revenue AND NOT loss", query_type="query_string")
            client.fulltext_search("(merger OR acquisition) AND agreement", query_type="query_string")
            client.fulltext_search("acqui*", query_type="query_string")  # wildcard
        """
        params: dict = {"query": query}

        # Query type
        if isinstance(query_type, QueryType):
            query_type = query_type.value
        if query_type != "match":
            params["query_type"] = query_type

        # Filters
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

        # Sorting
        if sort_by != "filing_date":
            params["sort_by"] = sort_by
        if sort_order != "desc":
            params["sort_order"] = sort_order

        # Pagination
        if from_ != 0:
            params["from"] = from_
        if to != 100:
            params["to"] = to

        data = self._request("POST", "/fulltext_search", json=params)
        return SearchResult.model_validate(data)
