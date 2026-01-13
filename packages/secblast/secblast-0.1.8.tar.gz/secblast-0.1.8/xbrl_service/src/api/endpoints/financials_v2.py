"""
Financial data API endpoints v2 - using new sb_xbrl_* tables.
"""

import logging
from enum import Enum
from typing import Optional, List, Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.database import get_db_session
from ...services.financial_extractor_v2 import FinancialExtractorV2

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v2/financials", tags=["financials"])


@router.get("")
async def get_financials(
    cik: int = Query(..., description="Company CIK number"),
    accession_number: Optional[str] = Query(None, description="Specific filing accession number"),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Get all financial statements for a company.

    Returns the most recent balance sheet, income statement, and cash flow.
    """
    extractor = FinancialExtractorV2(db)

    balance_sheet = await extractor.get_balance_sheet(cik, accession_number)
    income_statement = await extractor.get_income_statement(cik, accession_number)
    cash_flow = await extractor.get_cash_flow(cik, accession_number)
    filings = await extractor.get_filings(cik)

    return {
        "cik": str(cik),
        "balance_sheet": balance_sheet,
        "income_statement": income_statement,
        "cash_flow": cash_flow,
        "filings": filings,
    }


@router.get("/balance-sheet")
async def get_balance_sheet(
    cik: int = Query(..., description="Company CIK number"),
    accession_number: Optional[str] = Query(None, description="Specific filing accession number"),
    format: Optional[Literal["default", "table"]] = Query(
        "default",
        description="Response format: 'default' returns line_items with nested values, 'table' returns columns and rows for easy table rendering"
    ),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Get balance sheet for a company.

    Use format=table for easy table rendering with columns (periods) and rows (line items).
    """
    extractor = FinancialExtractorV2(db)

    if format == "table":
        statement = await extractor.get_statement_table(cik, "balance_sheet", accession_number)
    else:
        statement = await extractor.get_balance_sheet(cik, accession_number)

    if not statement:
        raise HTTPException(
            status_code=404,
            detail=f"Balance sheet not found for CIK {cik}. Ensure XBRL data has been processed."
        )

    return statement


@router.get("/income-statement")
async def get_income_statement(
    cik: int = Query(..., description="Company CIK number"),
    accession_number: Optional[str] = Query(None, description="Specific filing accession number"),
    format: Optional[Literal["default", "table"]] = Query(
        "default",
        description="Response format: 'default' returns line_items with nested values, 'table' returns columns and rows for easy table rendering"
    ),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Get income statement for a company.

    Use format=table for easy table rendering with columns (periods) and rows (line items).
    """
    extractor = FinancialExtractorV2(db)

    if format == "table":
        statement = await extractor.get_statement_table(cik, "income_statement", accession_number)
    else:
        statement = await extractor.get_income_statement(cik, accession_number)

    if not statement:
        raise HTTPException(
            status_code=404,
            detail=f"Income statement not found for CIK {cik}. Ensure XBRL data has been processed."
        )

    return statement


@router.get("/cash-flow")
async def get_cash_flow(
    cik: int = Query(..., description="Company CIK number"),
    accession_number: Optional[str] = Query(None, description="Specific filing accession number"),
    format: Optional[Literal["default", "table"]] = Query(
        "default",
        description="Response format: 'default' returns line_items with nested values, 'table' returns columns and rows for easy table rendering"
    ),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Get cash flow statement for a company.

    Use format=table for easy table rendering with columns (periods) and rows (line items).
    """
    extractor = FinancialExtractorV2(db)

    if format == "table":
        statement = await extractor.get_statement_table(cik, "cash_flow", accession_number)
    else:
        statement = await extractor.get_cash_flow(cik, accession_number)

    if not statement:
        raise HTTPException(
            status_code=404,
            detail=f"Cash flow statement not found for CIK {cik}. Ensure XBRL data has been processed."
        )

    return statement


@router.get("/raw")
async def get_raw_xbrl(
    cik: int = Query(..., description="Company CIK number"),
    accession_number: Optional[str] = Query(None, description="Specific filing accession number"),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Get complete raw XBRL data for a filing.

    Returns all facts organized by statement type with presentation structure.
    """
    extractor = FinancialExtractorV2(db)
    data = await extractor.get_raw_xbrl(cik, accession_number)

    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"XBRL data not found for CIK {cik}. Ensure XBRL data has been processed."
        )

    return data


@router.get("/filings")
async def get_available_filings(
    cik: int = Query(..., description="Company CIK number"),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Get list of all available filings with XBRL data for a company.
    """
    extractor = FinancialExtractorV2(db)
    filings = await extractor.get_filings(cik)

    return {
        "cik": str(cik),
        "filings": filings,
        "total_count": len(filings),
    }


@router.get("/history")
async def get_financial_history(
    cik: int = Query(..., description="Company CIK number"),
    concepts: str = Query(..., description="Comma-separated list of XBRL concept names"),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Get historical values for specific XBRL concepts across all filings.

    Use this endpoint to chart metrics over time. Pass concept names
    (e.g., "Assets,RevenueFromContractWithCustomerExcludingAssessedTax,NetIncomeLoss")
    to retrieve their historical values.
    """
    extractor = FinancialExtractorV2(db)

    concept_list = [c.strip() for c in concepts.split(",") if c.strip()]
    if not concept_list:
        raise HTTPException(status_code=400, detail="At least one concept name is required")

    history = await extractor.get_history(cik, concept_list)

    return {
        "cik": str(cik),
        "concepts": history,
    }
