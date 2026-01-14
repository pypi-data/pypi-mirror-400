import pandas as pd




class IncomeStatement:
    def __init__(self, data):
        self.quoteId = [float(i.get('quoteId')) if i.get('quoteId') is not None else None for i in data]
        self.type = [float(i.get('type')) if i.get('type') is not None else None for i in data]
        self.fiscalYear = [float(i.get('fiscalYear')) if i.get('fiscalYear') is not None else None for i in data]
        self.fiscalPeriod = [float(i.get('fiscalPeriod')) if i.get('fiscalPeriod') is not None else None for i in data]
        self.endDate = [i.get('endDate') for i in data]
        self.publishDate = [i.get('publishDate') for i in data]
        self.totalRevenue = [float(i.get('totalRevenue')) if i.get('totalRevenue') is not None else None for i in data]
        self.revenue = [float(i.get('revenue')) if i.get('revenue') is not None else None for i in data]
        self.costofRevenueTotal = [float(i.get('costofRevenueTotal')) if i.get('costofRevenueTotal') is not None else None for i in data]
        self.grossProfit = [float(i.get('grossProfit')) if i.get('grossProfit') is not None else None for i in data]
        self.operatingExpense = [float(i.get('operatingExpense')) if i.get('operatingExpense') is not None else None for i in data]
        self.sellGenAdminExpenses = [float(i.get('sellGenAdminExpenses')) if i.get('sellGenAdminExpenses') is not None else None for i in data]
        self.researchDevelopment = [float(i.get('researchDevelopment')) if i.get('researchDevelopment') is not None else None for i in data]
        self.operatingIncome = [float(i.get('operatingIncome')) if i.get('operatingIncome') is not None else None for i in data]
        self.otherNetIncome = [float(i.get('otherNetIncome')) if i.get('otherNetIncome') is not None else None for i in data]
        self.netIncomeBeforeTax = [float(i.get('netIncomeBeforeTax')) if i.get('netIncomeBeforeTax') is not None else None for i in data]
        self.incomeTax = [float(i.get('incomeTax')) if i.get('incomeTax') is not None else None for i in data]
        self.netIncomeAfterTax = [float(i.get('netIncomeAfterTax')) if i.get('netIncomeAfterTax') is not None else None for i in data]
        self.netIncomeBeforeExtra = [float(i.get('netIncomeBeforeExtra')) if i.get('netIncomeBeforeExtra') is not None else None for i in data]
        self.totalExtraordinaryItems = [float(i.get('totalExtraordinaryItems')) if i.get('totalExtraordinaryItems') is not None else None for i in data]
        self.netIncome = [float(i.get('netIncome')) if i.get('netIncome') is not None else None for i in data]
        self.incomeAvaitoComExclExtraOrd = [float(i.get('incomeAvaitoComExclExtraOrd')) if i.get('incomeAvaitoComExclExtraOrd') is not None else None for i in data]
        self.incomeAvaitoComInclExtraOrd = [float(i.get('incomeAvaitoComInclExtraOrd')) if i.get('incomeAvaitoComInclExtraOrd') is not None else None for i in data]
        self.dilutedNetIncome = [float(i.get('dilutedNetIncome')) if i.get('dilutedNetIncome') is not None else None for i in data]
        self.dilutedWeightedAverageShares = [float(i.get('dilutedWeightedAverageShares')) if i.get('dilutedWeightedAverageShares') is not None else None for i in data]
        self.dilutedEPSExclExtraItems = [float(i.get('dilutedEPSExclExtraItems')) if i.get('dilutedEPSExclExtraItems') is not None else None for i in data]
        self.dilutedEPSInclExtraItems = [float(i.get('dilutedEPSInclExtraItems')) if i.get('dilutedEPSInclExtraItems') is not None else None for i in data]
        self.dividendsperShare = [float(i.get('dividendsperShare')) if i.get('dividendsperShare') is not None else None for i in data]
        self.dilutedNormalizedEPS = [float(i.get('dilutedNormalizedEPS')) if i.get('dilutedNormalizedEPS') is not None else None for i in data]
        self.operatingProfit = [float(i.get('operatingProfit')) if i.get('operatingProfit') is not None else None for i in data]
        self.earningAfterTax = [float(i.get('earningAfterTax')) if i.get('earningAfterTax') is not None else None for i in data]
        self.earningBeforeTax = [float(i.get('earningBeforeTax')) if i.get('earningBeforeTax') is not None else None for i in data]
        self.data_dict = {
            "quote_id": self.quoteId,
            "type": self.type,
            "fiscal_year": self.fiscalYear,
            "fiscal_period": self.fiscalPeriod,
            "end_date": self.endDate,
            "publish_date": self.publishDate,
            "total_revenue": self.totalRevenue,
            "revenue": self.revenue,
            "cost_of_revenue_total": self.costofRevenueTotal,
            "gross_profit": self.grossProfit,
            "operating_expense": self.operatingExpense,
            "sell_gen_admin_expenses": self.sellGenAdminExpenses,
            "research_development": self.researchDevelopment,
            "operating_income": self.operatingIncome,
            "other_net_income": self.otherNetIncome,
            "net_income_before_tax": self.netIncomeBeforeTax,
            "income_tax": self.incomeTax,
            "net_income_after_tax": self.netIncomeAfterTax,
            "net_income_before_extra": self.netIncomeBeforeExtra,
            "total_extraordinary_items": self.totalExtraordinaryItems,
            "net_income": self.netIncome,
            "income_ava_to_com_excl_extra_ord": self.incomeAvaitoComExclExtraOrd,
            "income_ava_to_com_incl_extra_ord": self.incomeAvaitoComInclExtraOrd,
            "diluted_net_income": self.dilutedNetIncome,
            "diluted_weighted_average_shares": self.dilutedWeightedAverageShares,
            "diluted_eps_excl_extra_items": self.dilutedEPSExclExtraItems,
            "diluted_eps_incl_extra_items": self.dilutedEPSInclExtraItems,
            "dividends_per_share": self.dividendsperShare,
            "diluted_normalized_eps": self.dilutedNormalizedEPS,
            "operating_profit": self.operatingProfit,
            "earning_after_tax": self.earningAfterTax,
            "earning_before_tax": self.earningBeforeTax,
        }

        self.as_dataframe = pd.DataFrame(self.data_dict)
