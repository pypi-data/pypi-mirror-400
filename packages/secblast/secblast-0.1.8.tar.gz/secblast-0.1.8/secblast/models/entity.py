"""Entity/Company data models."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Address(BaseModel):
    """Mailing or business address."""

    street1: str | None = None
    street2: str | None = None
    city: str | None = None
    state: str | None = None
    zip: str | None = None
    country: str | None = None


class FormerName(BaseModel):
    """Former company name with date range."""

    name: str
    from_date: str | None = Field(None, alias="from")
    to_date: str | None = Field(None, alias="to")


class EntityInfo(BaseModel):
    """SEC entity/company information."""

    cik: str
    name: str
    conformed_name: str | None = Field(None, alias="conformedName")
    entity_type: str | None = Field(None, alias="entityType")
    tickers: list[str] = []
    exchanges: list[str] = []
    sic: str | None = None
    sic_description: str | None = Field(None, alias="sicDescription")
    ein: str | None = None
    description: str | None = None
    website: str | None = None
    fiscal_year_end: str | None = Field(None, alias="fiscalYearEnd")
    state_of_incorporation: str | None = Field(None, alias="stateOfIncorporation")
    addresses: dict[str, Address] | None = None
    former_names: list[FormerName] = Field(default_factory=list, alias="formerNames")

    model_config = {"populate_by_name": True}
