import pandas as pd


class OvernightTicker:
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


class OvernightValues:
    def __init__(self, values):
        self.tickerId = [i.get('tickerId') for i in values]
        self.close = [float(i.get('close')) for i in values]
        self.change = [float(i.get('change')) for i in values]
        self.changeRatio = [round(float(i.get('changeRatio'))*100,2) for i in values]
        self.overnightVolume = [float(i.get('overnightVolume')) for i in values]
        self.overnightPrice = [float(i.get('overnightPrice')) for i in values]
        self.overnightChange = [float(i.get('overnightChange')) for i in values]
        self.overnightChangeRatio = [round(float(i.get('overnightChangeRatio'))*100,2) for i in values]


        self.data_dict = { 
            'ticker_id': self.tickerId,
            'close': self.close,
            'change': self.change,
            'change_pct': self.changeRatio,
            'ovn_volume': self.overnightVolume,
            'ovn_price': self.overnightPrice,
            'ovn_change': self.overnightChange,
            'ovn_change_pct': self.overnightChangeRatio
        }


        self.as_dataframe = pd.DataFrame(self.data_dict)