class BalanceSheet:
    def __init__(self, data):
        self.quoteId = [float(i.get('quoteId')) if i.get('quoteId') is not None else None for i in data]
        self.type = [float(i.get('type')) if i.get('type') is not None else None for i in data]
        self.fiscalYear = [float(i.get('fiscalYear')) if i.get('fiscalYear') is not None else None for i in data]
        self.fiscalPeriod = [float(i.get('fiscalPeriod')) if i.get('fiscalPeriod') is not None else None for i in data]
        self.endDate = [i.get('endDate') for i in data]
        self.publishDate = [i.get('publishDate') for i in data]
        self.totalAssets = [float(i.get('totalAssets')) if i.get('totalAssets') is not None else None for i in data]
        self.totalCurrentAssets = [float(i.get('totalCurrentAssets')) if i.get('totalCurrentAssets') is not None else None for i in data]
        self.cashAndShortTermInvest = [float(i.get('cashAndShortTermInvest')) if i.get('cashAndShortTermInvest') is not None else None for i in data]
        self.cash = [float(i.get('cash')) if i.get('cash') is not None else None for i in data]
        self.cashEquivalents = [float(i.get('cashEquivalents')) if i.get('cashEquivalents') is not None else None for i in data]
        self.shortTermInvestments = [float(i.get('shortTermInvestments')) if i.get('shortTermInvestments') is not None else None for i in data]
        self.totalReceivablesNet = [float(i.get('totalReceivablesNet')) if i.get('totalReceivablesNet') is not None else None for i in data]
        self.accountsReceTradeNet = [float(i.get('accountsReceTradeNet')) if i.get('accountsReceTradeNet') is not None else None for i in data]
        self.totalInventory = [float(i.get('totalInventory')) if i.get('totalInventory') is not None else None for i in data]
        self.otherCurrentAssetsTotal = [float(i.get('otherCurrentAssetsTotal')) if i.get('otherCurrentAssetsTotal') is not None else None for i in data]
        self.totalNonCurrentAssets = [float(i.get('totalNonCurrentAssets')) if i.get('totalNonCurrentAssets') is not None else None for i in data]
        self.ppeTotalNet = [float(i.get('ppeTotalNet')) if i.get('ppeTotalNet') is not None else None for i in data]
        self.ppeTotalGross = [float(i.get('ppeTotalGross')) if i.get('ppeTotalGross') is not None else None for i in data]
        self.accumulatedDepreciationTotal = [float(i.get('accumulatedDepreciationTotal')) if i.get('accumulatedDepreciationTotal') is not None else None for i in data]
        self.longTermInvestments = [float(i.get('longTermInvestments')) if i.get('longTermInvestments') is not None else None for i in data]
        self.otherLongTermAssetsTotal = [float(i.get('otherLongTermAssetsTotal')) if i.get('otherLongTermAssetsTotal') is not None else None for i in data]
        self.totalLiabilities = [float(i.get('totalLiabilities')) if i.get('totalLiabilities') is not None else None for i in data]
        self.totalCurrentLiabilities = [float(i.get('totalCurrentLiabilities')) if i.get('totalCurrentLiabilities') is not None else None for i in data]
        self.accountsPayable = [float(i.get('accountsPayable')) if i.get('accountsPayable') is not None else None for i in data]
        self.accruedExpenses = [float(i.get('accruedExpenses')) if i.get('accruedExpenses') is not None else None for i in data]
        self.notesPayableShortTermDebt = [float(i.get('notesPayableShortTermDebt')) if i.get('notesPayableShortTermDebt') is not None else None for i in data]
        self.currentPortofLTDebtCapitalLeases = [float(i.get('currentPortofLTDebtCapitalLeases')) if i.get('currentPortofLTDebtCapitalLeases') is not None else None for i in data]
        self.otherCurrentLiabilitiesTotal = [float(i.get('otherCurrentLiabilitiesTotal')) if i.get('otherCurrentLiabilitiesTotal') is not None else None for i in data]
        self.totalNonCurrentLiabilities = [float(i.get('totalNonCurrentLiabilities')) if i.get('totalNonCurrentLiabilities') is not None else None for i in data]
        self.totalLongTermDebt = [float(i.get('totalLongTermDebt')) if i.get('totalLongTermDebt') is not None else None for i in data]
        self.longTermDebt = [float(i.get('longTermDebt')) if i.get('longTermDebt') is not None else None for i in data]
        self.capitalLeaseObligations = [float(i.get('capitalLeaseObligations')) if i.get('capitalLeaseObligations') is not None else None for i in data]
        self.totalDebt = [float(i.get('totalDebt')) if i.get('totalDebt') is not None else None for i in data]
        self.otherLiabilitiesTotal = [float(i.get('otherLiabilitiesTotal')) if i.get('otherLiabilitiesTotal') is not None else None for i in data]
        self.totalEquity = [float(i.get('totalEquity')) if i.get('totalEquity') is not None else None for i in data]
        self.totalStockhodersEquity = [float(i.get('totalStockhodersEquity')) if i.get('totalStockhodersEquity') is not None else None for i in data]
        self.commonStock = [float(i.get('commonStock')) if i.get('commonStock') is not None else None for i in data]
        self.additionalPaidInCapital = [float(i.get('additionalPaidInCapital')) if i.get('additionalPaidInCapital') is not None else None for i in data]
        self.retainedEarnings = [float(i.get('retainedEarnings')) if i.get('retainedEarnings') is not None else None for i in data]
        self.otherEquityTotal = [float(i.get('otherEquityTotal')) if i.get('otherEquityTotal') is not None else None for i in data]
        self.totalLiabilitiesShareholdersEquity = [float(i.get('totalLiabilitiesShareholdersEquity')) if i.get('totalLiabilitiesShareholdersEquity') is not None else None for i in data]
        self.totalCommonSharesOutstanding = [float(i.get('totalCommonSharesOutstanding')) if i.get('totalCommonSharesOutstanding') is not None else None for i in data]

        self.data_dict = {
            "quote_id": self.quoteId,
            "type": self.type,
            "fiscal_year": self.fiscalYear,
            "fiscal_period": self.fiscalPeriod,
            "end_date": self.endDate,
            "publish_date": self.publishDate,
            "total_assets": self.totalAssets,
            "total_current_assets": self.totalCurrentAssets,
            "cash_and_short_term_invest": self.cashAndShortTermInvest,
            "cash": self.cash,
            "cash_equivalents": self.cashEquivalents,
            "short_term_investments": self.shortTermInvestments,
            "total_receivables_net": self.totalReceivablesNet,
            "accounts_rece_trade_net": self.accountsReceTradeNet,
            "total_inventory": self.totalInventory,
            "other_current_assets_total": self.otherCurrentAssetsTotal,
            "total_non_current_assets": self.totalNonCurrentAssets,
            "ppe_total_net": self.ppeTotalNet,
            "ppe_total_gross": self.ppeTotalGross,
            "accumulated_depreciation_total": self.accumulatedDepreciationTotal,
            "long_term_investments": self.longTermInvestments,
            "other_long_term_assets_total": self.otherLongTermAssetsTotal,
            "total_liabilities": self.totalLiabilities,
            "total_current_liabilities": self.totalCurrentLiabilities,
            "accounts_payable": self.accountsPayable,
            "accrued_expenses": self.accruedExpenses,
            "notes_payable_short_term_debt": self.notesPayableShortTermDebt,
            "current_port_of_lt_debt_capital_leases": self.currentPortofLTDebtCapitalLeases,
            "other_current_liabilities_total": self.otherCurrentLiabilitiesTotal,
            "total_non_current_liabilities": self.totalNonCurrentLiabilities,
            "total_long_term_debt": self.totalLongTermDebt,
            "long_term_debt": self.longTermDebt,
            "capital_lease_obligations": self.capitalLeaseObligations,
            "total_debt": self.totalDebt,
            "other_liabilities_total": self.otherLiabilitiesTotal,
            "total_equity": self.totalEquity,
            "total_stockhoders_equity": self.totalStockhodersEquity,
            "common_stock": self.commonStock,
            "additional_paid_in_capital": self.additionalPaidInCapital,
            "retained_earnings": self.retainedEarnings,
            "other_equity_total": self.otherEquityTotal,
            "total_liabilities_shareholders_equity": self.totalLiabilitiesShareholdersEquity,
            "total_common_shares_outstanding": self.totalCommonSharesOutstanding
        }
        self.as_dataframe = pd.DataFrame(self.data_dict)


