import pandas as pd


class Ticker:
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


class Values:
    def __init__(self, values):
        self.tickerId = [i.get('tickerId') for i in values]
        self.tradeTime = [i.get('tradeTime') for i in values]
        def safe_float(val):
            try:
                return float(val)
            except (TypeError, ValueError):
                return None

        self.close = [safe_float(i.get('close')) for i in values]
        self.change = [safe_float(i.get('change')) for i in values]

        self.changeRatio = []
        for i in values:
            val = safe_float(i.get('changeRatio'))
            if val is not None:
                self.changeRatio.append(round(val * 100, 2))
            else:
                self.changeRatio.append(None)
        self.lastPrice = [safe_float(i.get('lastPrice')) for i in values]
        self.price = [safe_float(i.get('price')) for i in values]
        self.lastChange = [safe_float(i.get('lastChange')) for i in values]
        self.lastChangeRatio = [safe_float(i.get('lastChangeRatio')) for i in values]
        self.marketValue = [safe_float(i.get('marketValue')) for i in values]
        self.volume = [safe_float(i.get('volume')) for i in values]
        self.turnoverRate = [safe_float(i.get('turnoverRate')) for i in values]
        self.high = [safe_float(i.get('high')) for i in values]
        self.low = [safe_float(i.get('low')) for i in values]
        self.vibrateRatio = [safe_float(i.get('vibrateRatio')) for i in values]
        self.peTtm = [safe_float(i.get('peTtm')) for i in values]
        self.quantRating = [safe_float(i.get('quantRating')) for i in values]
        self.debtAssetsRatio = [safe_float(i.get('debtAssetsRatio')) for i in values]


        self.data_dict = {
            'ticker_id': self.tickerId,
            'trade_time': self.tradeTime,
            'close': self.close,
            'change': self.change,
            'change_pct': self.changeRatio,
            'last_price': self.lastPrice,
            'price': self.price,
            'last_change': self.lastChange,
            'last_change_pct': self.lastChangeRatio,
            'market_value': self.marketValue,
            'volume': self.volume,
            'turnover_rate': self.turnoverRate,
            'high': self.high,
            'low': self.low,
            'vibration': self.vibrateRatio,
            'peTtm': self.peTtm,
            'quant_rating': self.quantRating,
            'debt_assets_ratio': self.debtAssetsRatio
        }


        self.as_dataframe = pd.DataFrame(self.data_dict)


class TickerData:
    def __init__(self, ticker_obj: Ticker, values_obj: Values):
        # Merge dataframes on tickerId
        self.as_dataframe = pd.merge(
            ticker_obj.as_dataframe,
            values_obj.as_dataframe,
            on='ticker_id',
            how='inner'
        )

        # Optional: expose columns as dot notation (i.e., self.symbol, self.price, etc.)
        for column in self.as_dataframe.columns:
            setattr(self, column, self.as_dataframe[column])
