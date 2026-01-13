#!/usr/bin/env python3
"""
Read-only test script for AMD XBRL parsing.
Only parses files and prints output - does NOT touch the database.
"""

import sys
from pathlib import Path
from datetime import date

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.xbrl_parser import XBRLParser


def test_amd_parsing():
    """Test parsing AMD's 10-K filing - READ ONLY."""
    cik = 2488
    accession_number = "0000002488-25-000012"
    filing_date = date(2025, 2, 5)

    print("READ-ONLY AMD XBRL Parsing Test")
    print(f"  CIK: {cik}")
    print(f"  Accession: {accession_number}")
    print(f"  Filing Date: {filing_date}")
    print("-" * 60)

    parser = XBRLParser()

    # Test path resolution
    xbrl_path = parser._get_xbrl_path(cik, accession_number, filing_date)
    print(f"\nXBRL Path: {xbrl_path}")

    if not xbrl_path:
        print("ERROR: Could not find XBRL files!")
        return False

    # Find the main XBRL file
    xbrl_file = parser._find_xbrl_file(xbrl_path)
    print(f"XBRL File: {xbrl_file}")

    if not xbrl_file:
        print("ERROR: Could not find main XBRL file!")
        return False

    # Parse the filing
    print("\nParsing XBRL...")
    try:
        result = parser.parse_filing(cik, accession_number, filing_date)
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Print key values only
    print("\n" + "=" * 60)
    print("KEY FINANCIAL VALUES")
    print("=" * 60)

    metadata = result.get("metadata", {})
    print(f"\nMetadata:")
    print(f"  Fiscal Year: {metadata.get('fiscal_year')}")
    print(f"  Period End: {metadata.get('document_period_end')}")

    bs = result.get("balance_sheet", {})
    is_ = result.get("income_statement", {})
    cf = result.get("cash_flow", {})

    def get_value(data, *keys):
        """Get a nested value from dict."""
        for key in keys:
            if isinstance(data, dict) and key in data:
                data = data[key]
            else:
                return None
        if isinstance(data, dict) and "value" in data:
            return data["value"]
        return None

    def fmt(v):
        if v is None:
            return "N/A"
        if abs(v) >= 1e9:
            return f"${v/1e9:.2f}B"
        elif abs(v) >= 1e6:
            return f"${v/1e6:.2f}M"
        else:
            return f"${v:,.2f}"

    print("\nBalance Sheet:")
    print(f"  Total Assets: {fmt(get_value(bs, 'assets', 'total'))}")
    print(f"  Cash: {fmt(get_value(bs, 'assets', 'current', 'cash_and_equivalents'))}")
    print(f"  Total Equity: {fmt(get_value(bs, 'equity', 'total'))}")

    print("\nIncome Statement:")
    print(f"  Revenue: {fmt(get_value(is_, 'revenue', 'total'))}")
    print(f"  Net Income: {fmt(get_value(is_, 'net_income'))}")
    print(f"  Basic EPS: {get_value(is_, 'per_share', 'basic_eps')}")

    print("\nCash Flow:")
    print(f"  Operating Cash Flow: {fmt(get_value(cf, 'operating', 'net_cash'))}")
    print(f"  Investing Cash Flow: {fmt(get_value(cf, 'investing', 'net_cash'))}")

    # Count items
    def count_items(data):
        count = 0
        for v in data.values():
            if isinstance(v, dict):
                if "label" in v and "value" in v:
                    count += 1
                else:
                    count += count_items(v)
        return count

    print(f"\nTotal items extracted: {count_items(bs) + count_items(is_) + count_items(cf)}")
    print("\nDONE - No database writes performed.")

    return True


if __name__ == "__main__":
    success = test_amd_parsing()
    sys.exit(0 if success else 1)
