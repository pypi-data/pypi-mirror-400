"""Filing and document data models."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


class DocumentInfo(BaseModel):
    """Document within a filing."""

    id: str
    accession_number: str | None = Field(None, alias="accessionNumber")
    sequence: int | None = None
    document_type: str | None = Field(None, alias="documentType")
    file_name: str | None = Field(None, alias="fileName")
    description: str | None = None
    size: int | None = None
    content_type: str | None = Field(None, alias="contentType")

    model_config = {"populate_by_name": True}


class Item8K(BaseModel):
    """8-K item information."""

    id: str | None = None
    document_id: str | None = Field(None, alias="documentId")
    accession_number: str | None = Field(None, alias="accessionNumber")
    item_type: str = Field(alias="itemType")
    item_name: str | None = Field(None, alias="itemName")
    item_exhibit_doc_id: str | None = Field(None, alias="itemExhibitDocId")
    item_exhibit_name: str | None = Field(None, alias="itemExhibitName")
    referenced_exhibits: list[str] = Field(
        default_factory=list, alias="referencedExhibits"
    )
    created_at: datetime | None = Field(None, alias="createdAt")
    updated_at: datetime | None = Field(None, alias="updatedAt")

    model_config = {"populate_by_name": True}


class Section(BaseModel):
    """10-K/10-Q section with content."""

    id: str
    document_id: str | None = Field(None, alias="documentId")
    name: str | None = Field(None, alias="itemLabel")
    label: str | None = Field(None, alias="itemDescription")
    content: str | None = None

    model_config = {"populate_by_name": True}


class FilingInfo(BaseModel):
    """SEC filing information from filing_lookup."""

    accession_number: str = Field(alias="accessionNumber")
    form_type: str = Field(alias="form")
    cik: str
    filing_date: date = Field(alias="filingDate")
    report_date: date | None = Field(None, alias="reportDate")
    acceptance_datetime: datetime | None = Field(None, alias="acceptanceDateTime")
    document_count: int | None = Field(None, alias="documentCount")
    documents: list[DocumentInfo] = []
    eightk_items: list[Item8K] = Field(default_factory=list, alias="eightkItems")
    # Additional fields from API
    entity_name: str | None = Field(None, alias="entityName")
    tickers: list[str] = []
    size: int | None = None
    primary_document: str | None = Field(None, alias="primaryDocument")

    model_config = {"populate_by_name": True}


class FilingInfoDetail(BaseModel):
    """SEC filing information from filing_info (uses different field names)."""

    accession_number: str = Field(alias="accessionNumber")
    form_type: str = Field(alias="formType")
    cik: str
    filing_date: date = Field(alias="filingDate")
    report_date: date | None = Field(None, alias="reportDate")
    acceptance_datetime: datetime | None = Field(None, alias="acceptanceDatetime")
    document_count: int | None = Field(None, alias="documentCount")

    model_config = {"populate_by_name": True}


class FilingDetail(BaseModel):
    """Detailed filing information including filer and documents."""

    filing: FilingInfoDetail
    filer: dict | None = None
    documents: list[DocumentInfo] = []
    sections: list[Section] = []
    eightk_items: list[Item8K] = Field(default_factory=list, alias="eightkItems")

    model_config = {"populate_by_name": True}
