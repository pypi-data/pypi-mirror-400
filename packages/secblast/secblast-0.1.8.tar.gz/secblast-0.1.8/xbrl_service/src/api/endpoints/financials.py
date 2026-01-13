"""
Financial data API endpoints.
"""

import time
import logging
from datetime import date
from io import BytesIO
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

logger = logging.getLogger(__name__)
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.database import get_db_session
from ...models.schemas import (
    FinancialsResponse,
    FinancialStatementResponse,
    FinancialFilingSummary,
    ParseXBRLRequest,
    ParseXBRLResponse,
    RawXBRLResponse,
    FinancialHistoryResponse,
    AvailableFilingsResponse,
    PresentationNode,
    CalculationRelationship,
    CalculationChild,
    XBRLFact,
    HistoricalDataPoint,
)
from ...services.financial_extractor import FinancialExtractor
from ...services.xbrl_parser import XBRLParser

router = APIRouter(prefix="/v2/financials", tags=["financials"])


@router.get("", response_model=FinancialsResponse)
async def get_financials(
    cik: int = Query(..., description="Company CIK number"),
    accession_number: Optional[str] = Query(None, description="Specific filing accession number"),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Get all financial statements for a company.

    Returns the most recent balance sheet, income statement, and cash flow,
    along with a list of available filings.
    """
    extractor = FinancialExtractor(db)

    balance_sheet = await extractor.get_balance_sheet(cik, accession_number)
    income_statement = await extractor.get_income_statement(cik, accession_number)
    cash_flow = await extractor.get_cash_flow(cik, accession_number)
    filings = await extractor.get_filing_summaries(cik)

    return FinancialsResponse(
        balance_sheet=FinancialStatementResponse.model_validate(balance_sheet) if balance_sheet else None,
        income_statement=FinancialStatementResponse.model_validate(income_statement) if income_statement else None,
        cash_flow=FinancialStatementResponse.model_validate(cash_flow) if cash_flow else None,
        filings=[FinancialFilingSummary(**f) for f in filings],
    )


@router.get("/balance-sheet")
async def get_balance_sheet(
    cik: int = Query(..., description="Company CIK number"),
    accession_number: Optional[str] = Query(None, description="Specific filing accession number"),
    db: AsyncSession = Depends(get_db_session),
):
    """Get balance sheet for a company."""
    total_start = time.perf_counter()

    t0 = time.perf_counter()
    extractor = FinancialExtractor(db)
    t1 = time.perf_counter()

    statement = await extractor.get_balance_sheet(cik, accession_number)
    t2 = time.perf_counter()

    if not statement:
        raise HTTPException(status_code=404, detail="Balance sheet not found")

    response = FinancialStatementResponse.model_validate(statement)
    t3 = time.perf_counter()

    result = response.model_dump(by_alias=True, mode="json")
    t4 = time.perf_counter()

    logger.info(f"TIMING balance-sheet cik={cik}: "
                f"init={1000*(t1-t0):.1f}ms, "
                f"get_balance_sheet={1000*(t2-t1):.1f}ms, "
                f"validate={1000*(t3-t2):.1f}ms, "
                f"dump={1000*(t4-t3):.1f}ms, "
                f"total={1000*(t4-total_start):.1f}ms")

    return result


@router.get("/income-statement")
async def get_income_statement(
    cik: int = Query(..., description="Company CIK number"),
    accession_number: Optional[str] = Query(None, description="Specific filing accession number"),
    db: AsyncSession = Depends(get_db_session),
):
    """Get income statement for a company."""
    extractor = FinancialExtractor(db)
    statement = await extractor.get_income_statement(cik, accession_number)

    if not statement:
        raise HTTPException(status_code=404, detail="Income statement not found")

    response = FinancialStatementResponse.model_validate(statement)
    return response.model_dump(by_alias=True, mode="json")


@router.get("/cash-flow")
async def get_cash_flow(
    cik: int = Query(..., description="Company CIK number"),
    accession_number: Optional[str] = Query(None, description="Specific filing accession number"),
    db: AsyncSession = Depends(get_db_session),
):
    """Get cash flow statement for a company."""
    extractor = FinancialExtractor(db)
    statement = await extractor.get_cash_flow(cik, accession_number)

    if not statement:
        raise HTTPException(status_code=404, detail="Cash flow statement not found")

    response = FinancialStatementResponse.model_validate(statement)
    return response.model_dump(by_alias=True, mode="json")


@router.get("/filing", response_model=FinancialsResponse)
async def get_filing_financials(
    accession_number: str = Query(..., description="Filing accession number"),
    db: AsyncSession = Depends(get_db_session),
):
    """Get all financial statements for a specific filing."""
    # We need to look up the CIK from the accession number
    # For now, this requires the CIK to be passed
    raise HTTPException(
        status_code=400,
        detail="Please use /v2/financials with cik and accession_number parameters",
    )


@router.post("/parse", response_model=ParseXBRLResponse)
async def parse_xbrl(
    request: ParseXBRLRequest,
    filing_date: date = Query(..., description="Filing date"),
    form_type: str = Query(..., description="Form type (10-K, 10-Q, etc.)"),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Parse XBRL data from a filing and store the results.

    This endpoint is typically called by the filing processor when new
    10-K or 10-Q filings are detected.
    """
    extractor = FinancialExtractor(db)

    try:
        count = await extractor.parse_and_store(
            cik=request.cik,
            accession_number=request.accession_number,
            filing_date=filing_date,
            form_type=form_type,
        )

        return ParseXBRLResponse(
            success=True,
            message=f"Successfully parsed filing {request.accession_number}",
            statements_created=count,
        )
    except FileNotFoundError as e:
        return ParseXBRLResponse(
            success=False,
            message=str(e),
            statements_created=0,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== NEW ENDPOINTS FOR FULL XBRL ==========


@router.get("/raw")
async def get_raw_xbrl(
    cik: int = Query(..., description="Company CIK number"),
    accession_number: Optional[str] = Query(None, description="Specific filing accession number"),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Get complete raw XBRL data for a filing.

    Returns all facts, presentation hierarchy, calculation relationships,
    and human-readable labels from the XBRL filing.

    If no accession_number is provided, returns data for the most recent 10-K.
    """
    extractor = FinancialExtractor(db)

    # Get filing info
    if not accession_number:
        # Find most recent 10-K
        filing_info = await extractor.find_latest_10k(cik)
        if not filing_info:
            filing_info = await extractor.find_latest_10q(cik)
        if not filing_info:
            raise HTTPException(status_code=404, detail=f"No 10-K or 10-Q filings found for CIK {cik}")
        accession_number, filing_date, form_type = filing_info
    else:
        # Get filing info from database
        filing_info = await extractor.get_filing_info(cik, accession_number)
        if not filing_info:
            raise HTTPException(status_code=404, detail=f"Filing {accession_number} not found")
        filing_date, form_type = filing_info

    # Try to get from cache/database first
    cached = await extractor.get_raw_xbrl_data(cik, accession_number)
    if cached:
        response = _build_raw_response(cached, cik, accession_number, filing_date, form_type)
        return response.model_dump(by_alias=True, mode="json")

    # Parse the filing
    parser = XBRLParser()
    try:
        parsed = parser.parse_filing_full(cik, accession_number, filing_date)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing XBRL: {str(e)}")

    # Store for future requests
    await extractor.store_raw_xbrl_data(
        cik=cik,
        accession_number=accession_number,
        filing_date=filing_date,
        form_type=form_type,
        data=parsed,
    )

    response = _build_raw_response(parsed, cik, accession_number, filing_date, form_type)
    return response.model_dump(by_alias=True, mode="json")


def _build_fallback_presentation(
    all_facts: dict,
    labels: dict,
) -> dict:
    """Build hierarchical presentation trees from facts when linkbase is missing."""

    def get_label(concept: str) -> str:
        return labels.get(concept, concept)

    def create_node(concept: str, level: int = 1, is_abstract: bool = False) -> dict:
        return {
            "concept": concept,
            "label": get_label(concept),
            "level": level,
            "is_abstract": is_abstract,
            "children": [],
        }

    def create_section(name: str, label: str) -> dict:
        return {
            "concept": name,
            "label": label,
            "level": 0,
            "is_abstract": True,
            "children": [],
        }

    def matches_any(concept: str, patterns: list) -> bool:
        concept_lower = concept.lower()
        return any(p.lower() in concept_lower for p in patterns)

    def has_numeric_value(concept: str) -> bool:
        facts = all_facts.get(concept, [])
        return facts and any(isinstance(f.get('value'), (int, float)) for f in facts)

    # Skip non-financial concepts
    def is_financial(concept: str) -> bool:
        return not (concept.startswith('Document') or concept.startswith('Entity') or
                   concept.startswith('Auditor') or concept.startswith('Security'))

    # ==================== BALANCE SHEET ====================
    bs_current_assets = create_section("CurrentAssets", "Current Assets")
    bs_noncurrent_assets = create_section("NoncurrentAssets", "Non-current Assets")
    bs_current_liabs = create_section("CurrentLiabilities", "Current Liabilities")
    bs_noncurrent_liabs = create_section("NoncurrentLiabilities", "Non-current Liabilities")
    bs_equity = create_section("StockholdersEquitySection", "Stockholders' Equity")
    bs_totals = create_section("Totals", "Totals")

    # Current asset patterns
    current_asset_patterns = ['Current', 'ShortTerm', 'Inventory', 'Receivable', 'Prepaid']
    # Non-current asset patterns
    noncurrent_asset_patterns = ['Noncurrent', 'PropertyPlant', 'Goodwill', 'Intangible', 'LongTerm', 'Deferred']
    # Current liability patterns
    current_liab_patterns = ['Current', 'Payable', 'Accrued', 'ShortTerm']
    # Non-current liability patterns
    noncurrent_liab_patterns = ['Noncurrent', 'LongTerm', 'Deferred']
    # Equity patterns
    equity_patterns = ['Equity', 'Stock', 'RetainedEarnings', 'Treasury', 'AccumulatedOther', 'Capital']
    # Total patterns
    total_patterns = ['Assets', 'Liabilities', 'LiabilitiesAndStockholders']

    for concept in sorted(all_facts.keys()):
        if not is_financial(concept) or not has_numeric_value(concept):
            continue
        c_lower = concept.lower()

        # Check if it's a total line
        if 'total' in c_lower or concept in ['Assets', 'AssetsCurrent', 'AssetsNoncurrent',
                                               'Liabilities', 'LiabilitiesCurrent', 'LiabilitiesNoncurrent',
                                               'StockholdersEquity', 'LiabilitiesAndStockholdersEquity']:
            if matches_any(concept, ['Asset', 'Liabil', 'Equity']):
                bs_totals["children"].append(create_node(concept))
                continue

        # Assets
        if 'asset' in c_lower:
            if matches_any(concept, current_asset_patterns) and 'noncurrent' not in c_lower:
                bs_current_assets["children"].append(create_node(concept))
            elif matches_any(concept, noncurrent_asset_patterns) or 'noncurrent' in c_lower:
                bs_noncurrent_assets["children"].append(create_node(concept))
            continue

        # Cash, Inventory, Receivables -> Current Assets
        if any(p in c_lower for p in ['cash', 'inventory', 'receivable', 'prepaid']):
            if 'noncurrent' not in c_lower:
                bs_current_assets["children"].append(create_node(concept))
            continue

        # PPE, Goodwill, Intangibles -> Non-current Assets
        if any(p in c_lower for p in ['property', 'plant', 'equipment', 'goodwill', 'intangible']):
            bs_noncurrent_assets["children"].append(create_node(concept))
            continue

        # Liabilities
        if 'liabilit' in c_lower or 'payable' in c_lower or 'debt' in c_lower:
            if matches_any(concept, current_liab_patterns) and 'noncurrent' not in c_lower and 'longterm' not in c_lower:
                bs_current_liabs["children"].append(create_node(concept))
            else:
                bs_noncurrent_liabs["children"].append(create_node(concept))
            continue

        # Accrued -> Current Liabilities
        if 'accrued' in c_lower and 'noncurrent' not in c_lower:
            bs_current_liabs["children"].append(create_node(concept))
            continue

        # Equity
        if matches_any(concept, equity_patterns):
            bs_equity["children"].append(create_node(concept))
            continue

    balance_sheet = []
    if bs_current_assets["children"]:
        balance_sheet.append(bs_current_assets)
    if bs_noncurrent_assets["children"]:
        balance_sheet.append(bs_noncurrent_assets)
    if bs_current_liabs["children"]:
        balance_sheet.append(bs_current_liabs)
    if bs_noncurrent_liabs["children"]:
        balance_sheet.append(bs_noncurrent_liabs)
    if bs_equity["children"]:
        balance_sheet.append(bs_equity)
    if bs_totals["children"]:
        balance_sheet.append(bs_totals)

    # ==================== INCOME STATEMENT ====================
    is_revenue = create_section("Revenue", "Revenue")
    is_cost = create_section("CostOfRevenue", "Cost of Revenue")
    is_gross = create_section("GrossProfit", "Gross Profit")
    is_opex = create_section("OperatingExpenses", "Operating Expenses")
    is_opinc = create_section("OperatingIncome", "Operating Income")
    is_other = create_section("OtherIncomeExpense", "Other Income/Expense")
    is_pretax = create_section("IncomeBeforeTax", "Income Before Tax")
    is_tax = create_section("IncomeTax", "Income Tax")
    is_netinc = create_section("NetIncome", "Net Income")
    is_eps = create_section("EarningsPerShare", "Earnings Per Share")

    for concept in sorted(all_facts.keys()):
        if not is_financial(concept) or not has_numeric_value(concept):
            continue
        c_lower = concept.lower()

        # Revenue
        if any(p in c_lower for p in ['revenue', 'sales', 'netsales']):
            is_revenue["children"].append(create_node(concept))
        # Cost of Revenue
        elif any(p in c_lower for p in ['costof', 'costofgoods', 'costofrevenue', 'costofservices']):
            is_cost["children"].append(create_node(concept))
        # Gross Profit
        elif 'grossprofit' in c_lower:
            is_gross["children"].append(create_node(concept))
        # Operating Expenses
        elif any(p in c_lower for p in ['researchanddevelopment', 'sellinggeneral', 'operatingexpense', 'amortization']):
            is_opex["children"].append(create_node(concept))
        # Operating Income
        elif 'operatingincome' in c_lower or 'operatingloss' in c_lower:
            is_opinc["children"].append(create_node(concept))
        # Other Income/Expense
        elif any(p in c_lower for p in ['interestexpense', 'interestincome', 'otherincome', 'otherexpense', 'nonoperating']):
            is_other["children"].append(create_node(concept))
        # Income Before Tax
        elif 'beforeincometax' in c_lower or 'beforetax' in c_lower:
            is_pretax["children"].append(create_node(concept))
        # Income Tax
        elif 'incometax' in c_lower and 'before' not in c_lower:
            is_tax["children"].append(create_node(concept))
        # Net Income
        elif 'netincome' in c_lower or 'netloss' in c_lower:
            is_netinc["children"].append(create_node(concept))
        # EPS
        elif 'earningspershare' in c_lower or 'pershare' in c_lower:
            is_eps["children"].append(create_node(concept))

    income_statement = []
    for section in [is_revenue, is_cost, is_gross, is_opex, is_opinc, is_other, is_pretax, is_tax, is_netinc, is_eps]:
        if section["children"]:
            income_statement.append(section)

    # ==================== CASH FLOW ====================
    cf_operating = create_section("OperatingActivities", "Cash Flows from Operating Activities")
    cf_investing = create_section("InvestingActivities", "Cash Flows from Investing Activities")
    cf_financing = create_section("FinancingActivities", "Cash Flows from Financing Activities")
    cf_net = create_section("NetChange", "Net Change in Cash")

    for concept in sorted(all_facts.keys()):
        if not is_financial(concept) or not has_numeric_value(concept):
            continue
        c_lower = concept.lower()

        # Operating Activities
        if any(p in c_lower for p in ['operatingactivities', 'depreciation', 'amortization',
                                       'stockbasedcompensation', 'deferredtax', 'increasedecrease']):
            cf_operating["children"].append(create_node(concept))
        # Investing Activities
        elif any(p in c_lower for p in ['investingactivities', 'paymentstoacquire', 'proceedsfrom',
                                         'capitalexpenditure', 'purchaseof', 'saleof']):
            if 'financing' not in c_lower:
                cf_investing["children"].append(create_node(concept))
        # Financing Activities
        elif any(p in c_lower for p in ['financingactivities', 'repayment', 'dividend',
                                         'stockrepurchase', 'proceedsfromissuance', 'treasury']):
            cf_financing["children"].append(create_node(concept))
        # Net Change
        elif any(p in c_lower for p in ['netcash', 'cashcashequivalents', 'periodincreasedecrease']):
            cf_net["children"].append(create_node(concept))

    cash_flow = []
    for section in [cf_operating, cf_investing, cf_financing, cf_net]:
        if section["children"]:
            cash_flow.append(section)

    return {
        "balance_sheet": balance_sheet,
        "income_statement": income_statement,
        "cash_flow": cash_flow,
        "equity_statement": [],
        "other": [],
    }


def _build_fallback_calculations(all_facts: dict, labels: dict) -> dict:
    """Build calculation relationships from known GAAP hierarchies when linkbase is missing."""

    def get_label(concept: str) -> str:
        return labels.get(concept, concept)

    def is_text_block(concept: str) -> bool:
        """Check if concept is a text block (narrative disclosure)."""
        c_lower = concept.lower()
        return 'textblock' in c_lower or 'policytext' in c_lower or 'tabletext' in c_lower

    def find_concepts(patterns: list) -> list:
        """Find concepts matching any of the patterns."""
        matched = []
        for concept in all_facts.keys():
            # Skip text block / narrative concepts
            if is_text_block(concept):
                continue
            c_lower = concept.lower()
            if any(p.lower() in c_lower for p in patterns):
                # Skip abstract/grouping concepts
                if not concept.startswith('Document') and not concept.startswith('Entity'):
                    matched.append(concept)
        return matched

    calculations = {}

    # ===== BALANCE SHEET CALCULATIONS =====

    # Assets = AssetsCurrent + AssetsNoncurrent (or NoncurrentAssets)
    if 'Assets' in all_facts:
        children = []
        if 'AssetsCurrent' in all_facts:
            children.append({"concept": "AssetsCurrent", "label": get_label("AssetsCurrent"), "weight": 1.0, "order": 1})
        # Check both naming conventions for non-current assets
        noncurrent_concept = None
        if 'AssetsNoncurrent' in all_facts:
            noncurrent_concept = 'AssetsNoncurrent'
        elif 'NoncurrentAssets' in all_facts:
            noncurrent_concept = 'NoncurrentAssets'
        if noncurrent_concept:
            children.append({"concept": noncurrent_concept, "label": get_label(noncurrent_concept), "weight": 1.0, "order": 2})
        if children:
            calculations["Assets"] = {
                "parent_concept": "Assets",
                "parent_label": get_label("Assets"),
                "children": children
            }

    # Current Assets breakdown
    current_asset_concepts = find_concepts(['CashAndCash', 'ShortTermInvestment', 'AccountsReceivable',
                                            'Inventory', 'PrepaidExpense', 'OtherAssetsCurrent'])
    if 'AssetsCurrent' in all_facts and current_asset_concepts:
        children = [{"concept": c, "label": get_label(c), "weight": 1.0, "order": i}
                   for i, c in enumerate(sorted(current_asset_concepts), 1)]
        if children:
            calculations["AssetsCurrent"] = {
                "parent_concept": "AssetsCurrent",
                "parent_label": get_label("AssetsCurrent"),
                "children": children
            }

    # Non-current Assets breakdown - only main line items (exact matches preferred)
    noncurrent_key = 'NoncurrentAssets' if 'NoncurrentAssets' in all_facts else 'AssetsNoncurrent'
    if noncurrent_key in all_facts:
        # Use exact concept names for main balance sheet line items
        noncurrent_line_items = [
            'PropertyPlantAndEquipmentNet',
            'Goodwill',
            'IntangibleAssetsNetExcludingGoodwill',
            'LongTermInvestments',
            'OtherAssetsNoncurrent',
            'DeferredTaxAssetsNet',
            'OperatingLeaseRightOfUseAsset',
            'EquityMethodInvestments',
        ]
        children = []
        for i, concept in enumerate(noncurrent_line_items, 1):
            if concept in all_facts:
                children.append({"concept": concept, "label": get_label(concept), "weight": 1.0, "order": float(i)})
        if children:
            calculations[noncurrent_key] = {
                "parent_concept": noncurrent_key,
                "parent_label": get_label(noncurrent_key),
                "children": children
            }

    # Liabilities = LiabilitiesCurrent + LiabilitiesNoncurrent
    if 'Liabilities' in all_facts:
        children = []
        if 'LiabilitiesCurrent' in all_facts:
            children.append({"concept": "LiabilitiesCurrent", "label": get_label("LiabilitiesCurrent"), "weight": 1.0, "order": 1})
        if 'LiabilitiesNoncurrent' in all_facts:
            children.append({"concept": "LiabilitiesNoncurrent", "label": get_label("LiabilitiesNoncurrent"), "weight": 1.0, "order": 2})
        if children:
            calculations["Liabilities"] = {
                "parent_concept": "Liabilities",
                "parent_label": get_label("Liabilities"),
                "children": children
            }

    # LiabilitiesAndStockholdersEquity = Liabilities + StockholdersEquity
    if 'LiabilitiesAndStockholdersEquity' in all_facts:
        children = []
        if 'Liabilities' in all_facts:
            children.append({"concept": "Liabilities", "label": get_label("Liabilities"), "weight": 1.0, "order": 1})
        if 'StockholdersEquity' in all_facts:
            children.append({"concept": "StockholdersEquity", "label": get_label("StockholdersEquity"), "weight": 1.0, "order": 2})
        if children:
            calculations["LiabilitiesAndStockholdersEquity"] = {
                "parent_concept": "LiabilitiesAndStockholdersEquity",
                "parent_label": get_label("LiabilitiesAndStockholdersEquity"),
                "children": children
            }

    # ===== INCOME STATEMENT CALCULATIONS =====

    # Gross Profit = Revenue - Cost of Revenue
    revenue_concepts = find_concepts(['Revenue', 'Sales', 'NetSales'])
    cost_concepts = find_concepts(['CostOfRevenue', 'CostOfGoodsSold', 'CostOfServices'])
    if 'GrossProfit' in all_facts and (revenue_concepts or cost_concepts):
        children = []
        for c in revenue_concepts[:2]:
            children.append({"concept": c, "label": get_label(c), "weight": 1.0, "order": len(children) + 1})
        for c in cost_concepts[:2]:
            children.append({"concept": c, "label": get_label(c), "weight": -1.0, "order": len(children) + 1})
        if children:
            calculations["GrossProfit"] = {
                "parent_concept": "GrossProfit",
                "parent_label": get_label("GrossProfit"),
                "children": children
            }

    # Operating Income = Gross Profit - Operating Expenses
    opex_concepts = find_concepts(['ResearchAndDevelopment', 'SellingGeneral', 'OperatingExpenses'])
    if 'OperatingIncomeLoss' in all_facts:
        children = []
        if 'GrossProfit' in all_facts:
            children.append({"concept": "GrossProfit", "label": get_label("GrossProfit"), "weight": 1.0, "order": 1})
        for i, c in enumerate(opex_concepts[:3], 2):
            children.append({"concept": c, "label": get_label(c), "weight": -1.0, "order": i})
        if children:
            calculations["OperatingIncomeLoss"] = {
                "parent_concept": "OperatingIncomeLoss",
                "parent_label": get_label("OperatingIncomeLoss"),
                "children": children
            }

    # Net Income = Income Before Tax - Tax
    tax_concepts = find_concepts(['IncomeTaxExpense'])
    pretax_concepts = find_concepts(['IncomeLossFromContinuingOperationsBeforeTax', 'IncomeBeforeTax'])
    if 'NetIncomeLoss' in all_facts:
        children = []
        for c in pretax_concepts[:1]:
            children.append({"concept": c, "label": get_label(c), "weight": 1.0, "order": 1})
        for c in tax_concepts[:1]:
            children.append({"concept": c, "label": get_label(c), "weight": -1.0, "order": 2})
        if children:
            calculations["NetIncomeLoss"] = {
                "parent_concept": "NetIncomeLoss",
                "parent_label": get_label("NetIncomeLoss"),
                "children": children
            }

    # ===== CASH FLOW CALCULATIONS =====

    # Net Change in Cash = Operating + Investing + Financing
    operating = find_concepts(['NetCashProvidedByUsedInOperatingActivities'])
    investing = find_concepts(['NetCashProvidedByUsedInInvestingActivities'])
    financing = find_concepts(['NetCashProvidedByUsedInFinancingActivities'])
    net_change = find_concepts(['CashCashEquivalentsPeriodIncreaseDecrease', 'CashAndCashEquivalentsPeriodIncreaseDecrease'])

    if net_change:
        children = []
        for c in operating[:1]:
            children.append({"concept": c, "label": get_label(c), "weight": 1.0, "order": 1})
        for c in investing[:1]:
            children.append({"concept": c, "label": get_label(c), "weight": 1.0, "order": 2})
        for c in financing[:1]:
            children.append({"concept": c, "label": get_label(c), "weight": 1.0, "order": 3})
        if children:
            calculations[net_change[0]] = {
                "parent_concept": net_change[0],
                "parent_label": get_label(net_change[0]),
                "children": children
            }

    return calculations


def _is_text_block(concept: str) -> bool:
    """Check if concept is a text block (narrative disclosure)."""
    if not concept:
        return False
    c_lower = concept.lower()
    return 'textblock' in c_lower or 'policytext' in c_lower or 'tabletext' in c_lower


def _collect_concepts_from_tree(nodes: list) -> set:
    """Recursively collect all concept names from presentation tree nodes."""
    concepts = set()
    for node in nodes:
        if isinstance(node, dict):
            concept = node.get("concept")
            # Skip text block concepts
            if concept and not _is_text_block(concept):
                concepts.add(concept)
            concepts.update(_collect_concepts_from_tree(node.get("children", [])))
    return concepts


def _filter_tree_nodes(nodes: list) -> list:
    """Recursively filter out text block nodes from presentation trees."""
    filtered = []
    for node in nodes:
        if isinstance(node, dict):
            concept = node.get("concept", "")
            # Skip text block concepts
            if _is_text_block(concept):
                continue
            # Filter children recursively
            new_node = dict(node)
            new_node["children"] = _filter_tree_nodes(node.get("children", []))
            filtered.append(new_node)
    return filtered


def _build_raw_response(
    parsed: dict,
    cik: int | str,
    accession_number: str,
    filing_date: date,
    form_type: str,
) -> RawXBRLResponse:
    """Build RawXBRLResponse from parsed XBRL data."""
    metadata = parsed.get("metadata", {})
    presentation = parsed.get("presentation_trees", {})
    calculations = parsed.get("calculation_relationships", {})
    all_facts = parsed.get("all_facts", {})
    labels = parsed.get("labels", {})

    # Use fallback if presentation is empty
    has_presentation = any(
        presentation.get(k) for k in ["balance_sheet", "income_statement", "cash_flow"]
    )
    if not has_presentation and all_facts:
        presentation = _build_fallback_presentation(all_facts, labels)

    # Filter out text block concepts from presentation trees
    for key in ["balance_sheet", "income_statement", "cash_flow", "equity_statement", "other"]:
        if key in presentation:
            presentation[key] = _filter_tree_nodes(presentation[key])

    # Use fallback if calculations are empty
    if not calculations and all_facts:
        calculations = _build_fallback_calculations(all_facts, labels)

    # Filter text blocks from calculations too
    filtered_calculations = {}
    for parent, calc_data in calculations.items():
        if _is_text_block(parent):
            continue
        filtered_children = [c for c in calc_data.get("children", []) if not _is_text_block(c.get("concept", ""))]
        if filtered_children:
            filtered_calculations[parent] = {
                "parent_concept": calc_data.get("parent_concept", parent),
                "parent_label": calc_data.get("parent_label", parent),
                "children": filtered_children
            }
    calculations = filtered_calculations

    # Collect all concepts used in presentation trees
    used_concepts = set()
    for key in ["balance_sheet", "income_statement", "cash_flow", "equity_statement", "other"]:
        used_concepts.update(_collect_concepts_from_tree(presentation.get(key, [])))

    # Also include concepts from calculations
    for parent, calc_data in calculations.items():
        used_concepts.add(parent)
        for child in calc_data.get("children", []):
            if child.get("concept"):
                used_concepts.add(child["concept"])

    # Convert presentation trees to PresentationNode models
    def convert_tree(node: dict) -> PresentationNode:
        return PresentationNode(
            concept=node.get("concept", ""),
            label=node.get("label", ""),
            level=node.get("level", 0),
            is_abstract=node.get("is_abstract", False),
            children=[convert_tree(c) for c in node.get("children", [])],
        )

    # Convert calculation relationships
    calc_response = {}
    for parent, calc_data in calculations.items():
        calc_response[parent] = CalculationRelationship(
            parent_concept=calc_data.get("parent_concept", parent),
            parent_label=calc_data.get("parent_label", parent),
            children=[
                CalculationChild(
                    concept=c.get("concept", ""),
                    label=c.get("label", ""),
                    weight=c.get("weight", 1.0),
                    order=c.get("order", 0.0),
                )
                for c in calc_data.get("children", [])
            ],
        )

    # Convert facts - ONLY for concepts used in presentation/calculations
    facts_response = {}
    for concept in used_concepts:
        if concept in all_facts:
            facts_response[concept] = [
                XBRLFact(
                    concept=concept,
                    label=labels.get(concept, concept),
                    value=f.get("value"),
                    unit=f.get("unit"),
                    period_end=f.get("period_end"),
                    period_start=f.get("period_start"),
                    dimensions=f.get("dimensions", {}),
                    decimals=f.get("decimals"),
                )
                for f in all_facts[concept]
            ]

    # Filter labels to only include used concepts
    filtered_labels = {k: v for k, v in labels.items() if k in used_concepts}

    return RawXBRLResponse(
        cik=str(cik),
        accession_number=accession_number,
        filing_date=filing_date,
        form_type=form_type,
        fiscal_year=metadata.get("fiscal_year"),
        fiscal_period=metadata.get("fiscal_period"),
        period_end=metadata.get("document_period_end") or filing_date,
        balance_sheet=[convert_tree(t) for t in presentation.get("balance_sheet", [])],
        income_statement=[convert_tree(t) for t in presentation.get("income_statement", [])],
        cash_flow=[convert_tree(t) for t in presentation.get("cash_flow", [])],
        equity_statement=[convert_tree(t) for t in presentation.get("equity_statement", [])],
        other_statements=[convert_tree(t) for t in presentation.get("other", [])],
        calculations=calc_response,
        facts=facts_response,
        labels=filtered_labels,
    )


@router.get("/filings")
async def get_available_filings(
    cik: int = Query(..., description="Company CIK number"),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Get list of ALL available 10-K and 10-Q filings for a company.

    Returns metadata for each filing that can be used to fetch detailed XBRL data.
    """
    extractor = FinancialExtractor(db)
    filings = await extractor.get_all_filings(cik)

    response = AvailableFilingsResponse(
        cik=str(cik),
        filings=[
            FinancialFilingSummary(
                accession_number=f["accession_number"],
                filing_date=f["filing_date"],
                form_type=f["form_type"],
                fiscal_year=f.get("fiscal_year"),
                fiscal_period=f.get("fiscal_period"),
            )
            for f in filings
        ],
        total_count=len(filings),
    )
    return response.model_dump(by_alias=True, mode="json")


@router.get("/history")
async def get_financial_history(
    cik: int = Query(..., description="Company CIK number"),
    concepts: str = Query(..., description="Comma-separated list of XBRL concept names"),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Get historical values for specific XBRL concepts across all filings.

    Use this endpoint to chart metrics over time. Pass concept names
    (e.g., "Assets,Revenues,NetIncomeLoss") to retrieve their historical values.
    """
    extractor = FinancialExtractor(db)

    concept_list = [c.strip() for c in concepts.split(",") if c.strip()]
    if not concept_list:
        raise HTTPException(status_code=400, detail="At least one concept name is required")

    history = await extractor.get_historical_values(cik, concept_list)

    # Convert to response format
    concepts_response = {}
    total_filings = 0

    for concept, data_points in history.items():
        concepts_response[concept] = [
            HistoricalDataPoint(
                filing_date=dp["filing_date"],
                period_end=dp["period_end"],
                fiscal_year=dp.get("fiscal_year"),
                fiscal_period=dp.get("fiscal_period"),
                form_type=dp["form_type"],
                value=dp["value"],
                accession_number=dp["accession_number"],
            )
            for dp in data_points
        ]
        total_filings = max(total_filings, len(data_points))

    response = FinancialHistoryResponse(
        cik=str(cik),
        concepts=concepts_response,
        total_filings=total_filings,
    )
    return response.model_dump(by_alias=True, mode="json")


@router.get("/export/excel")
async def export_to_excel(
    cik: int = Query(..., description="Company CIK number"),
    accession_number: Optional[str] = Query(None, description="Specific filing accession number"),
    company_name: Optional[str] = Query(None, description="Company name for the export"),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Export financial data to Excel format.

    Returns an .xlsx file with multiple sheets containing financial statements
    organized by their presentation hierarchy.
    """
    extractor = FinancialExtractor(db)

    # Get filing info
    if not accession_number:
        filing_info = await extractor.find_latest_10k(cik)
        if not filing_info:
            filing_info = await extractor.find_latest_10q(cik)
        if not filing_info:
            raise HTTPException(status_code=404, detail=f"No filings found for CIK {cik}")
        accession_number, filing_date, form_type = filing_info
    else:
        filing_info = await extractor.get_filing_info(cik, accession_number)
        if not filing_info:
            raise HTTPException(status_code=404, detail=f"Filing {accession_number} not found")
        filing_date, form_type = filing_info

    # Get or parse XBRL data
    cached = await extractor.get_raw_xbrl_data(cik, accession_number)
    if not cached:
        parser = XBRLParser()
        try:
            cached = parser.parse_filing_full(cik, accession_number, filing_date)
        except FileNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))

    # Use provided company name or empty string
    company_name = company_name or ""

    # Generate Excel file
    try:
        from ...services.excel_export import ExcelExporter
        exporter = ExcelExporter()
        excel_bytes = exporter.export_filing(
            cached, cik, accession_number, filing_date, form_type, company_name
        )
    except ImportError:
        raise HTTPException(
            status_code=501,
            detail="Excel export not available. Please install openpyxl."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating Excel file: {str(e)}")

    # Return as downloadable file
    filename = f"financials_{cik}_{accession_number.replace('-', '')}.xlsx"
    return StreamingResponse(
        excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
