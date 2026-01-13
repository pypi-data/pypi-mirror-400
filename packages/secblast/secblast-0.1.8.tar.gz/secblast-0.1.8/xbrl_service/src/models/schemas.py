from datetime import date
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, field_validator


def to_camel(string: str) -> str:
    """Convert snake_case to camelCase."""
    components = string.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


class CamelCaseModel(BaseModel):
    """Base model that converts snake_case to camelCase for JSON output."""
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        serialize_by_alias=True,  # Ensures JSON output uses camelCase
    )


class FinancialLineItem(CamelCaseModel):
    """A single line item in a financial statement."""

    label: str
    value: float
    unit: str = "USD"
    children: Optional[Dict[str, "FinancialLineItem"]] = None


class FinancialStatementResponse(CamelCaseModel):
    """Response model for a single financial statement."""

    id: int
    cik: str
    accession_number: str
    filing_date: date
    form_type: str
    fiscal_year: Optional[int] = None
    fiscal_period: Optional[str] = None
    statement_type: str
    period_end: date
    currency: str = "USD"
    data: Dict[str, Any]

    @field_validator("cik", mode="before")
    @classmethod
    def convert_cik_to_str(cls, v):
        return str(v) if v is not None else v

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        serialize_by_alias=True,
        from_attributes=True,
    )


class FinancialFilingSummary(CamelCaseModel):
    """Summary of a filing with financial data."""

    accession_number: str
    filing_date: date
    form_type: str
    fiscal_year: Optional[int] = None
    fiscal_period: Optional[str] = None


class FinancialsResponse(CamelCaseModel):
    """Response model for all financials of a company."""

    balance_sheet: Optional[FinancialStatementResponse] = None
    income_statement: Optional[FinancialStatementResponse] = None
    cash_flow: Optional[FinancialStatementResponse] = None
    filings: List[FinancialFilingSummary] = []


class ParseXBRLRequest(CamelCaseModel):
    """Request model for parsing XBRL data."""

    cik: int
    accession_number: str


class ParseXBRLResponse(CamelCaseModel):
    """Response model for XBRL parsing."""

    success: bool
    message: str
    statements_created: int = 0


# ========== NEW SCHEMAS FOR FULL XBRL ==========


class XBRLFact(CamelCaseModel):
    """A single XBRL fact value with all context."""

    concept: str
    label: str
    value: Any
    unit: Optional[str] = None
    period_end: Optional[date] = None
    period_start: Optional[date] = None
    dimensions: Dict[str, str] = {}
    decimals: Optional[str] = None


class PresentationNode(CamelCaseModel):
    """A node in the presentation hierarchy tree."""

    concept: str
    label: str
    level: int = 0
    is_abstract: bool = False
    children: List["PresentationNode"] = []

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
        serialize_by_alias=True,
        from_attributes=True,
    )


# Enable self-referencing model
PresentationNode.model_rebuild()


class CalculationChild(CamelCaseModel):
    """A child item in a calculation relationship."""

    concept: str
    label: str
    weight: float = 1.0
    order: float = 0.0


class CalculationRelationship(CamelCaseModel):
    """A calculation rollup relationship showing how a total is computed."""

    parent_concept: str
    parent_label: str
    children: List[CalculationChild] = []


class RawXBRLResponse(CamelCaseModel):
    """Complete raw XBRL data response with all facts and linkbase data."""

    cik: str
    accession_number: str
    filing_date: date
    form_type: str
    fiscal_year: Optional[int] = None
    fiscal_period: Optional[str] = None
    period_end: date

    # Presentation trees organized by statement type
    balance_sheet: List[PresentationNode] = []
    income_statement: List[PresentationNode] = []
    cash_flow: List[PresentationNode] = []
    equity_statement: List[PresentationNode] = []
    other_statements: List[PresentationNode] = []

    # Calculation relationships keyed by parent concept
    calculations: Dict[str, CalculationRelationship] = {}

    # All facts keyed by concept name
    facts: Dict[str, List[XBRLFact]] = {}

    # Human-readable labels
    labels: Dict[str, str] = {}


class HistoricalDataPoint(CamelCaseModel):
    """A single historical data point for charting."""

    filing_date: date
    period_end: date
    fiscal_year: Optional[int] = None
    fiscal_period: Optional[str] = None
    form_type: str
    value: Any
    accession_number: str


class FinancialHistoryResponse(CamelCaseModel):
    """Historical data for selected concepts across all filings."""

    cik: str
    concepts: Dict[str, List[HistoricalDataPoint]] = {}
    total_filings: int = 0


class AvailableFilingsResponse(CamelCaseModel):
    """List of all available filings with XBRL data for a company."""

    cik: str
    filings: List[FinancialFilingSummary] = []
    total_count: int = 0
