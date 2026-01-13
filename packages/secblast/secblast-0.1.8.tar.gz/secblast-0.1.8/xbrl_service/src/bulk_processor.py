#!/usr/bin/env python3
"""
Bulk XBRL Processor

Processes XBRL filings and stores structured data in sb_xbrl_* tables.
Tracks processing status in sb_document_metadata.xbrl_processed.

Usage:
    # Process unprocessed filings (marks as processed)
    python bulk_processor.py --limit 1000

    # Process specific filing without marking (for RSS real-time)
    python bulk_processor.py --accession 0000002488-25-000012 --no-mark

    # Backfill historical data
    python bulk_processor.py --backfill --workers 8
"""

import argparse
import logging
import sys
import time
import xml.etree.ElementTree as ET
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import date
from typing import Optional, Dict, List, Tuple
import json
import re
import os

import psycopg2
from psycopg2.extras import execute_values, RealDictCursor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Database configuration
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': int(os.environ.get('DB_PORT', 5432)),
    'dbname': os.environ.get('DB_NAME', 'secblast'),
    'user': os.environ.get('DB_USER', 'secblast'),
    'password': os.environ.get('DB_PASSWORD', 'secblast123')
}


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


class XBRLProcessor:
    """Processes XBRL filings and stores in relational schema."""

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

        # 3. Parse presentation linkbase for fact-to-statement mapping and order
        fact_to_role_order = {}
        if 'presentation' in documents:
            fact_to_role_order = self._parse_presentation_linkbase(documents['presentation'])

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
        deduplicated_count = self._insert_facts(
            accession_number, cik, filing_date, facts, contexts, stmt_id_map, fact_to_role_order
        )
        stats['facts_deduplicated'] = deduplicated_count

        return stats

    def _get_filing_info(self, accession_number: str) -> dict:
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT cik, filing_date FROM sb_filings
                WHERE accession_number = %s
                LIMIT 1
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

    def _parse_presentation_linkbase(self, path: str) -> Dict[str, Tuple[str, int]]:
        """
        Parse presentation linkbase to get role URI and presentation order for each concept.

        Returns:
            Dict mapping local_name -> (role_uri, presentation_order)
        """
        tree = ET.parse(path)
        root = tree.getroot()

        # Result: local_name -> (role, order)
        fact_to_role_order = {}

        NS = {
            'link': 'http://www.xbrl.org/2003/linkbase',
            'xlink': 'http://www.w3.org/1999/xlink'
        }

        for plink in root.findall('.//link:presentationLink', NS):
            role = plink.get('{http://www.w3.org/1999/xlink}role')

            # Build label -> local_name mapping from loc elements
            label_to_concept = {}
            for loc in plink.findall('link:loc', NS):
                label = loc.get('{http://www.w3.org/1999/xlink}label')
                href = loc.get('{http://www.w3.org/1999/xlink}href')
                if href and '#' in href:
                    concept_part = href.split('#')[-1]
                    if '_' in concept_part:
                        local_name = concept_part.split('_', 1)[-1]
                    else:
                        local_name = concept_part
                    label_to_concept[label] = local_name

            # Build parent -> [(child, order)] from presentationArc elements
            children = {}  # parent_label -> [(child_label, order)]
            roots = set(label_to_concept.keys())

            for arc in plink.findall('link:presentationArc', NS):
                parent = arc.get('{http://www.w3.org/1999/xlink}from')
                child = arc.get('{http://www.w3.org/1999/xlink}to')
                order = float(arc.get('order', '1'))

                if parent not in children:
                    children[parent] = []
                children[parent].append((child, order))

                # Child is not a root
                roots.discard(child)

            # Sort children by order
            for parent in children:
                children[parent].sort(key=lambda x: x[1])

            # Traverse tree in presentation order (depth-first)
            presentation_order = 0
            visited = set()

            def traverse(label):
                nonlocal presentation_order
                if label in visited:
                    return
                visited.add(label)

                local_name = label_to_concept.get(label)
                if local_name and local_name not in fact_to_role_order:
                    fact_to_role_order[local_name] = (role, presentation_order)
                    presentation_order += 1

                for child_label, _ in children.get(label, []):
                    traverse(child_label)

            # Start from root nodes
            for root_label in sorted(roots):
                traverse(root_label)

        return fact_to_role_order

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
        """Deduplicate facts per Arelle OIM specification (consistent-pairs strategy)."""
        fact_map = {}
        duplicate_count = 0

        for f in facts:
            key = (f['local_name'], f['context_id'], f['unit'])

            if key not in fact_map:
                fact_map[key] = f
            else:
                duplicate_count += 1
                existing = fact_map[key]
                existing_dec = existing['decimals'] if existing['decimals'] != 0 else 999
                new_dec = f['decimals'] if f['decimals'] != 0 else 999

                if new_dec > existing_dec:
                    fact_map[key] = f

        return list(fact_map.values())

    def _insert_facts(self, accession_number: str, cik: str, filing_date,
                      facts: list, contexts: dict, stmt_id_map: dict,
                      fact_to_role_order: Dict[str, Tuple[str, int]]) -> int:
        """Insert facts with deduplication. Returns count of deduplicated facts."""
        deduplicated_facts = self._deduplicate_facts(facts)

        fact_data = []

        for f in deduplicated_facts:
            ctx = contexts.get(f['context_id'])
            if ctx is None:
                continue

            statement_id = None
            presentation_order = 999999  # Default for concepts not in presentation

            role_order = fact_to_role_order.get(f['local_name'])
            if role_order:
                role, presentation_order = role_order
                if role in stmt_id_map:
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
                presentation_order,
            ))

        with self.conn.cursor() as cur:
            execute_values(cur, """
                INSERT INTO sb_xbrl_facts
                (accession_number, cik, filing_date, concept, namespace, local_name,
                 value, value_text, unit, decimals, context_id, period_type,
                 period_start, period_end, segment, statement_id, is_primary, is_extension,
                 presentation_order)
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
                    END,
                    presentation_order = EXCLUDED.presentation_order
            """, fact_data)

        self.conn.commit()
        return len(fact_data)


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


