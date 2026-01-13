"""
US-GAAP XBRL tag mappings for financial statements.
Maps XBRL tags to structured financial statement line items.
"""

# Balance Sheet mappings
BALANCE_SHEET_MAPPINGS = {
    # Assets - Current
    "CashAndCashEquivalentsAtCarryingValue": "assets.current.cash_and_equivalents",
    "ShortTermInvestments": "assets.current.short_term_investments",
    "MarketableSecuritiesCurrent": "assets.current.marketable_securities",
    "AccountsReceivableNetCurrent": "assets.current.accounts_receivable",
    "InventoryNet": "assets.current.inventory",
    "PrepaidExpenseAndOtherAssetsCurrent": "assets.current.prepaid_expenses",
    "OtherAssetsCurrent": "assets.current.other",
    "AssetsCurrent": "assets.current.total",
    # Assets - Non-Current
    "PropertyPlantAndEquipmentNet": "assets.non_current.property_plant_equipment",
    "Goodwill": "assets.non_current.goodwill",
    "IntangibleAssetsNetExcludingGoodwill": "assets.non_current.intangible_assets",
    "LongTermInvestments": "assets.non_current.long_term_investments",
    "MarketableSecuritiesNoncurrent": "assets.non_current.marketable_securities",
    "DeferredTaxAssetsNetNoncurrent": "assets.non_current.deferred_tax_assets",
    "OtherAssetsNoncurrent": "assets.non_current.other",
    "AssetsNoncurrent": "assets.non_current.total",
    # Total Assets
    "Assets": "assets.total",
    # Liabilities - Current
    "AccountsPayableCurrent": "liabilities.current.accounts_payable",
    "AccruedLiabilitiesCurrent": "liabilities.current.accrued_liabilities",
    "DeferredRevenueCurrent": "liabilities.current.deferred_revenue",
    "CommercialPaper": "liabilities.current.commercial_paper",
    "ShortTermBorrowings": "liabilities.current.short_term_debt",
    "LongTermDebtCurrent": "liabilities.current.current_portion_long_term_debt",
    "OtherLiabilitiesCurrent": "liabilities.current.other",
    "LiabilitiesCurrent": "liabilities.current.total",
    # Liabilities - Non-Current
    "LongTermDebtNoncurrent": "liabilities.non_current.long_term_debt",
    "DeferredRevenueNoncurrent": "liabilities.non_current.deferred_revenue",
    "DeferredTaxLiabilitiesNoncurrent": "liabilities.non_current.deferred_tax_liabilities",
    "OtherLiabilitiesNoncurrent": "liabilities.non_current.other",
    "LiabilitiesNoncurrent": "liabilities.non_current.total",
    # Total Liabilities
    "Liabilities": "liabilities.total",
    # Stockholders' Equity
    "CommonStockValue": "equity.common_stock",
    "RetainedEarningsAccumulatedDeficit": "equity.retained_earnings",
    "AccumulatedOtherComprehensiveIncomeLossNetOfTax": "equity.accumulated_other_comprehensive_income",
    "TreasuryStockValue": "equity.treasury_stock",
    "AdditionalPaidInCapital": "equity.additional_paid_in_capital",
    "StockholdersEquity": "equity.total",
    "MinorityInterest": "equity.minority_interest",
    "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest": "equity.total_including_noncontrolling",
    # Total Liabilities and Equity
    "LiabilitiesAndStockholdersEquity": "liabilities_and_equity.total",
}

# Income Statement mappings
INCOME_STATEMENT_MAPPINGS = {
    # Revenue
    "RevenueFromContractWithCustomerExcludingAssessedTax": "revenue.net_sales",
    "Revenues": "revenue.total",
    "SalesRevenueNet": "revenue.net_sales",
    "SalesRevenueGoodsNet": "revenue.goods",
    "SalesRevenueServicesNet": "revenue.services",
    # Cost of Revenue
    "CostOfGoodsAndServicesSold": "cost_of_revenue.total",
    "CostOfRevenue": "cost_of_revenue.total",
    "CostOfGoodsSold": "cost_of_revenue.goods",
    "CostOfServices": "cost_of_revenue.services",
    # Gross Profit
    "GrossProfit": "gross_profit",
    # Operating Expenses
    "ResearchAndDevelopmentExpense": "operating_expenses.research_and_development",
    "SellingGeneralAndAdministrativeExpense": "operating_expenses.selling_general_administrative",
    "SellingAndMarketingExpense": "operating_expenses.selling_and_marketing",
    "GeneralAndAdministrativeExpense": "operating_expenses.general_and_administrative",
    "OperatingExpenses": "operating_expenses.total",
    # Operating Income
    "OperatingIncomeLoss": "operating_income",
    # Other Income/Expense
    "InterestExpense": "other.interest_expense",
    "InterestIncome": "other.interest_income",
    "InterestAndDividendIncome": "other.interest_and_dividend_income",
    "OtherNonoperatingIncomeExpense": "other.other_income_expense",
    "NonoperatingIncomeExpense": "other.total",
    # Income Before Tax
    "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest": "income_before_tax",
    # Tax
    "IncomeTaxExpenseBenefit": "income_tax_expense",
    # Net Income
    "NetIncomeLoss": "net_income",
    "NetIncomeLossAttributableToParent": "net_income_attributable_to_parent",
    "NetIncomeLossAttributableToNoncontrollingInterest": "net_income_attributable_to_noncontrolling",
    # Per Share Data
    "EarningsPerShareBasic": "per_share.basic_eps",
    "EarningsPerShareDiluted": "per_share.diluted_eps",
    "CommonStockDividendsPerShareDeclared": "per_share.dividends_declared",
    # Shares Outstanding
    "WeightedAverageNumberOfSharesOutstandingBasic": "shares.basic_weighted_average",
    "WeightedAverageNumberOfDilutedSharesOutstanding": "shares.diluted_weighted_average",
}

