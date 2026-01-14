import pandas as pd
from UTILS.helpers import safe_float
from UTILS.confluence import score_price_target


class yfPriceTarget:
    def __init__(self, data):

        self.current = safe_float(data.get('current'))
        self.low     = safe_float(data.get('low'))
        self.high    = safe_float(data.get('high'))
        self.mean    = safe_float(data.get('mean'))
        self.median  = safe_float(data.get('median'))
        self.data_dict = {
            'current': self.current,
            'high': self.high,
            'low': self.low,
            'average': self.mean,
            'median': self.median
        }

        scorer = score_price_target(
            current=self.current,
            mean=self.mean,
            median=self.median,
            high=self.high,
            low=self.low
        )
        self.data_dict.update(scorer.to_columns('price_target'))

        self.as_dataframe = pd.DataFrame(self.data_dict, index=[0])