def get_unprocessed_filings(conn, limit: int = 1000, form_types: List[str] = None) -> List[str]:
    """Get accession numbers of filings with XBRL that haven't been processed."""
    form_filter = ""
    if form_types:
        placeholders = ','.join(['%s'] * len(form_types))
        form_filter = f"AND f.form_type IN ({placeholders})"

    query = f"""
        SELECT accession_number FROM (
            SELECT DISTINCT ON (d.accession_number) d.accession_number, d.filing_date
            FROM sb_documents d
            JOIN sb_filings f ON d.accession_number = f.accession_number
            WHERE d.file_name LIKE '%%_htm.xml'
              AND NOT EXISTS (
                  SELECT 1 FROM sb_document_metadata m
                  WHERE m.id = d.accession_number || '-1'
                    AND m.xbrl_processed = TRUE
              )
              {form_filter}
        ) sub
        ORDER BY filing_date DESC
        LIMIT %s
    """

    params = form_types + [limit] if form_types else [limit]

    with conn.cursor() as cur:
        cur.execute(query, params)
        return [row[0] for row in cur.fetchall()]


def mark_as_processed(conn, accession_number: str, success: bool = True):
    """Mark a filing as XBRL processed in sb_document_metadata."""
    doc_id = f"{accession_number}-1"

    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO sb_document_metadata (id, xbrl_processed)
            VALUES (%s, %s)
            ON CONFLICT (id) DO UPDATE SET xbrl_processed = EXCLUDED.xbrl_processed
        """, (doc_id, success))

    conn.commit()


def process_single_filing(accession_number: str, mark_processed: bool = True) -> Tuple[str, bool, str, dict]:
    """Process a single filing. Returns (accession_number, success, error_msg, stats)."""
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)

        # Get document paths
        docs = get_document_paths(conn, accession_number)

        if 'filing_summary' not in docs or 'instance' not in docs:
            return (accession_number, False, "Missing required documents", {})

        # Check if files exist
        for doc_type, path in docs.items():
            if not os.path.exists(path):
                return (accession_number, False, f"File not found: {path}", {})

        # Process the filing
        processor = XBRLProcessor(conn)
        stats = processor.process_filing(accession_number, docs)

        # Mark as processed if requested
        if mark_processed:
            mark_as_processed(conn, accession_number, True)

        return (accession_number, True, None, stats)

    except Exception as e:
        error_msg = str(e)
        # Mark as failed if we should track processing
        if mark_processed and conn:
            try:
                mark_as_processed(conn, accession_number, False)
            except:
                pass
        return (accession_number, False, error_msg, {})

    finally:
        if conn:
            conn.close()


def process_batch(accession_numbers: List[str], workers: int = 4, mark_processed: bool = True) -> dict:
    """Process a batch of filings in parallel."""
    results = {
        'success': 0,
        'failed': 0,
        'total_facts': 0,
        'errors': []
    }

    logger.info(f"Processing {len(accession_numbers)} filings with {workers} workers...")

    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(process_single_filing, acc, mark_processed): acc
            for acc in accession_numbers
        }

        for future in as_completed(futures):
            acc, success, error, stats = future.result()

            if success:
                results['success'] += 1
                results['total_facts'] += stats.get('facts_deduplicated', 0)

                if results['success'] % 100 == 0:
                    logger.info(f"Processed {results['success']} filings...")
            else:
                results['failed'] += 1
                results['errors'].append({'accession': acc, 'error': error})
                logger.warning(f"Failed {acc}: {error}")

    return results


def main():
    parser = argparse.ArgumentParser(description='Bulk XBRL Processor')
    parser.add_argument('--limit', type=int, default=1000, help='Maximum filings to process')
    parser.add_argument('--workers', type=int, default=4, help='Number of parallel workers')
    parser.add_argument('--accession', type=str, help='Process specific accession number')
    parser.add_argument('--no-mark', action='store_true', help='Do not mark as processed')
    parser.add_argument('--backfill', action='store_true', help='Backfill mode (process all unprocessed)')
    parser.add_argument('--form-types', type=str, help='Comma-separated form types (e.g., 10-K,10-Q)')

    args = parser.parse_args()

    mark_processed = not args.no_mark

    # Single filing mode
    if args.accession:
        logger.info(f"Processing single filing: {args.accession}")
        acc, success, error, stats = process_single_filing(args.accession, mark_processed)

        if success:
            logger.info(f"Success! Stats: {stats}")
        else:
            logger.error(f"Failed: {error}")
            sys.exit(1)
        return

    # Batch mode
    conn = psycopg2.connect(**DB_CONFIG)

    try:
        form_types = args.form_types.split(',') if args.form_types else None
        limit = 1000000 if args.backfill else args.limit

        logger.info(f"Getting unprocessed filings (limit={limit})...")
        accession_numbers = get_unprocessed_filings(conn, limit, form_types)
        logger.info(f"Found {len(accession_numbers)} unprocessed filings")

        if not accession_numbers:
            logger.info("No filings to process")
            return

        start_time = time.time()
        results = process_batch(accession_numbers, args.workers, mark_processed)
        elapsed = time.time() - start_time

        logger.info("=" * 60)
        logger.info("PROCESSING COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Success: {results['success']}")
        logger.info(f"Failed: {results['failed']}")
        logger.info(f"Total facts: {results['total_facts']:,}")
        logger.info(f"Time: {elapsed:.1f}s ({len(accession_numbers) / elapsed:.1f} filings/sec)")

        if results['errors']:
            logger.info(f"\nFirst 10 errors:")
            for err in results['errors'][:10]:
                logger.info(f"  {err['accession']}: {err['error']}")

    finally:
        conn.close()


if __name__ == '__main__':
    main()
