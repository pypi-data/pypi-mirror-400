import pandas as pd



class ETFHoldings:
    def __init__(self, data):
        self.fundQuoteId = [i.get('fundQuoteId') for i in data]
        self.name = [i.get('name') for i in data]
        self.changeRatio = [round(float(i.get('changeRatio'))*100,2) for i in data]
        self.shareNumber = [float(i.get('shareNumber')) if i.get('shareNumber') is not None else None for i in data]
        self.ratio = [round(float(i.get('ratio'))*100,2) if i.get('ratio') is not None else None for i in data]
        tickerTuple = [i.get('tickerTuple') for i in data]
        self.tickerId = [i.get('tickerId') for i in tickerTuple]
        self.ticker_name = [i.get('name') for i in tickerTuple]
        self.symbol = [i.get('symbol') for i in tickerTuple]


        self.data_dict = { 
            'fund_id': self.fundQuoteId,
            'fund_name': self.name,
            'change_pct': self.changeRatio,
            'share_number': self.shareNumber,
            'ratio': self.ratio,
            'ticker_id': self.tickerId,
            'ticker_name': self.ticker_name,
            'ticker': self.symbol
        }


        self.as_dataframe = pd.DataFrame(self.data_dict)