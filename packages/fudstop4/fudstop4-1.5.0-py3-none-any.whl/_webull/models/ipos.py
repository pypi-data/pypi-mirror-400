import pandas as pd


class IPOsUpcoming:
    def __init__(self, items):
        self.tickerId = [i.get('tickerId') for i in items]
        self.listDate = [i.get('listDate') for i in items]
        self.issueUpLimit = [float(i.get('issueUpLimit')) if i.get('issueUpLimit') is not None else None for i in items]
        self.issuePriceStr = [i.get('issuePriceStr') for i in items]
        self.offerAmount = [float(i['offerAmount']) if i.get('offerAmount') is not None else None for i in items]
        self.issueDownLimit = [float(i.get('issueDownLimit')) if i.get('issueDownLimit') is not None else None for i in items]
        self.issueShares = [float(i.get('issueShares')) if i.get('issueShares') is not None else None for i in items]
        self.prospectusPublishDate = [i.get('prospectusPublishDate') for i in items]
        self.purchaseEndDate = [i.get('purchaseEndDate') for i in items]
        self.prospectus = [i.get('prospectus') for i in items]
        self.ipoStatus = [i.get('ipoStatus') for i in items]
        self.closeDays = [float(i.get('closeDays')) if i.get('closeDays') is not None else None for i in items]
        self.offeringType = [i.get('offeringType') for i in items]
        self.name = [i.get('name') for i in items]
        tickerTuple = [i.get('tickerTuple') for i in items]
        self.tickerId = [i.get('tickerId') for i in tickerTuple]
        self.name = [i.get('name') for i in tickerTuple]
        self.symbol = [i.get('symbol') for i in tickerTuple]
        self.change = [float(i.get('change')) for i in tickerTuple]
        self.changeRatio = [round(float(i.get('changeRatio'))*100,2) for i in tickerTuple]
        self.volume = [float(i.get('volume')) for i in tickerTuple]



        self.data_dict = { 
            'ticker': self.symbol,
            'name': self.name,
            'issue_down_limit': self.issueDownLimit,
            'issued_shares': self.issueShares,
            'prospectus_date': self.prospectusPublishDate,            
            'purchase_end_date': self.purchaseEndDate,
            'prospectus_url': self.prospectus,
            'ipo_status': self.ipoStatus,
            'close_days': self.closeDays,
            'offering_type': self.offeringType,
            'change': self.change,
            'change_pct': self.changeRatio,
            'volume': self.volume

        }

        self.as_dataframe = pd.DataFrame(self.data_dict)



# class IPOsFiling:
#     def __init__(self, items):

#         self.tickerId = [i.get('tickerId') for i in items]
#         self.listDate = [i.get('listDate') for i in items]
#         self.issueUpLimit = [i.get('issueUpLimit') for i in items]
#         self.issuePrice = [i.get('issuePrice') for i in items]
#         self.issuePriceStr = [i.get('issuePriceStr') for i in items]
#         self.offerAmount = [i.get('offerAmount') for i in items]
#         self.issueDownLimit = [i.get('issueDownLimit') for i in items]
#         self.issueShares = [i.get('issueShares') for i in items]
#         self.issueCurrencyId = [i.get('issueCurrencyId') for i in items]
#         self.prospectusPublishDate = [i.get('prospectusPublishDate') for i in items]
#         self.purchaseStartDate = [i.get('purchaseStartDate') for i in items]
#         self.purchaseEndDate = [i.get('purchaseEndDate') for i in items]
#         self.prospectus = [i.get('prospectus') for i in items]
#         self.ipoStatus = [i.get('ipoStatus') for i in items]
#         self.closeDays = [i.get('closeDays') for i in items]
#         self.offeringType = [i.get('offeringType') for i in items]
#         self.currencyId = [i.get('currencyId') for i in items]
#         self.webullUnderwriting = [i.get('webullUnderwriting') for i in items]
#         self.name = [i.get('name') for i in items]
#         self.tickerTuple = [i.get('tickerTuple') for i in items]

#         self.data_dict = { 
#             'ticker': self.symbol,
#             'name': self.name,
#             'issue_down_limit': self.issueDownLimit,
#             'issued_shares': self.issueShares,
#             'prospectus_date': self.prospectusPublishDate,            
#             'purchase_end_date': self.purchaseEndDate,
#             'prospectus_url': self.prospectus,
#             'ipo_status': self.ipoStatus,
#             'close_days': self.closeDays,
#             'offering_type': self.offeringType,
#             'change': self.change,
#             'change_pct': self.changeRatio,
#             'volume': self.volume

#         }