import pandas as pd



class HighDividendTicker:
    def __init__(self, ticker):
        self.tickerId = [i.get('tickerId') for i in ticker]
        self.name = [i.get('name') for i in ticker]
        self.symbol = [i.get('symbol') for i in ticker]
        self.tradeTime = [i.get('tradeTime') for i in ticker]
        self.close = [float(i.get('close')) for i in ticker]
        self.change = [float(i.get('change')) for i in ticker]
        self.changeRatio = [round(float(i.get('changeRatio'))*100,2) for i in ticker]
        self.marketValue = [float(i.get('marketValue')) for i in ticker]
        self.volume = [float(i.get('volume')) for i in ticker]
        self.turnoverRate = [float(i.get('turnoverRate')) for i in ticker]
        self.peTtm = [float(i.get('peTtm')) for i in ticker]
        self.dividend = [float(i.get('dividend')) for i in ticker]
        self.fiftyTwoWkHigh = [float(i.get('fiftyTwoWkHigh')) for i in ticker]
        self.fiftyTwoWkLow = [float(i.get('fiftyTwoWkLow')) for i in ticker]
        self.open = [float(i.get('open')) for i in ticker]
        self.high = [float(i.get('high')) for i in ticker]
        self.low = [float(i.get('low')) for i in ticker]
        self.vibrateRatio = [float(i.get('vibrateRatio')) for i in ticker]


        self.data_dict = {
            'ticker_id': self.tickerId,
            'name': self.name,
            'ticker': self.symbol,
            'trade_time': self.tradeTime,
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'change': self.change,
            'change_pct': self.changeRatio,
            'market_value': self.marketValue,
            'volume': self.volume,
            'turnover_rate': self.turnoverRate,
            'pe_ttm': self.peTtm,
            'dividend': self.dividend,
            'fifty_high': self.fiftyTwoWkHigh,
            'fifty_low': self.fiftyTwoWkLow,
            'vibration': self.vibrateRatio


        }


        self.as_dataframe = pd.DataFrame(self.data_dict)


class DividendsValues:
    def __init__(self, values):
        self.tickerId = [i.get('tickerId') for i in values]
        self._yield = [float(i.get('yield')) for i in values]
        self.dividend = [float(i.get('dividend')) if i.get('dividend') is not None else None for i in values]
        self.exDate = [i.get('exDate') for i in values]


        self.data_dict = { 
            'ticker_id': self.tickerId,
            'yield': self._yield,
            'dividend': self.dividend,
            'ex_date': self.exDate
        }


        self.as_dataframe = pd.DataFrame(self.data_dict)