#!/usr/bin/env python3
"""
Test script for the new XBRL relational schema.
Processes one filing (AMD 10-K, accession 0000002488-25-000012) and shows results.
"""

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Optional, Dict, List
import psycopg2
from psycopg2.extras import execute_values, RealDictCursor
import json
import re
from datetime import date

# Database connection
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'dbname': 'secblast',
    'user': 'secblast',
    'password': 'secblast123'
}

# Test filing
TEST_ACCESSION = '0000002488-25-000012'
TEST_CIK = '2488'


# =============================================================================
# DDL - Create Tables
# =============================================================================

CREATE_TABLES_SQL = """
-- Drop existing tables if they exist (for testing)
DROP TABLE IF EXISTS sb_xbrl_facts CASCADE;
DROP TABLE IF EXISTS sb_xbrl_contexts CASCADE;
DROP TABLE IF EXISTS sb_xbrl_statements CASCADE;
DROP TABLE IF EXISTS sb_xbrl_concept_map CASCADE;
DROP MATERIALIZED VIEW IF EXISTS mv_xbrl_financials CASCADE;

-- Table: sb_xbrl_statements
CREATE TABLE sb_xbrl_statements (
    id SERIAL PRIMARY KEY,
    accession_number TEXT NOT NULL,
    cik TEXT NOT NULL,
    filing_date DATE,
    role_uri TEXT NOT NULL,
    short_name TEXT,
    long_name TEXT,
    menu_category TEXT,
    position INT,
    statement_type TEXT,
    UNIQUE(accession_number, role_uri)
);

CREATE INDEX idx_xbrl_statements_cik ON sb_xbrl_statements(cik);
CREATE INDEX idx_xbrl_statements_type ON sb_xbrl_statements(statement_type);
CREATE INDEX idx_xbrl_statements_accession ON sb_xbrl_statements(accession_number);
CREATE INDEX idx_xbrl_statements_cik_type ON sb_xbrl_statements(cik, statement_type);

-- Table: sb_xbrl_contexts
CREATE TABLE sb_xbrl_contexts (
    id SERIAL PRIMARY KEY,
    accession_number TEXT NOT NULL,
    cik TEXT NOT NULL,
    context_id TEXT NOT NULL,
    period_type TEXT,
    period_start DATE,
    period_end DATE,
    segment JSONB,
    UNIQUE(accession_number, context_id)
);

CREATE INDEX idx_xbrl_contexts_cik ON sb_xbrl_contexts(cik);
CREATE INDEX idx_xbrl_contexts_accession ON sb_xbrl_contexts(accession_number);
CREATE INDEX idx_xbrl_contexts_period ON sb_xbrl_contexts(period_end);
CREATE INDEX idx_xbrl_contexts_cik_period ON sb_xbrl_contexts(cik, period_end);

-- Table: sb_xbrl_facts
-- Deduplicated per Arelle OIM spec: unique on (accession, concept, context, unit)
CREATE TABLE sb_xbrl_facts (
    id BIGSERIAL PRIMARY KEY,
    accession_number TEXT NOT NULL,
    cik TEXT NOT NULL,
    filing_date DATE,
    concept TEXT NOT NULL,
    namespace TEXT,
    local_name TEXT,
    value NUMERIC,
    value_text TEXT,
    unit TEXT,
    decimals INT,
    context_id TEXT,
    period_type TEXT,
    period_start DATE,
    period_end DATE,
    segment JSONB,
    statement_id INT REFERENCES sb_xbrl_statements(id),
    is_primary BOOLEAN DEFAULT FALSE,
    is_extension BOOLEAN DEFAULT FALSE,
    -- Deduplication: A fact is uniquely identified by concept + context + unit
    UNIQUE(accession_number, local_name, context_id, unit)
);

CREATE INDEX idx_xbrl_facts_cik ON sb_xbrl_facts(cik);
CREATE INDEX idx_xbrl_facts_accession ON sb_xbrl_facts(accession_number);
CREATE INDEX idx_xbrl_facts_concept ON sb_xbrl_facts(local_name);
CREATE INDEX idx_xbrl_facts_concept_full ON sb_xbrl_facts(concept);
CREATE INDEX idx_xbrl_facts_statement ON sb_xbrl_facts(statement_id);
CREATE INDEX idx_xbrl_facts_period ON sb_xbrl_facts(period_end);
CREATE INDEX idx_xbrl_facts_primary ON sb_xbrl_facts(is_primary) WHERE is_primary = TRUE;
CREATE INDEX idx_xbrl_facts_cik_period ON sb_xbrl_facts(cik, period_end);
CREATE INDEX idx_xbrl_facts_cik_concept ON sb_xbrl_facts(cik, local_name);
CREATE INDEX idx_xbrl_facts_cik_primary ON sb_xbrl_facts(cik, is_primary) WHERE is_primary = TRUE;
CREATE INDEX idx_xbrl_facts_cik_period_primary ON sb_xbrl_facts(cik, period_end, is_primary) WHERE is_primary = TRUE;

-- Table: sb_xbrl_concept_map
CREATE TABLE sb_xbrl_concept_map (
    id SERIAL PRIMARY KEY,
    raw_concept TEXT UNIQUE NOT NULL,
    local_name TEXT,
    normalized_name TEXT,
    statement_type TEXT,
    line_order INT,
    is_primary BOOLEAN DEFAULT FALSE,
    description TEXT
);

CREATE INDEX idx_xbrl_concept_map_local ON sb_xbrl_concept_map(local_name);
CREATE INDEX idx_xbrl_concept_map_normalized ON sb_xbrl_concept_map(normalized_name);
CREATE INDEX idx_xbrl_concept_map_statement ON sb_xbrl_concept_map(statement_type);
"""


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class StatementInfo:
    role_uri: str
    short_name: str
    long_name: str
    menu_category: str
    position: int
    statement_type: str

