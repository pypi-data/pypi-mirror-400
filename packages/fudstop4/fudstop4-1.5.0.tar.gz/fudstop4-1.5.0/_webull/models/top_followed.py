import pandas as pd



class FollowedTicker:
    def __init__(self, ticker):
        self.tickerId = [i.get('tickerId') for i in ticker]
        self.name = [i.get('name') for i in ticker]
        self.symbol = [i.get('symbol') for i in ticker]


        self.data_dict = { 
            'ticker_id': self.tickerId,
            'name': self.name,
            'ticker': self.symbol
        }

        self.as_dataframe = pd.DataFrame(self.data_dict)



class FollowedValues:
    def __init__(self, values):
        self.tickerId = [i.get('tickerId') for i in values]
        self.tradeTime = [i.get('tradeTime') for i in values]
        self.close = [i.get('close') for i in values]
        self.change = [i.get('change') for i in values]
        self.changeRatio = [round(float(i.get('changeRatio'))*100,2) for i in values]
        self.lastPrice = [float(i.get('lastPrice')) for i in values]
        self.lastChange = [float(i.get('lastChange')) for i in values]
        self.lastChangeRatio = [round(float(i.get('lastChangeRatio'))*100,2) for i in values]
        self.marketValue = [float(i.get('marketValue')) for i in values]
        self.volume = [float(i.get('volume')) for i in values]
        self.turnoverRate = [float(i.get('turnoverRate')) for i in values]
        self.high = [float(i.get('high')) for i in values]
        self.low = [float(i.get('low')) for i in values]
        self.vibrateRatio = [float(i.get('vibrateRatio')) for i in values]
        self.peTtm = [float(i.get('peTtm')) for i in values]
        self.followers = [float(i.get('followers')) for i in values]


        self.data_dict = { 
            'ticker_id':self.tickerId,
            'trade_time': self.tradeTime,
            'close': self.close,
            'change': self.change,
            'change_pct': self.changeRatio,
            'last_price': self.lastPrice,
            'last_change': self.lastChange,
            'last_change_pct': self.lastChangeRatio,
            'market_value': self.marketValue,
            'volume': self.volume,
            'turnover_rate': self.turnoverRate,
            'high': self.high,
            'low': self.low,
            'vibration': self.vibrateRatio,
            'pe_ttm': self.peTtm,
            'followers': self.followers
        }


        self.as_dataframe = pd.DataFrame(self.data_dict)