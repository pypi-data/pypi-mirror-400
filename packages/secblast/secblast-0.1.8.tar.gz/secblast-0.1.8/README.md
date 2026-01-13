# SecBlast Python SDK

Python SDK for the [SecBlast SEC Filing API](https://secblastapi.com).

## Installation

```bash
pip install secblast
```

## Quick Start

```python
from secblast import SecBlastClient

# Initialize the client
client = SecBlastClient(api_key="your-api-key")

# Look up a company
entity = client.get_entity(ticker="AAPL")
print(f"{entity.name} (CIK: {entity.cik})")

# Search filings
filings = client.lookup_filings(
    tickers=["AAPL"],
    form_types=["10-K"],
    date_from="2023-01-01",
)
print(f"Found {filings.count} filings")

# Full-text search
results = client.fulltext_search(
    "material contract",
    form_types=["8-K"],
)
for hit in results.hits:
    print(f"{hit.accession_number}: {hit.text_content[:100]}...")

# Get financial data
balance_sheet = client.get_balance_sheet(cik="320193")
```

## Async Support

```python
import asyncio
from secblast import AsyncSecBlastClient

async def main():
    async with AsyncSecBlastClient(api_key="your-api-key") as client:
        entity = await client.get_entity(ticker="AAPL")
        print(entity.name)

asyncio.run(main())
```

## API Reference

### Entity Lookup

```python
# Search entities with filters
entities = client.lookup_entities(
    tickers=["AAPL", "MSFT"],
    exchanges=["NASDAQ"],
    sics=["3571"],  # Electronic Computers
    name_includes=["tech"],
)

# Get single entity
entity = client.get_entity(ticker="AAPL")
entity = client.get_entity(cik="320193")
```

### Filing Lookup

```python
# Search filings
filings = client.lookup_filings(
    tickers=["AAPL"],
    form_types=["10-K", "10-Q"],
    date_from="2023-01-01",
    date_to="2023-12-31",
    exclude_amendments=True,
    sort_by="filing_date",
    sort_order="desc",
)

# Get detailed filing info
detail = client.get_filing_info("0000320193-23-000077")
print(detail.filing.form_type)
print(len(detail.documents))

# Get 10-K/10-Q sections
sections = client.get_filing_sections(document_id, form_type="10-K")
for section in sections:
    print(f"{section.id}: {section.name}")

# Batch fetch 8-K items
items = client.get_8k_items([
    "0001829126-25-010357",
    "0001213900-25-126699",
])
```

### Full-Text Search

```python
# Standard search
results = client.fulltext_search("revenue growth")

# Exact phrase
results = client.fulltext_search(
    "material contract",
    query_type="match_phrase",
)

# Lucene query syntax
results = client.fulltext_search(
    "revenue AND NOT loss",
    query_type="query_string",
)

# With filters
results = client.fulltext_search(
    "merger agreement",
    ciks=["320193"],
    form_types=["8-K"],
    date_from="2023-01-01",
    sort_by="_score",  # Sort by relevance
)
```

### Documents

```python
# Get raw document content
content = client.get_document(document_id)  # Returns bytes

# Get as JSON
doc = client.get_document(document_id, output_format="json")
print(doc.file_name, doc.content_type)

# Generate PDF
pdf_bytes = client.get_pdf(document_id=document_id)
# Or entire filing
pdf_bytes = client.get_pdf(accession_number="0000320193-23-000077")
```

### Financial Data

```python
# Get financial statements
balance_sheet = client.get_balance_sheet(cik="320193")
income_stmt = client.get_income_statement(cik="320193")
cash_flow = client.get_cash_flow(cik="320193")

# Get raw XBRL data
raw = client.get_raw_financials(cik="320193")

# List available filings
filings = client.list_financial_filings(cik="320193")

# Get historical data for a concept
history = client.get_financial_history(cik="320193", concept="us-gaap:Revenue")

# Export to Excel
xlsx_bytes = client.export_financials_excel(cik="320193")
with open("financials.xlsx", "wb") as f:
    f.write(xlsx_bytes)
```

## Error Handling

```python
from secblast import (
    SecBlastClient,
    AuthenticationError,
    RateLimitError,
    ValidationError,
)

client = SecBlastClient(api_key="your-api-key")

try:
    entity = client.get_entity(ticker="AAPL")
except AuthenticationError:
    print("Invalid API key")
except RateLimitError as e:
    print(f"Rate limit exceeded: {e.limit_type}")
except ValidationError as e:
    print(f"Invalid request: {e.message}")
```

## License

MIT