@dataclass
class ContextInfo:
    context_id: str
    period_type: str
    period_start: Optional[str]
    period_end: str
    segment: Optional[dict]


# =============================================================================
# XBRL Processor
# =============================================================================

class XBRLProcessor:
    STATEMENT_PATTERNS = {
        'BalanceSheet': [
            r'balance\s*sheet', r'financial\s*position', r'assets.*liabilities'
        ],
        'IncomeStatement': [
            r'statement.*operations', r'income\s*statement', r'earnings',
            r'profit.*loss', r'statement.*income'
        ],
        'CashFlow': [
            r'cash\s*flow', r'statement.*cash'
        ],
        'Equity': [
            r'stockholders.*equity', r'shareholders.*equity', r'changes.*equity'
        ],
        'ComprehensiveIncome': [
            r'comprehensive\s*income'
        ]
    }

    BASE_NAMESPACES = [
        'http://fasb.org/us-gaap/',
        'http://fasb.org/srt/',
        'http://xbrl.sec.gov/dei/',
        'http://xbrl.sec.gov/ecd/',
    ]

    def __init__(self, conn):
        self.conn = conn

    def process_filing(self, accession_number: str, documents: Dict[str, str]) -> dict:
        """Process a filing and return stats."""
        stats = {'contexts': 0, 'statements': 0, 'facts_raw': 0, 'facts_deduplicated': 0}

        # 1. Parse FilingSummary.xml
        statements = self._parse_filing_summary(documents['filing_summary'])

        # 2. Parse instance document
        contexts, facts, cik_from_instance = self._parse_instance(documents['instance'])
        stats['facts_raw'] = len(facts)

        # 3. Parse presentation linkbase for fact-to-statement mapping
        fact_to_role = {}
        if 'presentation' in documents:
            fact_to_role = self._parse_presentation_linkbase(documents['presentation'])

        # 4. Get filing info from sb_filings
        filing_info = self._get_filing_info(accession_number)
        cik = filing_info['cik']
        filing_date = filing_info['filing_date']

        # 5. Insert contexts
        self._insert_contexts(accession_number, cik, contexts)
        stats['contexts'] = len(contexts)

        # 6. Insert statements
        stmt_id_map = self._insert_statements(accession_number, cik, filing_date, statements)
        stats['statements'] = len(statements)

        # 7. Insert facts (with deduplication)
        deduplicated_count = self._insert_facts(accession_number, cik, filing_date, facts, contexts, stmt_id_map, fact_to_role)
        stats['facts_deduplicated'] = deduplicated_count

        return stats

    def _get_filing_info(self, accession_number: str) -> dict:
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT cik, filing_date FROM sb_filings
                WHERE accession_number = %s
            """, (accession_number,))
            row = cur.fetchone()
            if row:
                return {'cik': row[0], 'filing_date': row[1]}
            raise ValueError(f"Filing not found: {accession_number}")

    def _parse_filing_summary(self, path: str) -> List[StatementInfo]:
        tree = ET.parse(path)
        root = tree.getroot()

        statements = []
        for report in root.findall('.//Report'):
            menu_category = report.findtext('MenuCategory', '')
            role_uri = report.findtext('Role', '')
            short_name = report.findtext('ShortName', '')
            long_name = report.findtext('LongName', '')
            position = int(report.findtext('Position', '0'))

            statement_type = self._classify_statement(role_uri, short_name)

            statements.append(StatementInfo(
                role_uri=role_uri,
                short_name=short_name,
                long_name=long_name,
                menu_category=menu_category,
                position=position,
                statement_type=statement_type
            ))

        return statements

    def _classify_statement(self, role_uri: str, short_name: str) -> str:
        combined = f"{role_uri} {short_name}".lower()

        for stmt_type, patterns in self.STATEMENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, combined, re.IGNORECASE):
                    return stmt_type

        return 'Other'

    def _parse_instance(self, path: str) -> tuple:
        tree = ET.parse(path)
        root = tree.getroot()

        cik = None
        contexts = {}

        for ctx in root.findall('.//{http://www.xbrl.org/2003/instance}context'):
            ctx_id = ctx.get('id')

            identifier = ctx.find('.//{http://www.xbrl.org/2003/instance}identifier')
            if identifier is not None and cik is None:
                cik = identifier.text

            period = ctx.find('.//{http://www.xbrl.org/2003/instance}period')
            instant = period.findtext('.//{http://www.xbrl.org/2003/instance}instant')
            start = period.findtext('.//{http://www.xbrl.org/2003/instance}startDate')
            end = period.findtext('.//{http://www.xbrl.org/2003/instance}endDate')

            segment = ctx.find('.//{http://www.xbrl.org/2003/instance}segment')
            dims = None
            if segment is not None:
                dims = {}
                for member in segment.findall('.//{http://xbrl.org/2006/xbrldi}explicitMember'):
                    dim = member.get('dimension')
                    dims[dim] = member.text

            contexts[ctx_id] = ContextInfo(
                context_id=ctx_id,
                period_type='instant' if instant else 'duration',
                period_start=start,
                period_end=instant or end,
                segment=dims
            )

        facts = []
        for elem in root.iter():
            ctx_ref = elem.get('contextRef')
            if ctx_ref is None:
                continue

            tag = elem.tag
            if tag.startswith('{'):
                ns, local = tag[1:].split('}', 1)
            else:
                ns, local = '', tag

            if ns in ['http://www.xbrl.org/2003/instance', 'http://www.xbrl.org/2003/linkbase']:
                continue

            unit_ref = elem.get('unitRef')
            decimals = elem.get('decimals', '0')

            try:
                value = float(elem.text) if elem.text else None
                value_text = None
            except (ValueError, TypeError):
                value = None
                value_text = elem.text

            prefix = self._get_namespace_prefix(ns)
            concept = f"{prefix}:{local}" if prefix else local

            is_extension = not any(ns.startswith(base) for base in self.BASE_NAMESPACES)

            facts.append({
                'concept': concept,
                'namespace': ns,
                'local_name': local,
                'value': value,
                'value_text': value_text,
                'unit': unit_ref,
                'decimals': int(decimals) if decimals and decimals != 'INF' else 0,
                'context_id': ctx_ref,
                'is_extension': is_extension,
            })

        return contexts, facts, cik

    def _get_namespace_prefix(self, ns: str) -> str:
        if 'us-gaap' in ns:
            return 'us-gaap'
        elif 'dei' in ns:
            return 'dei'
        elif 'srt' in ns:
            return 'srt'
        elif 'ecd' in ns:
            return 'ecd'
        else:
            parts = ns.rstrip('/').split('/')
            return parts[-1] if parts else ''

    def _parse_presentation_linkbase(self, path: str) -> Dict[str, str]:
        tree = ET.parse(path)
        root = tree.getroot()

        fact_to_role = {}

        for plink in root.findall('.//{http://www.xbrl.org/2003/linkbase}presentationLink'):
            role = plink.get('{http://www.w3.org/1999/xlink}role')

            for loc in plink.findall('.//{http://www.xbrl.org/2003/linkbase}loc'):
                href = loc.get('{http://www.w3.org/1999/xlink}href')
                if href and '#' in href:
                    concept_part = href.split('#')[-1]
                    if '_' in concept_part:
                        local_name = concept_part.split('_', 1)[-1]
                    else:
                        local_name = concept_part

                    if local_name not in fact_to_role:
                        fact_to_role[local_name] = role

        return fact_to_role

    def _insert_contexts(self, accession_number: str, cik: str, contexts: dict):
        context_data = [
            (accession_number, cik, ctx.context_id, ctx.period_type,
             ctx.period_start, ctx.period_end,
             json.dumps(ctx.segment) if ctx.segment else None)
            for ctx in contexts.values()
        ]

        with self.conn.cursor() as cur:
            execute_values(cur, """
                INSERT INTO sb_xbrl_contexts
                (accession_number, cik, context_id, period_type, period_start, period_end, segment)
                VALUES %s
                ON CONFLICT (accession_number, context_id) DO NOTHING
            """, context_data)

        self.conn.commit()

    def _insert_statements(self, accession_number: str, cik: str, filing_date,
                           statements: List[StatementInfo]) -> Dict[str, int]:
        stmt_id_map = {}

        with self.conn.cursor() as cur:
            for stmt in statements:
                cur.execute("""
                    INSERT INTO sb_xbrl_statements
                    (accession_number, cik, filing_date, role_uri, short_name, long_name,
                     menu_category, position, statement_type)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (accession_number, role_uri) DO UPDATE SET
                        short_name = EXCLUDED.short_name,
                        statement_type = EXCLUDED.statement_type
                    RETURNING id
                """, (accession_number, cik, filing_date, stmt.role_uri, stmt.short_name,
                      stmt.long_name, stmt.menu_category, stmt.position, stmt.statement_type))

                stmt_id = cur.fetchone()[0]
                stmt_id_map[stmt.role_uri] = stmt_id

        self.conn.commit()
        return stmt_id_map

    def _deduplicate_facts(self, facts: list) -> list:
        """
        Deduplicate facts per Arelle OIM specification.

        A fact is uniquely identified by: concept + context + unit

        Deduplication strategy (consistent-pairs):
        - Complete duplicates (same value): keep one
        - Consistent duplicates (same except decimals): keep highest precision
        - Inconsistent duplicates (different values): keep highest precision, log warning

        Higher decimals = more precise (e.g., decimals=2 is more precise than decimals=-6)
        Exception: decimals='INF' means infinite precision (stored as 0, but should be highest)
        """
        # Key: (local_name, context_id, unit) -> best fact
        fact_map = {}
        duplicate_count = 0
        inconsistent_count = 0

        for f in facts:
            key = (f['local_name'], f['context_id'], f['unit'])

            if key not in fact_map:
                fact_map[key] = f
            else:
                duplicate_count += 1
                existing = fact_map[key]

                # Check if values match (consistent vs inconsistent)
                if existing['value'] != f['value'] and existing['value'] is not None and f['value'] is not None:
                    inconsistent_count += 1

                # Keep the one with higher precision (higher decimals value)
                # Treat 0 (from INF) as highest precision
                existing_dec = existing['decimals'] if existing['decimals'] != 0 else 999
                new_dec = f['decimals'] if f['decimals'] != 0 else 999

                if new_dec > existing_dec:
                    fact_map[key] = f

        if duplicate_count > 0:
            print(f"    Deduplication: {duplicate_count} duplicates removed, {inconsistent_count} inconsistent")

        return list(fact_map.values())

    def _insert_facts(self, accession_number: str, cik: str, filing_date,
                      facts: list, contexts: dict, stmt_id_map: dict, fact_to_role: dict) -> int:
        """Insert facts with deduplication. Returns count of deduplicated facts."""
        # First, deduplicate facts
        deduplicated_facts = self._deduplicate_facts(facts)

        fact_data = []

        for f in deduplicated_facts:
            ctx = contexts.get(f['context_id'])
            if ctx is None:
                continue

            statement_id = None
            role = fact_to_role.get(f['local_name'])
            if role and role in stmt_id_map:
                statement_id = stmt_id_map[role]

            fact_data.append((
                accession_number,
                cik,
                filing_date,
                f['concept'],
                f['namespace'],
                f['local_name'],
                f['value'],
                f['value_text'],
                f['unit'],
                f['decimals'],
                f['context_id'],
                ctx.period_type,
                ctx.period_start,
                ctx.period_end,
                json.dumps(ctx.segment) if ctx.segment else None,
                statement_id,
                ctx.segment is None,
                f['is_extension'],
            ))

        with self.conn.cursor() as cur:
            execute_values(cur, """
                INSERT INTO sb_xbrl_facts
                (accession_number, cik, filing_date, concept, namespace, local_name,
                 value, value_text, unit, decimals, context_id, period_type,
                 period_start, period_end, segment, statement_id, is_primary, is_extension)
                VALUES %s
                ON CONFLICT (accession_number, local_name, context_id, unit)
                DO UPDATE SET
                    decimals = CASE
                        WHEN EXCLUDED.decimals > sb_xbrl_facts.decimals THEN EXCLUDED.decimals
                        ELSE sb_xbrl_facts.decimals
                    END,
                    value = CASE
                        WHEN EXCLUDED.decimals > sb_xbrl_facts.decimals THEN EXCLUDED.value
                        ELSE sb_xbrl_facts.value
                    END
            """, fact_data)

        self.conn.commit()
        return len(fact_data)


# =============================================================================
# Main Test
# =============================================================================

def get_document_paths(conn, accession_number: str) -> dict:
    """Get paths to XBRL documents for a filing."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT file_name, path_on_disk
            FROM sb_documents
            WHERE accession_number = %s
              AND (file_name LIKE '%%_htm.xml'
                   OR file_name = 'FilingSummary.xml'
                   OR file_name LIKE '%%_pre.xml')
        """, (accession_number,))

        docs = {}
        for fname, path in cur.fetchall():
            if fname == 'FilingSummary.xml':
                docs['filing_summary'] = path
            elif fname.endswith('_htm.xml'):
                docs['instance'] = path
            elif fname.endswith('_pre.xml'):
                docs['presentation'] = path
        return docs


def show_results(conn):
    """Display results after processing."""
    print("\n" + "="*80)
    print("RESULTS")
    print("="*80)

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Count tables
        print("\n--- Table Counts ---")
        for table in ['sb_xbrl_statements', 'sb_xbrl_contexts', 'sb_xbrl_facts']:
            cur.execute(f"SELECT COUNT(*) as cnt FROM {table}")
            print(f"{table}: {cur.fetchone()['cnt']} rows")

        # Show statements
        print("\n--- Statements (MenuCategory = 'Statements') ---")
        cur.execute("""
            SELECT statement_type, short_name, position
            FROM sb_xbrl_statements
            WHERE menu_category = 'Statements'
            ORDER BY position
        """)
        for row in cur.fetchall():
            print(f"  {row['position']:2d}. [{row['statement_type']:20s}] {row['short_name']}")

        # Show sample facts for Income Statement
        print("\n--- Income Statement Facts (Primary, Latest Period) ---")
        cur.execute("""
            SELECT
                fa.local_name,
                fa.value,
                fa.unit,
                fa.period_start,
                fa.period_end
            FROM sb_xbrl_facts fa
            JOIN sb_xbrl_statements s ON fa.statement_id = s.id
            WHERE s.statement_type = 'IncomeStatement'
              AND fa.is_primary = TRUE
              AND fa.value IS NOT NULL
              AND fa.period_type = 'duration'
            ORDER BY s.position, fa.local_name
            LIMIT 20
        """)
        for row in cur.fetchall():
            val = f"{row['value']:,.0f}" if row['value'] else 'N/A'
            print(f"  {row['local_name']:50s} {val:>20s} {row['unit'] or ''}")

        # Show sample facts for Balance Sheet
        print("\n--- Balance Sheet Facts (Primary, Latest Period) ---")
        cur.execute("""
            SELECT
                fa.local_name,
                fa.value,
                fa.unit,
                fa.period_end
            FROM sb_xbrl_facts fa
            JOIN sb_xbrl_statements s ON fa.statement_id = s.id
            WHERE s.statement_type = 'BalanceSheet'
              AND fa.is_primary = TRUE
              AND fa.value IS NOT NULL
              AND fa.period_type = 'instant'
            ORDER BY fa.period_end DESC, fa.local_name
            LIMIT 20
        """)
        for row in cur.fetchall():
            val = f"{row['value']:,.0f}" if row['value'] else 'N/A'
            print(f"  {row['local_name']:50s} {val:>20s} ({row['period_end']})")

        # Show key metrics
        print("\n--- Key Metrics ---")
        cur.execute("""
            SELECT local_name, value, period_end
            FROM sb_xbrl_facts
            WHERE local_name IN (
                'Assets', 'Liabilities', 'StockholdersEquity',
                'RevenueFromContractWithCustomerExcludingAssessedTax',
                'NetIncomeLoss', 'GrossProfit', 'OperatingIncomeLoss'
            )
              AND is_primary = TRUE
              AND value IS NOT NULL
            ORDER BY local_name, period_end DESC
        """)
        current_concept = None
        for row in cur.fetchall():
            if row['local_name'] != current_concept:
                current_concept = row['local_name']
                print(f"\n  {current_concept}:")
            val = f"${row['value']:,.0f}"
            print(f"    {row['period_end']}: {val:>25s}")


def main():
    print("="*80)
    print("XBRL New Schema Test")
    print(f"Processing filing: {TEST_ACCESSION}")
    print("="*80)

    # Connect to database
    conn = psycopg2.connect(**DB_CONFIG)

    try:
        # Step 1: Create tables
        print("\n[1] Creating tables...")
        with conn.cursor() as cur:
            cur.execute(CREATE_TABLES_SQL)
        conn.commit()
        print("    Tables created successfully")

        # Step 2: Get document paths
        print("\n[2] Getting document paths...")
        docs = get_document_paths(conn, TEST_ACCESSION)
        for doc_type, path in docs.items():
            print(f"    {doc_type}: {path}")

        if 'filing_summary' not in docs or 'instance' not in docs:
            print("ERROR: Missing required documents")
            return

        # Step 3: Process filing
        print("\n[3] Processing filing...")
        processor = XBRLProcessor(conn)
        stats = processor.process_filing(TEST_ACCESSION, docs)
        print(f"    Contexts: {stats['contexts']}")
        print(f"    Statements: {stats['statements']}")
        print(f"    Facts (raw): {stats['facts_raw']}")
        print(f"    Facts (deduplicated): {stats['facts_deduplicated']}")

        # Step 4: Show results
        show_results(conn)

    finally:
        conn.close()


if __name__ == '__main__':
    main()
