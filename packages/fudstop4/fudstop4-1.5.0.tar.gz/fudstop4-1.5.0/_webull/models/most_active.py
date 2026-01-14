import pandas as pd


def _sanitize_float(value: object) -> float:
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(",", "").replace("%", "")
    if not text:
        return 0.0
    if not any(ch.isdigit() for ch in text) and text not in (".", "-."):
        return 0.0
    try:
        return float(text)
    except (TypeError, ValueError):
        return 0.0


class Ticker:
    def __init__(self, ticker):

        self.tickerId = [i.get('tickerId') for i in ticker]
        self.name = [i.get('name') for i in ticker]
        self.symbol = [i.get('symbol') for i in ticker]
        self.tradeTime = [i.get('tradeTime') for i in ticker]
        self.status = [i.get('status') for i in ticker]
        self.close = [_sanitize_float(i.get('close')) for i in ticker]
        self.change = [_sanitize_float(i.get('change')) for i in ticker]
        self.changeRatio = [round(_sanitize_float(i.get('changeRatio')) * 100, 2) for i in ticker]
        self.marketValue = [_sanitize_float(i.get('marketValue')) for i in ticker]
        self.volume = [_sanitize_float(i.get('volume')) for i in ticker]
        self.turnoverRate = [_sanitize_float(i.get('turnoverRate')) for i in ticker]
        self.dividend = [_sanitize_float(i.get('dividend')) for i in ticker]
        self.fiftyTwoWkHigh = [_sanitize_float(i.get('fiftyTwoWkHigh')) for i in ticker]
        self.fiftyTwoWkLow = [_sanitize_float(i.get('fiftyTwoWkLow')) for i in ticker]
        self.open = [_sanitize_float(i.get('open')) for i in ticker]
        self.high = [_sanitize_float(i.get('high')) for i in ticker]
        self.low = [_sanitize_float(i.get('low')) for i in ticker]
        self.vibrateRatio = [_sanitize_float(i.get('vibrateRatio')) for i in ticker]


        self.data_dict = {
            'ticker_id': self.tickerId,
            'name': self.name,
            'symbol': self.symbol,
            'trade_time': self.tradeTime,
            'status': self.status,
            'close': self.close,
            'change': self.change,
            'change_ratio': self.changeRatio,
            'market_value': self.marketValue,
            'volume': self.volume,
            'turnover_rate': self.turnoverRate,
            'dividend': self.dividend,
            'fifty_high': self.fiftyTwoWkHigh,
            'fifty_low': self.fiftyTwoWkLow,
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'vibration': self.vibrateRatio
        }

        self.as_dataframe = pd.DataFrame(self.data_dict)

class Values:
    def __init__(self, values):
        self.tickerId = [i.get('tickerId') for i in values]
        self.rankValue = [_sanitize_float(i.get('rankValue')) for i in values]
        self.isRatio = [i.get('isRatio') for i in values]
        self.quantRating = [_sanitize_float(i.get('quantRating')) for i in values]
        self.debtAssetsRatio = [_sanitize_float(i.get('debtAssetsRatio')) for i in values]
        
        self.data_dict = {
            'ticker_id': self.tickerId,
            'rank_value': self.rankValue,
            'is_ratio': self.isRatio,
            'quant_rating': self.quantRating,
            'debt_assets_ratio': self.debtAssetsRatio
        }

        self.as_dataframe = pd.DataFrame(self.data_dict)
