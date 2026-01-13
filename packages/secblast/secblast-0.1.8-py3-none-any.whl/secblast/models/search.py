"""Search result data models."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field

from secblast.models.entity import EntityInfo


class SearchHit(BaseModel):
    """Individual search result hit."""

    id: str
    score: float
    accession_number: str = Field(alias="accession_number")
    form_type: str = Field(alias="form_type")
    filing_date: date = Field(alias="filing_date")
    acceptance_date_time: datetime | None = Field(None, alias="acceptance_date_time")
    document_type: str | None = Field(None, alias="document_type")
    document_description: str | None = Field(None, alias="document_description")
    file_name: str | None = Field(None, alias="file_name")
    ciks: list[str] = []
    sics: list[str] = []
    size: int | None = None
    highlights: list[str] = []
    text_content: str | None = Field(None, alias="text_content")

    model_config = {"populate_by_name": True}


class SearchResult(BaseModel):
    """Full-text search result."""

    total_hits: int
    hits: list[SearchHit] = []
    entities: list[EntityInfo] = []
    response_bytes: int | None = None
