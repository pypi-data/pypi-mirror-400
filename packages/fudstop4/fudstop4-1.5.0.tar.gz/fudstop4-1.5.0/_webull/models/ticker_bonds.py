import pandas as pd
from fudstop4.apis.webull.webull_trading import WebullTrading
trading = WebullTrading()



class TickerBonds:
    def __init__(self, data):
        self.tickerId = [i.get('tickerId') for i in data]
        self.symbol = [i.get('symbol') for i in data]
        self.isin = [i.get('isin') for i in data]
        self.disSymbol = [i.get('disSymbol') for i in data]
        self.type = [i.get('type') for i in data]
        self.regionId = [i.get('regionId') for i in data]
        self.fullName = [i.get('fullName') for i in data]
        self.name = [i.get('name') for i in data]
        self.currencyId = [i.get('currencyId') for i in data]
        self.exchangeId = [i.get('exchangeId') for i in data]
        self.securityType = [i.get('securityType') for i in data]
        self.subType = [i.get('subType') for i in data]
        self.regionCode = [i.get('regionCode') for i in data]
        self.exchangeCode = [i.get('exchangeCode') for i in data]
        self.template = [i.get('template') for i in data]
        self.expDate = [i.get('expDate') for i in data]
        self.parValue = [i.get('parValue') for i in data]
        self.coupon = [i.get('coupon') for i in data]
        self.accruedInterest = [i.get('accruedInterest') for i in data]
        self.couponFrequency = [i.get('couponFrequency') for i in data]
        self.couponFreqDesc = [i.get('couponFreqDesc') for i in data]
        self.term = [i.get('term') for i in data]
        self.close = [i.get('close') for i in data]
        self.preClose = [i.get('preClose') for i in data]
        self.change = [i.get('change') for i in data]
        self.changeRatio = [i.get('changeRatio') for i in data]
        self.bondYield = [i.get('bondYield') for i in data]
        self.yieldYTW = [i.get('yieldYTW') for i in data]
        self.askPrice = [i.get('askPrice') for i in data]
        self.bidPrice = [i.get('bidPrice') for i in data]
        self.askMinSize = [i.get('askMinSize') for i in data]
        self.bidMinSize = [i.get('bidMinSize') for i in data]
        self.askVolume = [i.get('askVolume') for i in data]
        self.bidVolume = [i.get('bidVolume') for i in data]
        self.askYield = [i.get('askYield') for i in data]
        self.oddLotSupport = [i.get('oddLotSupport') for i in data]
        self.askYieldYTW = [i.get('askYieldYTW') for i in data]
        self.bidYield = [i.get('bidYield') for i in data]
        self.bidYieldYTW = [i.get('bidYieldYTW') for i in data]
        self.rating = [i.get('rating') for i in data]
        self.duration = [i.get('duration') for i in data]
        self.convexity = [i.get('convexity') for i in data]
        self.issueDate = [i.get('issueDate') for i in data]
        self.issuerName = [i.get('issuerName') for i in data]
        self.isCallable = [i.get('isCallable') for i in data]
        self.nextCallDate = [i.get('nextCallDate') for i in data]
        self.nextCallPrice = [i.get('nextCallPrice') for i in data]
        self.belongTickerId = [i.get('belongTickerId') for i in data]


        def _to_float_safe(val_list):
            # Converts a list to float if possible, leaves as-is if not
            return [float(x) if x is not None and not isinstance(x, bool) else x for x in val_list]

        self.data_dict = {
            "ticker_id": self.tickerId,
            "bond_ticker": self.symbol,
            "isin": self.isin,
            "full_name": self.fullName,
            "name": self.name,
            "expiry": self.expDate,
            "par_value": _to_float_safe(self.parValue),
            "coupon": _to_float_safe(self.coupon),
            "accrued_interest": _to_float_safe(self.accruedInterest),
            "coupon_frequency": _to_float_safe(self.couponFrequency),
            "coupon_freq_desc": self.couponFreqDesc,
            "term": self.term,
            "close": _to_float_safe(self.close),
            "change": _to_float_safe(self.change),
            "change_ratio": _to_float_safe(self.changeRatio),
            "bond_yield": _to_float_safe(self.bondYield),
            "yield_ytw": _to_float_safe(self.yieldYTW),
            "ask_price": _to_float_safe(self.askPrice),
            "bid_price": _to_float_safe(self.bidPrice),
            "ask_min_size": _to_float_safe(self.askMinSize),
            "bid_min_size": _to_float_safe(self.bidMinSize),
            "ask_volume": _to_float_safe(self.askVolume),
            "bid_volume": _to_float_safe(self.bidVolume),
            "ask_yield": _to_float_safe(self.askYield),
            "odd_lot_support": self.oddLotSupport,  # likely bool
            "ask_yield_ytw": _to_float_safe(self.askYieldYTW),
            "bid_yield": _to_float_safe(self.bidYield),
            "bid_yield_ytw": _to_float_safe(self.bidYieldYTW),
            "rating": self.rating,
            "duration": _to_float_safe(self.duration),
            "convexity": _to_float_safe(self.convexity),
            "issue_date": self.issueDate,
            "issuer_name": self.issuerName,
            "is_callable": self.isCallable,  # likely bool
            "next_call_date": self.nextCallDate,
            "next_call_price": _to_float_safe(self.nextCallPrice),
            "ticker_id": _to_float_safe(self.belongTickerId)
        }



        self.as_dataframe = pd.DataFrame(self.data_dict)
