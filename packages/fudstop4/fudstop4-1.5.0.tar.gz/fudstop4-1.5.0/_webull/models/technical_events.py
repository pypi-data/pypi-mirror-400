import pandas as pd
from datetime import datetime
import pytz

class TechnicalTicker:
    def __init__(self, ticker, type, time_horizon):
        self.tickerId = [i.get('tickerId') for i in ticker]
        self.name = [i.get('name') for i in ticker]
        self.symbol = [i.get('symbol') for i in ticker]


        self.data_dict = { 
            'ticker_id': self.tickerId,
            'name': self.name,
            'ticker': self.symbol
        }

        self.as_dataframe = pd.DataFrame(self.data_dict)


        self.as_dataframe['type'] = type
        self.as_dataframe['time_horizon'] = time_horizon



class TechnicalValues:
    def __init__(self, values):
        eastern = pytz.timezone('US/Eastern')

        self.tickerId = [i.get('tickerId') for i in values]
        self.tradeTime = [
            datetime.strptime(t, "%Y-%m-%dT%H:%M:%S.%f%z")
            .astimezone(eastern)
            .strftime('%Y-%m-%d %H:%M:%S')
            if t else None
            for t in [i.get('tradeTime') for i in values]
        ]
        self.close = [float(i.get('close')) for i in values]
        self.open = [float(i.get('open')) for i in values]
        self.change = [float(i.get('change')) for i in values]
        self.changeRatio = [round(float(i.get('changeRatio'))*100,2) for i in values]
        self.marketValue = [float(i.get('marketValue')) for i in values]
        self.volume = [float(i.get('volume')) for i in values]
        self.turnoverRate = [float(i.get('turnoverRate')) for i in values]
        self.high = [float(i.get('high')) for i in values]
        self.low = [float(i.get('low')) for i in values]
        self.vibrateRatio = [float(i.get('vibrateRatio')) for i in values]
        self.peTtm = [float(i.get('peTtm')) for i in values]
        self.score = [float(i.get('score')) for i in values]
        self.lastestSignal = [i.get('lastestSignal') for i in values]
        self.changeRatioMs = [
            round(float(i.get('changeRatioMs')) * 100, 2) if i.get('changeRatioMs') is not None else None
            for i in values
        ]


        self.data_dict = { 
            'ticker_id': self.tickerId,
            'trade_time': self.tradeTime,
            'close': self.close,
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'volume': self.volume,
            'change': self.change,
            'change_pct': self.changeRatio,
            'change_pct_ms': self.changeRatioMs,
            'market_value': self.marketValue,
            'pe_ttm': self.peTtm,
            'turnover_rate': self.turnoverRate,
            'vibration': self.vibrateRatio,
            'signal': self.lastestSignal,
            'score': self.score
                            }

        self.as_dataframe = pd.DataFrame(self.data_dict)