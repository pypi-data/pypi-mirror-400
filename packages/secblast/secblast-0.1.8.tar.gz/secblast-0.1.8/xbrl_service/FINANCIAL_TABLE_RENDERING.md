# Financial Statement Table Rendering Guide

## API Endpoint

```
GET /v2/financials/balance-sheet?cik={cik}&format=table
GET /v2/financials/income-statement?cik={cik}&format=table
GET /v2/financials/cash-flow?cik={cik}&format=table
```

## Response Format

```json
{
  "cik": "2488",
  "accession_number": "0000002488-25-000166",
  "filing_date": "2025-11-05",
  "form_type": "10-Q",
  "statement_type": "balance_sheet",
  "short_name": "Condensed Consolidated Balance Sheets",
  "columns": ["2025-09-27", "2024-12-28"],
  "rows": [
    {
      "concept": "CashAndCashEquivalentsAtCarryingValue",
      "label": "Cash And Cash Equivalents At Carrying Value",
      "values": [4808000000, 3787000000],
      "unit": "usd"
    }
  ]
}
```

## Presentation Order

Rows are returned in **presentation order** from the SEC filing's XBRL presentation linkbase. This matches exactly how the statement appears in the company's 10-K/10-Q filing.

For a balance sheet, the typical order is:

```
ASSETS
├── Cash and Cash Equivalents
├── Short-term Investments
├── Accounts Receivable
├── Inventory
├── Other Current Assets
├── **Total Current Assets**        ← Bold (collection/total)
├── Property, Plant & Equipment
├── Goodwill
├── Intangible Assets
├── Other Non-current Assets
├── **Total Assets**                ← Bold (collection/total)

LIABILITIES
├── Accounts Payable
├── Accrued Liabilities
├── Current Debt
├── Other Current Liabilities
├── **Total Current Liabilities**   ← Bold (collection/total)
├── Long-term Debt
├── Other Non-current Liabilities
├── **Total Liabilities**           ← Bold (collection/total)

EQUITY
├── Common Stock
├── Additional Paid-in Capital
├── Treasury Stock
├── Retained Earnings
├── Accumulated Other Comprehensive Income
├── **Total Stockholders' Equity**  ← Bold (collection/total)
├── **Total Liabilities & Equity**  ← Bold (collection/total)
```

## Identifying Collection/Total Entries (for Bolding)

Collection entries are totals that aggregate other line items. They should be rendered in **bold**.

### Method 1: Pattern Matching on Concept Name (Recommended)

Bold rows where `concept` matches these patterns:

```javascript
const TOTAL_PATTERNS = [
  // Balance Sheet totals
  /^Assets$/,
  /^AssetsCurrent$/,
  /^AssetsNoncurrent$/,
  /^Liabilities$/,
  /^LiabilitiesCurrent$/,
  /^LiabilitiesNoncurrent$/,
  /^LiabilitiesAndStockholdersEquity$/,
  /^StockholdersEquity$/,
  /^StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest$/,

  // Income Statement totals
  /^GrossProfit$/,
  /^OperatingIncomeLoss$/,
  /^IncomeLossFromContinuingOperationsBeforeIncomeTaxes/,
  /^NetIncomeLoss$/,
  /^ComprehensiveIncomeNetOfTax$/,

  // Cash Flow totals
  /^NetCashProvidedByUsedIn.*Activities$/,
  /^CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect$/,
];

function isTotalRow(concept) {
  return TOTAL_PATTERNS.some(pattern => pattern.test(concept));
}
```

### Method 2: Simple Keyword Matching

Bold rows where `label` contains total-indicating words:

```javascript
function isTotalRow(label) {
  const lowerLabel = label.toLowerCase();
  return (
    lowerLabel.startsWith('total ') ||
    lowerLabel.includes(' total') ||
    lowerLabel === 'assets' ||
    lowerLabel === 'liabilities' ||
    lowerLabel.includes('stockholders equity') ||
    lowerLabel.includes('net income') ||
    lowerLabel.includes('gross profit') ||
    lowerLabel.includes('operating income')
  );
}
```

### Method 3: Known Total Concepts (Comprehensive List)

```javascript
const TOTAL_CONCEPTS = new Set([
  // Balance Sheet
  'Assets',
  'AssetsCurrent',
  'AssetsNoncurrent',
  'Liabilities',
  'LiabilitiesCurrent',
  'LiabilitiesNoncurrent',
  'LiabilitiesAndStockholdersEquity',
  'StockholdersEquity',
  'StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest',
  'LiabilitiesAndPartnersCapital',

  // Income Statement
  'Revenues',
  'RevenueFromContractWithCustomerExcludingAssessedTax',
  'CostOfRevenue',
  'CostOfGoodsAndServicesSold',
  'GrossProfit',
  'OperatingExpenses',
  'OperatingIncomeLoss',
  'IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest',
  'IncomeTaxExpenseBenefit',
  'NetIncomeLoss',
  'NetIncomeLossAttributableToParent',
  'ComprehensiveIncomeNetOfTax',

  // Cash Flow
  'NetCashProvidedByUsedInOperatingActivities',
  'NetCashProvidedByUsedInInvestingActivities',
  'NetCashProvidedByUsedInFinancingActivities',
  'CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect',
  'CashAndCashEquivalentsPeriodIncreaseDecrease',
]);

function isTotalRow(concept) {
  return TOTAL_CONCEPTS.has(concept);
}
```

## React Example

```tsx
interface FinancialRow {
  concept: string;
  label: string;
  values: (number | null)[];
  unit: string;
}

interface TableData {
  columns: string[];
  rows: FinancialRow[];
  short_name: string;
}

function FinancialTable({ data }: { data: TableData }) {
  const formatValue = (val: number | null) => {
    if (val === null) return '—';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      notation: 'compact',
      maximumFractionDigits: 1,
    }).format(val);
  };

  const isTotalRow = (concept: string) => {
    return [
      'Assets', 'AssetsCurrent', 'Liabilities', 'LiabilitiesCurrent',
      'LiabilitiesAndStockholdersEquity', 'StockholdersEquity',
      'GrossProfit', 'OperatingIncomeLoss', 'NetIncomeLoss',
      'NetCashProvidedByUsedInOperatingActivities',
      'NetCashProvidedByUsedInInvestingActivities',
      'NetCashProvidedByUsedInFinancingActivities',
    ].includes(concept);
  };

  return (
    <table>
      <thead>
        <tr>
          <th>{data.short_name}</th>
          {data.columns.map(col => (
            <th key={col}>{col}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {data.rows.map(row => (
          <tr
            key={row.concept}
            style={{ fontWeight: isTotalRow(row.concept) ? 'bold' : 'normal' }}
          >
            <td>{row.label}</td>
            {row.values.map((val, i) => (
              <td key={i} style={{ textAlign: 'right' }}>
                {formatValue(val)}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
```

## Formatting Notes

1. **Values are in raw units** (not thousands/millions). Format as needed.
2. **Null values** indicate the concept wasn't reported for that period.
3. **Columns are sorted** most recent first (descending by date).
4. **Negative values** (like Treasury Stock, Accumulated Deficit) should show with parentheses or minus sign.
5. **Unit is typically "usd"** but check for "shares" or "pure" (ratios).

## Handling Missing Data

Some periods may have `null` values because:
- The concept wasn't reported in that filing
- Each filing only contains its own period data

Display as "—" or leave blank for null values.