class CashFlow:
    def __init__(self, data):
        self.quoteId = [float(i.get('quoteId')) if i.get('quoteId') is not None else None for i in data]
        self.type = [float(i.get('type')) if i.get('type') is not None else None for i in data]
        self.fiscalYear = [float(i.get('fiscalYear')) if i.get('fiscalYear') is not None else None for i in data]
        self.fiscalPeriod = [float(i.get('fiscalPeriod')) if i.get('fiscalPeriod') is not None else None for i in data]
        self.endDate = [i.get('endDate') for i in data]
        self.publishDate = [i.get('publishDate') for i in data]
        self.cashfromOperatingActivities = [float(i.get('cashfromOperatingActivities')) if i.get('cashfromOperatingActivities') is not None else None for i in data]
        self.netIncome = [float(i.get('netIncome')) if i.get('netIncome') is not None else None for i in data]
        self.depreciationAndAmortization = [float(i.get('depreciationAndAmortization')) if i.get('depreciationAndAmortization') is not None else None for i in data]
        self.nonCashItems = [float(i.get('nonCashItems')) if i.get('nonCashItems') is not None else None for i in data]
        self.changesinWorkingCapital = [float(i.get('changesinWorkingCapital')) if i.get('changesinWorkingCapital') is not None else None for i in data]
        self.cashfromInvestingActivities = [float(i.get('cashfromInvestingActivities')) if i.get('cashfromInvestingActivities') is not None else None for i in data]
        self.capitalExpenditures = [float(i.get('capitalExpenditures')) if i.get('capitalExpenditures') is not None else None for i in data]
        self.otherInvestingCashFlowItemsTotal = [float(i.get('otherInvestingCashFlowItemsTotal')) if i.get('otherInvestingCashFlowItemsTotal') is not None else None for i in data]
        self.cashfromFinancingActivities = [float(i.get('cashfromFinancingActivities')) if i.get('cashfromFinancingActivities') is not None else None for i in data]
        self.financingCashFlowItems = [float(i.get('financingCashFlowItems')) if i.get('financingCashFlowItems') is not None else None for i in data]
        self.totalCashDividendsPaid = [float(i.get('totalCashDividendsPaid')) if i.get('totalCashDividendsPaid') is not None else None for i in data]
        self.issuanceRetirementofStockNet = [float(i.get('issuanceRetirementofStockNet')) if i.get('issuanceRetirementofStockNet') is not None else None for i in data]
        self.issuanceRetirementofDebtNet = [float(i.get('issuanceRetirementofDebtNet')) if i.get('issuanceRetirementofDebtNet') is not None else None for i in data]
        self.netChangeinCash = [float(i.get('netChangeinCash')) if i.get('netChangeinCash') is not None else None for i in data]
        self.cashTaxesPaid = [float(i.get('cashTaxesPaid')) if i.get('cashTaxesPaid') is not None else None for i in data]


        self.data_dict = {
            "quote_id": self.quoteId,
            "type": self.type,
            "fiscal_year": self.fiscalYear,
            "fiscal_period": self.fiscalPeriod,
            "end_date": self.endDate,
            "publish_date": self.publishDate,
            "cash_from_operating_activities": self.cashfromOperatingActivities,
            "net_income": self.netIncome,
            "depreciation_and_amortization": self.depreciationAndAmortization,
            "non_cash_items": self.nonCashItems,
            "changes_in_working_capital": self.changesinWorkingCapital,
            "cash_from_investing_activities": self.cashfromInvestingActivities,
            "capital_expenditures": self.capitalExpenditures,
            "other_investing_cash_flow_items_total": self.otherInvestingCashFlowItemsTotal,
            "cash_from_financing_activities": self.cashfromFinancingActivities,
            "financing_cash_flow_items": self.financingCashFlowItems,
            "total_cash_dividends_paid": self.totalCashDividendsPaid,
            "issuance_retirement_of_stock_net": self.issuanceRetirementofStockNet,
            "issuance_retirement_of_debt_net": self.issuanceRetirementofDebtNet,
            "net_change_in_cash": self.netChangeinCash,
            "cash_taxes_paid": self.cashTaxesPaid
        }

        self.as_dataframe = pd.DataFrame(self.data_dict)