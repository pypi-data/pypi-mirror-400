import pandas as pd


class OvernightData:
    def __init__(self, ticker, values):


        self.tickerId = [i.get('tickerId') for i in ticker]
        self.name = [i.get('name') for i in ticker]
        self.symbol = [i.get('symbol') for i in ticker]

        self.dt = [i.get('dt') for i in values]
        self.close = [float(i.get('close')) for i in values]
        self.change = [float(i.get('change')) for i in values]
        self.changeRatio = [round(float(i.get('changeRatio'))*100,2) for i in values]
        self.overnightVolume = [float(i.get('overnightVolume')) for i in values]
        self.overnightPrice = [float(i.get('overnightPrice')) for i in values]
        self.overnightChange = [round(float(i.get('overnightChange')),2) for i in values]
        self.overnightChangeRatio = [round(float(i.get('overnightChangeRatio'))*100,2) for i in values]


        self.data_dict = { 
            'ticker_id': self.tickerId,
            'name': self.name,
            'ticker': self.symbol,
            'dt': self.dt,
            'close': self.close,
            'change': self.change,
            'change_ratio': self.changeRatio,
            'overnight_volume': self.overnightVolume,
            'overnight_price': self.overnightPrice,
            'overnight_change': self.overnightChange,
            'overnight_change_ratio': self.overnightChangeRatio

        }


        self.as_dataframe = pd.DataFrame(self.data_dict)