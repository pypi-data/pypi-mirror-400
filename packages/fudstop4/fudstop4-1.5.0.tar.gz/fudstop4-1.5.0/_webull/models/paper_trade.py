import pandas as pd



class PaperOrder:
    def __init__(self, data):
        pass




class Positions:
    def __init__(self, positions):

        self.id = [i.get('id') for i in positions]
        self.quantity = [int(i.get('quantity')) for i in positions]
        self.marketValue = [float(i.get('marketValue')) for i in positions]
        self.unrealizedProfitLoss = [i.get('unrealizedProfitLoss') for i in positions]
        self.strike = [float(i.get('optionExercisePrice')) for i in positions]
        self.unrealizedProfitLossRate = [float(i.get('unrealizedProfitLossRate')) for i in positions]
        self.costPrice = [float(i.get('costPrice')) for i in positions]
        self.lastPrice = [float(i.get('lastPrice')) for i in positions]
        self.proportion = [float(i.get('proportion')) for i in positions]
        self.symbol = [i.get('symbol') for i in positions]


        self.data_dict = { 
            'position_id': self.id,
            'ticker': self.symbol,
            'strike': self.strike,
            'quantity': self.quantity,
            'market_value': self.marketValue,
            'unrealized_pl': self.unrealizedProfitLoss,
            'unrealized_pl_rate': self.unrealizedProfitLossRate,
            'cost_basis': self.costPrice,
            'latest_price': self.lastPrice,
            'proportion': self.proportion,
            
        }

        self.as_dataframe = pd.DataFrame(self.data_dict)


class Items:
    def __init__(self, items):
        self.quantity = [int(i.get('quantity')) for i in items]
        self.lastPrice = [float(i.get('lastPrice')) for i in items]
        self.costPrice = [float(i.get('costPrice')) for i in items]
        self.totalCost = [float(i.get('totalCost')) for i in items]
        self.marketValue = [float(i.get('marketValue')) for i in items]
        self.unrealizedProfitLoss = [float(i.get('unrealizedProfitLoss')) for i in items]
        self.unrealizedProfitLossRate = [float(i.get('unrealizedProfitLossRate')) for i in items]
        self.proportion = [float(i.get('proportion')) for i in items]
        self.legId = [i.get('legId') for i in items]
        self.ticker = [i.get('ticker') for i in items]
        self.action = [i.get('action') for i in items]
        self.option_id = [i.get('tickerId') for i in items]
        self.ticker_id = [i.get('belongTickerId') for i in items]
        self.call_put = [i.get('optionType') for i in items]
        self.expiry = [i.get('optionExpireDate') for i in items]
        self.strike = [float(i.get('optionExercisePrice')) for i in items]
        self.cycle = [int(i.get('optionCycle')) for i in items]
        self.ticker = [i.get('symbol') for i in items]


        self.data_dict = { 
            'leg_id': self.legId,
            'ticker_id': self.ticker_id,
            'option_id': self.option_id,
            'ticker': self.ticker,
            'strike': self.strike,
            'call_put': self.call_put,
            'expiry': self.expiry,
            'cycle': self.cycle,
            'latest_price': self.lastPrice,
            'cost_basis': self.costPrice,
            'total_cost': self.totalCost,
            'market_value': self.marketValue,
            'unrealized_pl': self.unrealizedProfitLoss,
            'unrealized_pl_rate': self.unrealizedProfitLossRate,
            'proportion': self.proportion,
            'action': self.action
            

        }


        self.as_dataframe = pd.DataFrame(self.data_dict)


class Capital:
    def __init__(self, capital):

        self.netLiquidationValue = float(capital.get('netLiquidationValue'))
        self.unrealizedProfitLoss = float(capital.get('unrealizedProfitLoss'))
        self.unrealizedProfitLossRate = float(capital.get('unrealizedProfitLossRate'))
        self.buyingPower = float(capital.get('buyingPower'))
        self.totalCashValue = float(capital.get('totalCashValue'))
        self.totalMarketValue = float(capital.get('totalMarketValue'))
        self.totalCost = float(capital.get('totalCost'))


        self.data_dict = { 
            'net_liquidation_value': self.netLiquidationValue,
            'unrealized_pl': self.unrealizedProfitLoss,
            'unrealized_pl_rate': self.unrealizedProfitLossRate,
            'buying_power': self.buyingPower,
            'total_cash_value': self.totalCashValue,
            'total_market_value': self.totalMarketValue,
            'total_cost': self.totalCost
        }


        self.as_dataframe = pd.DataFrame(self.data_dict, index=[0])