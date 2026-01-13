"""Entity lookup endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel

from secblast.models.entity import EntityInfo

if TYPE_CHECKING:
    from secblast.client import SecBlastClient


class EntityLookupResult(BaseModel):
    """Result from entity lookup."""

    count: int
    truncated: bool = False
    entities: list[EntityInfo] = []


class EntitiesMixin:
    """Entity-related API methods."""

    def lookup_entities(
        self: "SecBlastClient",
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
        """
        Search for SEC entities (companies, filers).

        Args:
            ciks: Filter by CIK numbers
            tickers: Filter by stock tickers
            index_tickers: Filter by index tickers (GSPC, DJI, QQQ)
            exchanges: Filter by exchanges (NYSE, NASDAQ, OTC, CBOE)
            entity_types: Filter by entity type (OPERATING, INVESTMENT, OTHER)
            name_includes: Name must contain all of these (AND logic)
            name_excludes: Exclude if name contains any of these
            sics: Filter by SIC codes
            states: Filter by state abbreviations
            eins: Filter by EIN numbers
            from_: Start index (0-indexed)
            to: End index (exclusive), max 10000

        Returns:
            EntityLookupResult with matching entities
        """
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

        data = self._request("POST", "/entity_lookup", json=params)
        return EntityLookupResult.model_validate(data)

    def get_entity(
        self: "SecBlastClient",
        *,
        cik: str | None = None,
        ticker: str | None = None,
    ) -> EntityInfo | None:
        """
        Get a single entity by CIK or ticker.

        Args:
            cik: CIK number
            ticker: Stock ticker

        Returns:
            EntityInfo if found, None otherwise
        """
        if not cik and not ticker:
            raise ValueError("Must provide either cik or ticker")

        result = self.lookup_entities(
            ciks=[cik] if cik else None,
            tickers=[ticker] if ticker else None,
            to=1,
        )

        return result.entities[0] if result.entities else None
