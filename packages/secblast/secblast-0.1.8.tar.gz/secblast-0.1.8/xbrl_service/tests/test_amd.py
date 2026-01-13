#!/usr/bin/env python3
"""
Test script for parsing AMD 10-K filing XBRL data.
CIK: 2488
Accession: 0000002488-25-000012
Filing Date: 2025-02-05
"""

import sys
import json
from pathlib import Path
from datetime import date

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.xbrl_parser import XBRLParser


def test_amd_parsing():
    """Test parsing AMD's 10-K filing."""
    cik = 2488
    accession_number = "0000002488-25-000012"
    filing_date = date(2025, 2, 5)

    print(f"Testing AMD XBRL parsing")
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

    # Print metadata
    print("\n" + "=" * 60)
    print("METADATA")
    print("=" * 60)
    metadata = result.get("metadata", {})
    for key, value in metadata.items():
        print(f"  {key}: {value}")

    # Print Balance Sheet
    print("\n" + "=" * 60)
    print("BALANCE SHEET")
    print("=" * 60)
    balance_sheet = result.get("balance_sheet", {})
    print_statement(balance_sheet)

    # Print Income Statement
    print("\n" + "=" * 60)
    print("INCOME STATEMENT")
    print("=" * 60)
    income_statement = result.get("income_statement", {})
    print_statement(income_statement)

    # Print Cash Flow
    print("\n" + "=" * 60)
    print("CASH FLOW STATEMENT")
    print("=" * 60)
    cash_flow = result.get("cash_flow", {})
    print_statement(cash_flow)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    bs_items = count_items(balance_sheet)
    is_items = count_items(income_statement)
    cf_items = count_items(cash_flow)
    print(f"  Balance Sheet items: {bs_items}")
    print(f"  Income Statement items: {is_items}")
    print(f"  Cash Flow items: {cf_items}")
    print(f"  Total items extracted: {bs_items + is_items + cf_items}")

    return True


def print_statement(data: dict, indent: int = 0):
    """Pretty print a financial statement."""
    prefix = "  " * indent
    for key, value in data.items():
        if isinstance(value, dict):
            if "label" in value and "value" in value:
                # Leaf node
                formatted_value = format_number(value["value"])
                print(f"{prefix}{value['label']}: {formatted_value}")
            else:
                # Nested section
                print(f"{prefix}{key.upper()}:")
                print_statement(value, indent + 1)
        else:
            print(f"{prefix}{key}: {value}")


def format_number(value) -> str:
    """Format a number for display. SEC values are typically in thousands."""
    if value is None:
        return "N/A"
    if isinstance(value, (int, float)):
        # SEC values are in thousands, so multiply by 1000 for true value
        # But for display, just show as-is with appropriate suffix
        abs_val = abs(value)
        if abs_val >= 1_000_000:
            return f"${value/1_000:.1f}B"  # value is in thousands, so /1000 = billions
        elif abs_val >= 1_000:
            return f"${value:.1f}M"  # value is in thousands = millions
        elif abs_val >= 1:
            return f"${value*1000:,.0f}"  # small values, show in dollars
        else:
            return f"${value:.4f}"
    return str(value)


def count_items(data: dict) -> int:
    """Count the number of leaf items in a nested dict."""
    count = 0
    for value in data.values():
        if isinstance(value, dict):
            if "label" in value and "value" in value:
                count += 1
            else:
                count += count_items(value)
    return count


if __name__ == "__main__":
    success = test_amd_parsing()
    sys.exit(0 if success else 1)
