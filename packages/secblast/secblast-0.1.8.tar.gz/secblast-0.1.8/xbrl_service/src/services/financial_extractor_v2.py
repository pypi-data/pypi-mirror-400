"""
Financial data extractor v2 - uses new sb_xbrl_* tables.
"""

import logging
from datetime import date
from typing import Dict, Any, Optional, List, Tuple

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class FinancialExtractorV2:
    """Extracts financial data from the new sb_xbrl_* tables."""

    # Map API statement types to database statement types
    STATEMENT_TYPE_MAP = {
        "balance_sheet": ["BalanceSheet"],
        "income_statement": ["IncomeStatement", "ComprehensiveIncome"],
        "cash_flow": ["CashFlow"],
    }

    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def get_statement(
        self,
        cik: int,
        statement_type: str,
        accession_number: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Get a financial statement for a company.

        Args:
            cik: Company CIK number
            statement_type: One of 'balance_sheet', 'income_statement', 'cash_flow'
            accession_number: Optional specific filing accession number

        Returns:
            Dictionary with statement data or None if not found
        """
        # Get the statement types to query
        db_types = self.STATEMENT_TYPE_MAP.get(statement_type, [statement_type])
        types_str = ",".join([f"'{t}'" for t in db_types])

        # Find the relevant statement and filing
        if accession_number:
            stmt_query = text(f"""
                SELECT s.id, s.accession_number, s.filing_date, s.role_uri,
                       s.short_name, s.statement_type, f.form_type
                FROM sb_xbrl_statements s
                JOIN sb_filings f ON s.accession_number = f.accession_number AND s.cik = f.cik
                WHERE s.cik = :cik
                  AND s.accession_number = :accession_number
                  AND s.statement_type IN ({types_str})
                ORDER BY s.position
                LIMIT 1
            """)
            result = await self.db.execute(stmt_query, {
                "cik": str(cik),
                "accession_number": accession_number
            })
        else:
            # Get most recent 10-K or 10-Q
            stmt_query = text(f"""
                SELECT s.id, s.accession_number, s.filing_date, s.role_uri,
                       s.short_name, s.statement_type, f.form_type
                FROM sb_xbrl_statements s
                JOIN sb_filings f ON s.accession_number = f.accession_number AND s.cik = f.cik
                WHERE s.cik = :cik
                  AND s.statement_type IN ({types_str})
                  AND f.form_type IN ('10-K', '10-K/A', '10-Q', '10-Q/A')
                ORDER BY s.filing_date DESC, s.position
                LIMIT 1
            """)
            result = await self.db.execute(stmt_query, {"cik": str(cik)})

        row = result.fetchone()
        if not row:
            return None

        statement_id = row.id
        accession_number = row.accession_number
        filing_date = row.filing_date
        form_type = row.form_type
        short_name = row.short_name

        # Get facts for this statement
        facts = await self._get_statement_facts(cik, accession_number, statement_id)

        # Get period information
        periods = await self._get_periods(cik, accession_number)

        # Build response
        return {
            "cik": str(cik),
            "accession_number": accession_number,
            "filing_date": filing_date,
            "form_type": form_type,
            "statement_type": statement_type,
            "short_name": short_name,
            "periods": periods,
            "line_items": facts,
        }

    async def _get_statement_facts(
        self,
        cik: int,
        accession_number: str,
        statement_id: int,
    ) -> List[Dict[str, Any]]:
        """Get facts for a specific statement, ordered by presentation order."""
        query = text("""
            SELECT
                f.local_name as concept,
                f.value,
                f.unit,
                f.period_end,
                f.period_start,
                f.period_type,
                f.is_primary,
                f.decimals,
                f.presentation_order
            FROM sb_xbrl_facts f
            WHERE f.accession_number = :accession_number
              AND f.cik = :cik
              AND f.statement_id = :statement_id
              AND f.is_primary = TRUE
              AND f.value IS NOT NULL
            ORDER BY f.presentation_order, f.local_name, f.period_end DESC
        """)

        result = await self.db.execute(query, {
            "accession_number": accession_number,
            "cik": str(cik),
            "statement_id": statement_id,
        })

        rows = result.fetchall()

        # Group by concept
        concepts = {}
        for row in rows:
            concept = row.concept
            if concept not in concepts:
                concepts[concept] = {
                    "concept": concept,
                    "label": self._format_label(concept),
                    "values": [],
                }

            concepts[concept]["values"].append({
                "period_end": row.period_end.isoformat() if row.period_end else None,
                "period_start": row.period_start.isoformat() if row.period_start else None,
                "value": float(row.value) if row.value is not None else None,
                "unit": row.unit,
            })

        return list(concepts.values())

    async def _get_periods(self, cik: int, accession_number: str) -> List[Dict[str, Any]]:
        """Get unique periods for a filing."""
        query = text("""
            SELECT DISTINCT period_end, period_start, period_type
            FROM sb_xbrl_facts
            WHERE accession_number = :accession_number
              AND cik = :cik
              AND is_primary = TRUE
              AND period_end IS NOT NULL
            ORDER BY period_end DESC
        """)

        result = await self.db.execute(query, {
            "accession_number": accession_number,
            "cik": str(cik),
        })

        return [
            {
                "period_end": row.period_end.isoformat() if row.period_end else None,
                "period_start": row.period_start.isoformat() if row.period_start else None,
                "period_type": row.period_type,
            }
            for row in result.fetchall()
        ]

    def _format_label(self, concept: str) -> str:
        """Convert camelCase concept to readable label."""
        import re
        # Insert space before capitals
        result = re.sub(r'([a-z])([A-Z])', r'\1 \2', concept)
        # Handle consecutive capitals
        result = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1 \2', result)
        return result

    async def get_balance_sheet(
        self,
        cik: int,
        accession_number: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Get balance sheet for a company."""
        return await self.get_statement(cik, "balance_sheet", accession_number)

    async def get_income_statement(
        self,
        cik: int,
        accession_number: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Get income statement for a company."""
        return await self.get_statement(cik, "income_statement", accession_number)

    async def get_cash_flow(
        self,
        cik: int,
        accession_number: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Get cash flow statement for a company."""
        return await self.get_statement(cik, "cash_flow", accession_number)

    async def get_statement_table(
        self,
        cik: int,
        statement_type: str,
        accession_number: Optional[str] = None,
        limit_periods: int = 5,
    ) -> Optional[Dict[str, Any]]:
        """
        Get a financial statement in table format for easy rendering.

        Returns data structured as:
        {
            "columns": ["2024-09-28", "2023-09-30", ...],
            "rows": [
                {"concept": "Assets", "label": "Assets", "values": [364980000000, 352583000000, ...]},
                ...
            ]
        }

        For balance sheets, uses instant periods.
        For income/cash flow, uses duration periods matching the fiscal year/quarter.
        """
        # Get the raw statement first
        statement = await self.get_statement(cik, statement_type, accession_number)
        if not statement:
            return None

        line_items = statement.get("line_items", [])
        if not line_items:
            return statement

        # Determine period filter based on statement type
        # Balance sheets use instant (point-in-time), income/cash use duration
        is_balance_sheet = statement_type == "balance_sheet"

        # Extract all unique periods and determine columns
        period_set = set()
        for item in line_items:
            for v in item["values"]:
                if is_balance_sheet:
                    # For balance sheet, only use instant periods (period_start is None)
                    if v["period_start"] is None:
                        period_set.add(v["period_end"])
                else:
                    # For income/cash flow, use duration periods
                    # Prefer annual or quarterly durations
                    if v["period_start"] is not None:
                        period_set.add(v["period_end"])

        # Sort periods descending (most recent first) and limit
        columns = sorted(period_set, reverse=True)[:limit_periods]

        # Build rows with values aligned to columns
        rows = []
        for item in line_items:
            # Build period -> value map
            if is_balance_sheet:
                period_values = {
                    v["period_end"]: v["value"]
                    for v in item["values"]
                    if v["period_start"] is None
                }
            else:
                period_values = {
                    v["period_end"]: v["value"]
                    for v in item["values"]
                    if v["period_start"] is not None
                }

            # Get values for each column (None if missing)
            values = [period_values.get(col) for col in columns]

            # Only include rows that have at least one value
            if any(v is not None for v in values):
                rows.append({
                    "concept": item["concept"],
                    "label": item["label"],
                    "values": values,
                    "unit": item["values"][0]["unit"] if item["values"] else "usd",
                })

        return {
            "cik": statement["cik"],
            "accession_number": statement["accession_number"],
            "filing_date": statement["filing_date"],
            "form_type": statement["form_type"],
            "statement_type": statement_type,
            "short_name": statement.get("short_name"),
            "columns": columns,
            "rows": rows,
        }

    async def get_raw_xbrl(
        self,
        cik: int,
        accession_number: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Get complete raw XBRL data for a filing.

        Returns all facts organized by statement with presentation structure.
        """
        # Find the filing
        if accession_number:
            filing_query = text("""
                SELECT accession_number, filing_date, form_type
                FROM sb_filings
                WHERE cik = :cik AND accession_number = :accession_number
                LIMIT 1
            """)
            result = await self.db.execute(filing_query, {
                "cik": str(cik),
                "accession_number": accession_number,
            })
        else:
            filing_query = text("""
                SELECT accession_number, filing_date, form_type
                FROM sb_filings
                WHERE cik = :cik AND form_type IN ('10-K', '10-K/A', '10-Q', '10-Q/A')
                ORDER BY filing_date DESC
                LIMIT 1
            """)
            result = await self.db.execute(filing_query, {"cik": str(cik)})

        row = result.fetchone()
        if not row:
            return None

        accession_number = row.accession_number
        filing_date = row.filing_date
        form_type = row.form_type

        # Get all statements for this filing
        statements_query = text("""
            SELECT id, role_uri, short_name, long_name, statement_type, position
            FROM sb_xbrl_statements
            WHERE accession_number = :accession_number AND cik = :cik
            ORDER BY position
        """)
        statements_result = await self.db.execute(statements_query, {
            "accession_number": accession_number,
            "cik": str(cik),
        })
        statements = statements_result.fetchall()

        # Get all primary facts for this filing
        facts_query = text("""
            SELECT
                f.local_name as concept,
                f.value,
                f.unit,
                f.period_end,
                f.period_start,
                f.period_type,
                f.statement_id,
                f.decimals
            FROM sb_xbrl_facts f
            WHERE f.accession_number = :accession_number
              AND f.cik = :cik
              AND f.is_primary = TRUE
              AND f.value IS NOT NULL
            ORDER BY f.statement_id, f.period_end DESC
        """)
        facts_result = await self.db.execute(facts_query, {
            "accession_number": accession_number,
            "cik": str(cik),
        })
        facts = facts_result.fetchall()

        # Group facts by statement
        facts_by_statement = {}
        for fact in facts:
            stmt_id = fact.statement_id
            if stmt_id not in facts_by_statement:
                facts_by_statement[stmt_id] = {}

            concept = fact.concept
            if concept not in facts_by_statement[stmt_id]:
                facts_by_statement[stmt_id][concept] = []

            facts_by_statement[stmt_id][concept].append({
                "value": float(fact.value) if fact.value else None,
                "unit": fact.unit,
                "period_end": fact.period_end.isoformat() if fact.period_end else None,
                "period_start": fact.period_start.isoformat() if fact.period_start else None,
                "decimals": fact.decimals,
            })

        # Build response organized by statement type
        result_statements = {
            "balance_sheet": [],
            "income_statement": [],
            "cash_flow": [],
            "other": [],
        }

        for stmt in statements:
            stmt_type = stmt.statement_type
            stmt_facts = facts_by_statement.get(stmt.id, {})

            stmt_data = {
                "role_uri": stmt.role_uri,
                "short_name": stmt.short_name,
                "long_name": stmt.long_name,
                "facts": stmt_facts,
            }

            if stmt_type == "BalanceSheet":
                result_statements["balance_sheet"].append(stmt_data)
            elif stmt_type in ("IncomeStatement", "ComprehensiveIncome"):
                result_statements["income_statement"].append(stmt_data)
            elif stmt_type == "CashFlow":
                result_statements["cash_flow"].append(stmt_data)
            else:
                result_statements["other"].append(stmt_data)

        return {
            "cik": str(cik),
            "accession_number": accession_number,
            "filing_date": filing_date.isoformat() if filing_date else None,
            "form_type": form_type,
            "statements": result_statements,
        }

    async def get_filings(self, cik: int) -> List[Dict[str, Any]]:
        """Get list of all available filings with XBRL data."""
        query = text("""
            SELECT DISTINCT ON (s.accession_number)
                s.accession_number,
                s.filing_date,
                f.form_type
            FROM sb_xbrl_statements s
            JOIN sb_filings f ON s.accession_number = f.accession_number AND s.cik = f.cik
            WHERE s.cik = :cik
              AND f.form_type IN ('10-K', '10-K/A', '10-Q', '10-Q/A')
            ORDER BY s.accession_number, s.filing_date DESC
        """)

        result = await self.db.execute(query, {"cik": str(cik)})
        rows = result.fetchall()

        # Sort by filing date descending
        filings = [
            {
                "accession_number": row.accession_number,
                "filing_date": row.filing_date.isoformat() if row.filing_date else None,
                "form_type": row.form_type,
            }
            for row in rows
        ]
        filings.sort(key=lambda x: x["filing_date"] or "", reverse=True)

        return filings

    async def get_history(
        self,
        cik: int,
        concepts: List[str],
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get historical values for specific concepts across all filings.
        """
        if not concepts:
            return {}

        # Build concept filter
        concept_placeholders = ",".join([f":concept_{i}" for i in range(len(concepts))])
        params = {"cik": str(cik)}
        for i, concept in enumerate(concepts):
            params[f"concept_{i}"] = concept

        query = text(f"""
            SELECT
                f.local_name as concept,
                f.value,
                f.period_end,
                f.filing_date,
                f.accession_number,
                fi.form_type
            FROM sb_xbrl_facts f
            JOIN sb_filings fi ON f.accession_number = fi.accession_number AND f.cik = fi.cik
            WHERE f.cik = :cik
              AND f.local_name IN ({concept_placeholders})
              AND f.is_primary = TRUE
              AND f.value IS NOT NULL
            ORDER BY f.period_end DESC
        """)

        result = await self.db.execute(query, params)
        rows = result.fetchall()

        # Group by concept
        history = {concept: [] for concept in concepts}
        seen = {concept: set() for concept in concepts}

        for row in rows:
            concept = row.concept
            if concept not in history:
                continue

            # Deduplicate by period_end
            period_key = row.period_end.isoformat() if row.period_end else None
            if period_key in seen[concept]:
                continue
            seen[concept].add(period_key)

            history[concept].append({
                "period_end": period_key,
                "value": float(row.value) if row.value else None,
                "filing_date": row.filing_date.isoformat() if row.filing_date else None,
                "accession_number": row.accession_number,
                "form_type": row.form_type,
            })

        return history