# Cash Flow Statement mappings
CASH_FLOW_MAPPINGS = {
    # Operating Activities
    "NetIncomeLoss": "operating.net_income",
    "DepreciationDepletionAndAmortization": "operating.depreciation_amortization",
    "ShareBasedCompensation": "operating.stock_based_compensation",
    "DeferredIncomeTaxExpenseBenefit": "operating.deferred_income_taxes",
    "IncreaseDecreaseInAccountsReceivable": "operating.accounts_receivable_change",
    "IncreaseDecreaseInInventories": "operating.inventory_change",
    "IncreaseDecreaseInAccountsPayable": "operating.accounts_payable_change",
    "IncreaseDecreaseInOtherOperatingLiabilities": "operating.other_liabilities_change",
    "OtherOperatingActivitiesCashFlowStatement": "operating.other",
    "NetCashProvidedByUsedInOperatingActivities": "operating.net_cash",
    # Investing Activities
    "PaymentsToAcquirePropertyPlantAndEquipment": "investing.capital_expenditures",
    "PaymentsToAcquireBusinessesNetOfCashAcquired": "investing.acquisitions",
    "PaymentsToAcquireInvestments": "investing.purchases_of_investments",
    "ProceedsFromSaleOfInvestments": "investing.sales_of_investments",
    "ProceedsFromMaturitiesPrepaymentsAndCallsOfAvailableForSaleSecurities": "investing.maturities_of_investments",
    "PaymentsToAcquireIntangibleAssets": "investing.intangible_asset_purchases",
    "OtherInvestingActivitiesCashFlowStatement": "investing.other",
    "NetCashProvidedByUsedInInvestingActivities": "investing.net_cash",
    # Financing Activities
    "ProceedsFromIssuanceOfCommonStock": "financing.stock_issuance_proceeds",
    "PaymentsForRepurchaseOfCommonStock": "financing.stock_repurchases",
    "PaymentsOfDividendsCommonStock": "financing.dividends_paid",
    "ProceedsFromIssuanceOfLongTermDebt": "financing.debt_proceeds",
    "RepaymentsOfLongTermDebt": "financing.debt_repayments",
    "ProceedsFromRepaymentsOfShortTermDebt": "financing.short_term_debt_net",
    "OtherFinancingActivitiesCashFlowStatement": "financing.other",
    "NetCashProvidedByUsedInFinancingActivities": "financing.net_cash",
    # Summary
    "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect": "net_change_in_cash",
    "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents": "ending_cash_balance",
    "CashAndCashEquivalentsAtCarryingValue": "ending_cash",
}

# Labels for display
STATEMENT_LABELS = {
    "assets.current.cash_and_equivalents": "Cash and Cash Equivalents",
    "assets.current.short_term_investments": "Short-Term Investments",
    "assets.current.marketable_securities": "Marketable Securities",
    "assets.current.accounts_receivable": "Accounts Receivable, Net",
    "assets.current.inventory": "Inventory",
    "assets.current.prepaid_expenses": "Prepaid Expenses",
    "assets.current.other": "Other Current Assets",
    "assets.current.total": "Total Current Assets",
    "assets.non_current.property_plant_equipment": "Property, Plant & Equipment, Net",
    "assets.non_current.goodwill": "Goodwill",
    "assets.non_current.intangible_assets": "Intangible Assets",
    "assets.non_current.long_term_investments": "Long-Term Investments",
    "assets.non_current.other": "Other Non-Current Assets",
    "assets.non_current.total": "Total Non-Current Assets",
    "assets.total": "Total Assets",
    "liabilities.current.accounts_payable": "Accounts Payable",
    "liabilities.current.accrued_liabilities": "Accrued Liabilities",
    "liabilities.current.deferred_revenue": "Deferred Revenue",
    "liabilities.current.short_term_debt": "Short-Term Debt",
    "liabilities.current.other": "Other Current Liabilities",
    "liabilities.current.total": "Total Current Liabilities",
    "liabilities.non_current.long_term_debt": "Long-Term Debt",
    "liabilities.non_current.other": "Other Non-Current Liabilities",
    "liabilities.non_current.total": "Total Non-Current Liabilities",
    "liabilities.total": "Total Liabilities",
    "equity.common_stock": "Common Stock",
    "equity.retained_earnings": "Retained Earnings",
    "equity.treasury_stock": "Treasury Stock",
    "equity.total": "Total Stockholders' Equity",
    "liabilities_and_equity.total": "Total Liabilities and Stockholders' Equity",
    "revenue.net_sales": "Net Sales",
    "revenue.total": "Total Revenue",
    "cost_of_revenue.total": "Cost of Revenue",
    "gross_profit": "Gross Profit",
    "operating_expenses.research_and_development": "Research and Development",
    "operating_expenses.selling_general_administrative": "Selling, General & Administrative",
    "operating_expenses.total": "Total Operating Expenses",
    "operating_income": "Operating Income",
    "income_before_tax": "Income Before Income Taxes",
    "income_tax_expense": "Income Tax Expense",
    "net_income": "Net Income",
    "per_share.basic_eps": "Basic Earnings Per Share",
    "per_share.diluted_eps": "Diluted Earnings Per Share",
    "operating.net_cash": "Net Cash from Operating Activities",
    "investing.net_cash": "Net Cash from Investing Activities",
    "financing.net_cash": "Net Cash from Financing Activities",
    "net_change_in_cash": "Net Change in Cash",
    "ending_cash_balance": "Ending Cash Balance",
}
