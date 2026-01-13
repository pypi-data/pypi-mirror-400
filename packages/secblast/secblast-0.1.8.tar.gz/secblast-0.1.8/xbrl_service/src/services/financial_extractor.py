"""
Financial data extractor service.
Handles database operations for financial statements.
"""

import logging
import time
from datetime import date, datetime
from typing import Dict, Any, Optional, List, Tuple
import json

from sqlalchemy import select, desc, text
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.database import FinancialStatement, XBRLFilingData
from .xbrl_parser import XBRLParser
from .cache_service import cache

logger = logging.getLogger(__name__)


class FinancialExtractor:
    """Extracts and stores financial data from XBRL filings."""

    # Shared parser instance (lazy-initialized)
    _shared_parser: Optional[XBRLParser] = None

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    @property
    def parser(self) -> XBRLParser:
        """Lazy-initialize the parser only when needed."""
        if FinancialExtractor._shared_parser is None:
            logger.info("Initializing shared XBRLParser...")
            FinancialExtractor._shared_parser = XBRLParser()
        return FinancialExtractor._shared_parser

    async def find_latest_10k(self, cik: int) -> Optional[Tuple[str, date, str]]:
        """
        Find the latest 10-K or 10-K/A filing for a CIK from sb_filings table.
        Returns (accession_number, filing_date, form_type) or None if not found.
        """
        query = text("""
            SELECT accession_number, filing_date, form_type
            FROM sb_filings
            WHERE cik = :cik AND form_type IN ('10-K', '10-K/A')
            ORDER BY filing_date DESC
            LIMIT 1
        """)
        result = await self.db.execute(query, {"cik": str(cik)})
        row = result.fetchone()
        if row:
            return (row.accession_number, row.filing_date, row.form_type)
        return None

    async def find_latest_10q(self, cik: int) -> Optional[Tuple[str, date, str]]:
        """
        Find the latest 10-Q filing for a CIK from sb_filings table.
        Returns (accession_number, filing_date, form_type) or None if not found.
        """
        query = text("""
            SELECT accession_number, filing_date, form_type
            FROM sb_filings
            WHERE cik = :cik AND form_type IN ('10-Q', '10-Q/A')
            ORDER BY filing_date DESC
            LIMIT 1
        """)
        result = await self.db.execute(query, {"cik": str(cik)})
        row = result.fetchone()
        if row:
            return (row.accession_number, row.filing_date, row.form_type)
        return None

    async def _ensure_parsed(self, cik: int, prefer_annual: bool = True) -> bool:
        """
        Ensure financial data exists for a CIK by parsing the latest filing if needed.
        Returns True if data exists or was successfully parsed.
        """
        # First try annual report (10-K), then quarterly (10-Q)
        filings_to_try = []

        if prefer_annual:
            filing_10k = await self.find_latest_10k(cik)
            if filing_10k:
                filings_to_try.append(filing_10k)
            filing_10q = await self.find_latest_10q(cik)
            if filing_10q:
                filings_to_try.append(filing_10q)
        else:
            filing_10q = await self.find_latest_10q(cik)
            if filing_10q:
                filings_to_try.append(filing_10q)
            filing_10k = await self.find_latest_10k(cik)
            if filing_10k:
                filings_to_try.append(filing_10k)

        for accession_number, filing_date, form_type in filings_to_try:
            try:
                logger.info(f"Auto-parsing {form_type} for CIK {cik}: {accession_number}")
                count = await self.parse_and_store(cik, accession_number, filing_date, form_type)
                if count > 0:
                    return True
            except FileNotFoundError as e:
                logger.warning(f"XBRL files not found for {accession_number}: {e}")
                continue
            except Exception as e:
                logger.error(f"Error parsing {accession_number}: {e}")
                continue

        return False

    async def get_financials(
        self,
        cik: int,
        statement_type: Optional[str] = None,
        accession_number: Optional[str] = None,
        limit: int = 10,
    ) -> List[FinancialStatement]:
        """Get financial statements for a company."""
        t0 = time.perf_counter()

        cache_key = cache.make_key("financials", cik, statement_type, accession_number, limit)
        cached = cache.get(cache_key)
        t1 = time.perf_counter()

        if cached:
            logger.info(f"TIMING get_financials cik={cik} type={statement_type}: cache_hit, cache_check={1000*(t1-t0):.1f}ms")
            return cached

        query = select(FinancialStatement).where(FinancialStatement.cik == cik)

        if statement_type:
            query = query.where(FinancialStatement.statement_type == statement_type)

        if accession_number:
            query = query.where(FinancialStatement.accession_number == accession_number)

        query = query.order_by(desc(FinancialStatement.filing_date)).limit(limit)

        t2 = time.perf_counter()
        result = await self.db.execute(query)
        t3 = time.perf_counter()

        statements = result.scalars().all()
        t4 = time.perf_counter()

        cache.set(cache_key, list(statements))
        t5 = time.perf_counter()

        logger.info(f"TIMING get_financials cik={cik} type={statement_type}: "
                    f"cache_check={1000*(t1-t0):.1f}ms, "
                    f"query_build={1000*(t2-t1):.1f}ms, "
                    f"db_execute={1000*(t3-t2):.1f}ms, "
                    f"scalars={1000*(t4-t3):.1f}ms, "
                    f"cache_set={1000*(t5-t4):.1f}ms, "
                    f"rows={len(statements)}")

        return list(statements)

    async def get_balance_sheet(
        self,
        cik: int,
        accession_number: Optional[str] = None,
    ) -> Optional[FinancialStatement]:
        """Get balance sheet for a company. Auto-parses if not found."""
        t0 = time.perf_counter()

        statements = await self.get_financials(
            cik, statement_type="balance_sheet", accession_number=accession_number, limit=1
        )
        t1 = time.perf_counter()
        logger.info(f"TIMING get_balance_sheet cik={cik}: get_financials={1000*(t1-t0):.1f}ms, found={bool(statements)}")

        if statements:
            return statements[0]

        # No data found - try to parse
        if accession_number:
            # Parse specific filing on-demand
            t2 = time.perf_counter()
            parsed = await self._parse_specific_filing(cik, accession_number)
            t3 = time.perf_counter()
            logger.info(f"TIMING get_balance_sheet cik={cik}: _parse_specific_filing={1000*(t3-t2):.1f}ms")
            if parsed:
                statements = await self.get_financials(
                    cik, statement_type="balance_sheet", accession_number=accession_number, limit=1
                )
                t4 = time.perf_counter()
                logger.info(f"TIMING get_balance_sheet cik={cik}: get_financials_after_parse={1000*(t4-t3):.1f}ms")
                return statements[0] if statements else None
        else:
            # Parse latest filing
            t2 = time.perf_counter()
            parsed = await self._ensure_parsed(cik, prefer_annual=True)
            t3 = time.perf_counter()
            logger.info(f"TIMING get_balance_sheet cik={cik}: _ensure_parsed={1000*(t3-t2):.1f}ms")
            if parsed:
                statements = await self.get_financials(
                    cik, statement_type="balance_sheet", limit=1
                )
                t4 = time.perf_counter()
                logger.info(f"TIMING get_balance_sheet cik={cik}: get_financials_after_parse={1000*(t4-t3):.1f}ms")
                return statements[0] if statements else None

        return None

    async def get_income_statement(
        self,
        cik: int,
        accession_number: Optional[str] = None,
    ) -> Optional[FinancialStatement]:
        """Get income statement for a company. Auto-parses if not found."""
        statements = await self.get_financials(
            cik, statement_type="income_statement", accession_number=accession_number, limit=1
        )
        if statements:
            return statements[0]

        # No data found - try to parse
        if accession_number:
            # Parse specific filing on-demand
            parsed = await self._parse_specific_filing(cik, accession_number)
            if parsed:
                statements = await self.get_financials(
                    cik, statement_type="income_statement", accession_number=accession_number, limit=1
                )
                return statements[0] if statements else None
        else:
            # Parse latest filing
            parsed = await self._ensure_parsed(cik, prefer_annual=True)
            if parsed:
                statements = await self.get_financials(
                    cik, statement_type="income_statement", limit=1
                )
                return statements[0] if statements else None

        return None

    async def get_cash_flow(
        self,
        cik: int,
        accession_number: Optional[str] = None,
    ) -> Optional[FinancialStatement]:
        """Get cash flow statement for a company. Auto-parses if not found."""
        statements = await self.get_financials(
            cik, statement_type="cash_flow", accession_number=accession_number, limit=1
        )
        if statements:
            return statements[0]

        # No data found - try to parse
        if accession_number:
            # Parse specific filing on-demand
            parsed = await self._parse_specific_filing(cik, accession_number)
            if parsed:
                statements = await self.get_financials(
                    cik, statement_type="cash_flow", accession_number=accession_number, limit=1
                )
                return statements[0] if statements else None
        else:
            # Parse latest filing
            parsed = await self._ensure_parsed(cik, prefer_annual=True)
            if parsed:
                statements = await self.get_financials(
                    cik, statement_type="cash_flow", limit=1
                )
                return statements[0] if statements else None

        return None

    async def _parse_specific_filing(self, cik: int, accession_number: str) -> bool:
        """
        Parse a specific filing by accession number.
        Returns True if data exists or was successfully parsed.
        """
        # First check if data already exists (avoid redundant parsing)
        existing = await self.get_financials(cik, accession_number=accession_number, limit=1)
        if existing:
            return True

        # Get filing info from sb_filings
        filing_info = await self.get_filing_info(cik, accession_number)
        if not filing_info:
            logger.warning(f"Filing {accession_number} not found for CIK {cik}")
            return False

        filing_date, form_type = filing_info

        try:
            logger.info(f"On-demand parsing {form_type} for CIK {cik}: {accession_number}")
            count = await self.parse_and_store(cik, accession_number, filing_date, form_type)
            # count >= 0 means success (0 = already parsed, >0 = newly parsed)
            # count == -1 means already exists (concurrent insert handled in parse_and_store)
            return True
        except FileNotFoundError as e:
            logger.warning(f"XBRL files not found for {accession_number}: {e}")
            return False
        except Exception as e:
            # Rollback session on any error to prevent PendingRollbackError
            await self.db.rollback()
            logger.error(f"Error parsing {accession_number}: {e}")
            return False

    async def get_filing_summaries(self, cik: int, limit: int = 20) -> List[Dict[str, Any]]:
        """Get list of filings with financial data for a company."""
        query = (
            select(
                FinancialStatement.accession_number,
                FinancialStatement.filing_date,
                FinancialStatement.form_type,
                FinancialStatement.fiscal_year,
                FinancialStatement.fiscal_period,
            )
            .where(FinancialStatement.cik == cik)
            .distinct(FinancialStatement.accession_number)
            .order_by(
                FinancialStatement.accession_number,
                desc(FinancialStatement.filing_date),
            )
            .limit(limit)
        )

        result = await self.db.execute(query)
        rows = result.fetchall()

        return [
            {
                "accession_number": row.accession_number,
                "filing_date": row.filing_date,
                "form_type": row.form_type,
                "fiscal_year": row.fiscal_year,
                "fiscal_period": row.fiscal_period,
            }
            for row in rows
        ]

    async def parse_and_store(
        self,
        cik: int,
        accession_number: str,
        filing_date: date,
        form_type: str,
    ) -> int:
        """Parse XBRL filing and store financial statements."""
        # Check if already parsed
        existing = await self.get_financials(cik, accession_number=accession_number, limit=1)
        if existing:
            logger.info(f"Filing {accession_number} already parsed, skipping")
            return 0

        # Parse the XBRL
        try:
            parsed = self.parser.parse_filing(cik, accession_number, filing_date)
        except FileNotFoundError as e:
            logger.warning(f"XBRL files not found: {e}")
            return 0
        except Exception as e:
            logger.error(f"Error parsing XBRL: {e}")
            raise

        metadata = parsed["metadata"]
        statements_created = 0

        # Store each statement type
        for stmt_type, data in [
            ("balance_sheet", parsed["balance_sheet"]),
            ("income_statement", parsed["income_statement"]),
            ("cash_flow", parsed["cash_flow"]),
        ]:
            if not data:
                continue

            statement = FinancialStatement(
                cik=cik,
                accession_number=accession_number,
                filing_date=filing_date,
                form_type=form_type,
                fiscal_year=metadata.get("fiscal_year"),
                fiscal_period=metadata.get("fiscal_period"),
                statement_type=stmt_type,
                period_end=metadata.get("document_period_end") or filing_date,
                currency=metadata.get("currency", "USD"),
                data=data,
            )

            self.db.add(statement)
            statements_created += 1

        try:
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            # Check if it's a duplicate key error (race condition)
            error_str = str(e).lower()
            if "unique" in error_str or "duplicate" in error_str or "integrityerror" in error_str:
                logger.info(f"Filing {accession_number} already exists (concurrent insert)")
                return -1  # Special value: already exists
            raise

        # Clear cache for this CIK
        cache.delete(cache.make_key("financials", cik))

        logger.info(f"Stored {statements_created} statements for {accession_number}")
        return statements_created

    # ========== NEW METHODS FOR FULL XBRL ==========

    async def get_filing_info(self, cik: int, accession_number: str) -> Optional[Tuple[date, str]]:
        """
        Get filing info (filing_date, form_type) for a specific accession number.
        Returns None if not found.
        """
        query = text("""
            SELECT filing_date, form_type
            FROM sb_filings
            WHERE cik = :cik AND accession_number = :accession_number
            LIMIT 1
        """)
        result = await self.db.execute(query, {"cik": str(cik), "accession_number": accession_number})
        row = result.fetchone()
        if row:
            return (row.filing_date, row.form_type)
        return None

    async def get_raw_xbrl_data(self, cik: int, accession_number: str) -> Optional[Dict[str, Any]]:
        """
        Get raw XBRL data from the xbrl_filing_data table.
        Returns the parsed data dict or None if not found.
        """
        cache_key = cache.make_key("raw_xbrl", cik, accession_number)
        cached = cache.get(cache_key)
        if cached:
            return cached

        query = select(XBRLFilingData).where(
            XBRLFilingData.cik == cik,
            XBRLFilingData.accession_number == accession_number,
        )
        result = await self.db.execute(query)
        record = result.scalar_one_or_none()

        if record:
            data = {
                "all_facts": record.all_facts,
                "presentation_trees": record.presentation_trees,
                "calculation_relationships": record.calculation_relationships,
                "labels": record.labels,
                "metadata": {
                    "fiscal_year": record.fiscal_year,
                    "fiscal_period": record.fiscal_period,
                    "document_period_end": record.period_end,
                },
            }
            cache.set(cache_key, data)
            return data

        return None

    def _ensure_json_serializable(self, obj: Any) -> Any:
        """Recursively convert all non-JSON-serializable objects to strings."""
        if obj is None:
            return None
        if isinstance(obj, (str, int, float, bool)):
            return obj
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        if isinstance(obj, dict):
            return {str(k): self._ensure_json_serializable(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [self._ensure_json_serializable(item) for item in obj]
        # Fallback: convert to string with safety wrapper
        # Some Arelle objects have __repr__ that can throw exceptions
        try:
            # Try to get a sensible string representation
            if hasattr(obj, 'text'):
                return str(obj.text)
            if hasattr(obj, 'stringValue'):
                return str(obj.stringValue)
            if hasattr(obj, 'localName'):
                return str(obj.localName)
            return str(obj)
        except Exception:
            # If str() fails, return the type name
            return f"<{type(obj).__name__}>"

    async def store_raw_xbrl_data(
        self,
        cik: int,
        accession_number: str,
        filing_date: date,
        form_type: str,
        data: Dict[str, Any],
    ) -> None:
        """
        Store raw XBRL data in the xbrl_filing_data table.
        """
        metadata = data.get("metadata", {})

        # Ensure all data is JSON serializable
        all_facts = self._ensure_json_serializable(data.get("all_facts", {}))
        presentation_trees = self._ensure_json_serializable(data.get("presentation_trees", {}))
        calculation_relationships = self._ensure_json_serializable(data.get("calculation_relationships", {}))
        labels = self._ensure_json_serializable(data.get("labels", {}))

        # Parse period_end from metadata (it may be a string or date)
        period_end_val = metadata.get("document_period_end")
        if isinstance(period_end_val, str):
            try:
                period_end_val = datetime.strptime(period_end_val, "%Y-%m-%d").date()
            except ValueError:
                period_end_val = filing_date
        elif not period_end_val:
            period_end_val = filing_date

        record = XBRLFilingData(
            cik=cik,
            accession_number=accession_number,
            filing_date=filing_date,
            form_type=form_type,
            fiscal_year=metadata.get("fiscal_year"),
            fiscal_period=metadata.get("fiscal_period"),
            period_end=period_end_val,
            all_facts=all_facts,
            presentation_trees=presentation_trees,
            calculation_relationships=calculation_relationships,
            labels=labels,
        )

        self.db.add(record)
        await self.db.commit()

        # Update cache
        cache_key = cache.make_key("raw_xbrl", cik, accession_number)
        cache.set(cache_key, data)

        logger.info(f"Stored raw XBRL data for {accession_number}")

    async def get_all_filings(self, cik: int) -> List[Dict[str, Any]]:
        """
        Get ALL 10-K and 10-Q filings for a company from sb_filings.
        Returns list of filing summaries sorted by filing date descending.
        """
        query = text("""
            SELECT accession_number, filing_date, form_type
            FROM sb_filings
            WHERE cik = :cik AND form_type IN ('10-K', '10-K/A', '10-Q', '10-Q/A')
            ORDER BY filing_date DESC
        """)
        result = await self.db.execute(query, {"cik": str(cik)})
        rows = result.fetchall()

        return [
            {
                "accession_number": row.accession_number,
                "filing_date": row.filing_date,
                "form_type": row.form_type,
                "fiscal_year": None,  # Would need to parse or look up
                "fiscal_period": None,
            }
            for row in rows
        ]

    async def get_historical_values(
        self,
        cik: int,
        concepts: List[str],
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get historical values for specific concepts across all filings.
        Returns dict with concept names as keys, each containing a list of data points.
        """
        history = {concept: [] for concept in concepts}

        # Get all stored XBRL data for this CIK
        query = select(XBRLFilingData).where(
            XBRLFilingData.cik == cik
        ).order_by(desc(XBRLFilingData.filing_date))

        result = await self.db.execute(query)
        filings = result.scalars().all()

        for filing in filings:
            all_facts = filing.all_facts or {}

            for concept in concepts:
                if concept not in all_facts:
                    continue

                facts = all_facts[concept]
                # Get the best fact (no dimensions, matching period)
                best_fact = self._select_best_fact_for_history(facts, filing.period_end)

                if best_fact and best_fact.get("value") is not None:
                    history[concept].append({
                        "filing_date": filing.filing_date,
                        "period_end": filing.period_end,
                        "fiscal_year": filing.fiscal_year,
                        "fiscal_period": filing.fiscal_period,
                        "form_type": filing.form_type,
                        "value": best_fact["value"],
                        "accession_number": filing.accession_number,
                    })

        return history

    def _select_best_fact_for_history(
        self,
        facts: List[Dict[str, Any]],
        target_period: Optional[date],
    ) -> Optional[Dict[str, Any]]:
        """Select the best fact for historical data (no dimensions, matching period)."""
        if not facts:
            return None

        # Filter to facts without dimensions
        no_dim_facts = [f for f in facts if not f.get("dimensions")]
        candidates = no_dim_facts if no_dim_facts else facts

        if not candidates:
            return None

        # Prefer facts matching the target period
        if target_period:
            matching = [
                f for f in candidates
                if f.get("period_end") == target_period
            ]
            if matching:
                return matching[0]

        # Return most recent fact
        dated = [f for f in candidates if f.get("period_end")]
        if dated:
            dated.sort(key=lambda x: x.get("period_end") or date.min, reverse=True)
            return dated[0]

        return candidates[0] if candidates else None
