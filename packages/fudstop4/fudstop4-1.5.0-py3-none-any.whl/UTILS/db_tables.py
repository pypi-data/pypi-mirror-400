import pandas as pd
import json
from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()
client = OpenAI(api_key=os.environ.get('OPENAI_KEY'))

class InfoTable:
    """
    Represents a single ticker's comprehensive summary of **equity and options data**, 
    including pricing, dividend details, volatility, volume, correlation, and additional analytics.

    Each attribute represents a scalar value for the ticker (first item in the source data).

    Main field categories:
        - **Identification**: `ticker`, `industry`, `currency`
        - **Price & Quotes**: `price`, `high`, `low`, `open`, `prev_close`, `mid`, `spread`, `bid`, `ask`
        - **Bid/Ask Book**: `bid_size`, `ask_size`, `bid_ask_ratio`
        - **Dividends**: `dividend_date`, `dividend_amount`, `dividend_frequency`, `dividend_payout_ratio`, `yield_`
        - **Volume & OI**: `stock_vol`, `opt_vol`, `open_interest`, `avg_opt_vol_1mo`, `avg_opt_oi_1mo`
        - **Options Greeks/Volatility**:
            - `ivx*`, `ivx*_chg`, `ivx*_chg_percent`, `ivx*_chg_open`, `ivx*_chg_percent_open`
            - `ivr*`, `iv_rank`, `iv_ratio`, `ivp*`
        - **Historical Volatility**: `hv*`, `hvp*`
        - **Beta/Correlation**: `beta*`, `beta_ratio`, `corr*d`
        - **Change Metrics**: `change`, `change_percent`, `change_open`, `change_percent_open`
        - **Volume by Type**: `call_vol`, `put_vol`
        - **Market Stats**: `market_cap`, `outstanding_shares`, `earnings_yield`, `eps`, `pe`, `at_close`
        - **52-Week Stats**: `high_price_52wk`, `low_price_52wk`
        - **Analytics/Meta**: `volatile_rank`, `volatility_per_share`, `sentiment`, `update_date`, `last_date`, `insertion_timestamp`
        - **Other**: `spread`

    All fields are extracted as scalars from the first element in the provided `data` list.

    Args:
        data (list of dict): A list containing one dict (the data row for this ticker).

    Example:
        table = InfoTable(data)
        print(table.price, table.dividend_date)
    """
    def __init__(self, data):
        self.ticker = [i.get('ticker') for i in data]
        self.dividend_date = [i.get('dividend_date') for i in data]
        self.dividend_amount = [i.get('dividend_amount') for i in data]
        self.dividend_frequency = [i.get('dividend_frequency') for i in data]
        self.yield_ = [i.get('yield') for i in data]  # 'yield' is a reserved keyword
        self.bid_ask_ratio = [i.get('bid_ask_ratio') for i in data]
        self.bid_size = [i.get('bid_size') for i in data]
        self.ask_size = [i.get('ask_size') for i in data]
        self.opt_vol = [i.get('opt_vol') for i in data]
        self.stock_vol = [i.get('stock_vol') for i in data]
        self.ivx7 = [i.get('ivx7') for i in data]
        self.ivx14 = [i.get('ivx14') for i in data]
        self.ivx21 = [i.get('ivx21') for i in data]
        self.ivx30 = [i.get('ivx30') for i in data]
        self.ivx60 = [i.get('ivx60') for i in data]
        self.ivx90 = [i.get('ivx90') for i in data]
        self.ivx120 = [i.get('ivx120') for i in data]
        self.ivx150 = [i.get('ivx150') for i in data]
        self.ivx180 = [i.get('ivx180') for i in data]
        self.ivx270 = [i.get('ivx270') for i in data]
        self.ivx360 = [i.get('ivx360') for i in data]
        self.ivx720 = [i.get('ivx720') for i in data]
        self.ivx1080 = [i.get('ivx1080') for i in data]
        self.ivx7_chg = [i.get('ivx7_chg') for i in data]
        self.ivx14_chg = [i.get('ivx14_chg') for i in data]
        self.ivx21_chg = [i.get('ivx21_chg') for i in data]
        self.ivx30_chg = [i.get('ivx30_chg') for i in data]
        self.ivx60_chg = [i.get('ivx60_chg') for i in data]
        self.ivx90_chg = [i.get('ivx90_chg') for i in data]
        self.ivx120_chg = [i.get('ivx120_chg') for i in data]
        self.ivx150_chg = [i.get('ivx150_chg') for i in data]
        self.ivx180_chg = [i.get('ivx180_chg') for i in data]
        self.ivx270_chg = [i.get('ivx270_chg') for i in data]
        self.ivx360_chg = [i.get('ivx360_chg') for i in data]
        self.ivx720_chg = [i.get('ivx720_chg') for i in data]
        self.ivx1080_chg = [i.get('ivx1080_chg') for i in data]
        self.ivx7_chg_percent = [i.get('ivx7_chg_percent') for i in data]
        self.ivx14_chg_percent = [i.get('ivx14_chg_percent') for i in data]
        self.ivx21_chg_percent = [i.get('ivx21_chg_percent') for i in data]
        self.ivx30_chg_percent = [i.get('ivx30_chg_percent') for i in data]
        self.ivx60_chg_percent = [i.get('ivx60_chg_percent') for i in data]
        self.ivx90_chg_percent = [i.get('ivx90_chg_percent') for i in data]
        self.ivx120_chg_percent = [i.get('ivx120_chg_percent') for i in data]
        self.ivx150_chg_percent = [i.get('ivx150_chg_percent') for i in data]
        self.ivx180_chg_percent = [i.get('ivx180_chg_percent') for i in data]
        self.ivx270_chg_percent = [i.get('ivx270_chg_percent') for i in data]
        self.ivx360_chg_percent = [i.get('ivx360_chg_percent') for i in data]
        self.ivx720_chg_percent = [i.get('ivx720_chg_percent') for i in data]
        self.ivx1080_chg_percent = [i.get('ivx1080_chg_percent') for i in data]
        self.ivx7_chg_open = [i.get('ivx7_chg_open') for i in data]
        self.ivx14_chg_open = [i.get('ivx14_chg_open') for i in data]
        self.ivx21_chg_open = [i.get('ivx21_chg_open') for i in data]
        self.ivx30_chg_open = [i.get('ivx30_chg_open') for i in data]
        self.ivx60_chg_open = [i.get('ivx60_chg_open') for i in data]
        self.ivx90_chg_open = [i.get('ivx90_chg_open') for i in data]
        self.ivx120_chg_open = [i.get('ivx120_chg_open') for i in data]
        self.ivx150_chg_open = [i.get('ivx150_chg_open') for i in data]
        self.ivx180_chg_open = [i.get('ivx180_chg_open') for i in data]
        self.ivx270_chg_open = [i.get('ivx270_chg_open') for i in data]
        self.ivx360_chg_open = [i.get('ivx360_chg_open') for i in data]
        self.ivx720_chg_open = [i.get('ivx720_chg_open') for i in data]
        self.ivx1080_chg_open = [i.get('ivx1080_chg_open') for i in data]
        self.ivx7_chg_percent_open = [i.get('ivx7_chg_percent_open') for i in data]
        self.ivx14_chg_percent_open = [i.get('ivx14_chg_percent_open') for i in data]
        self.ivx21_chg_percent_open = [i.get('ivx21_chg_percent_open') for i in data]
        self.ivx30_chg_percent_open = [i.get('ivx30_chg_percent_open') for i in data]
        self.ivx60_chg_percent_open = [i.get('ivx60_chg_percent_open') for i in data]
        self.ivx90_chg_percent_open = [i.get('ivx90_chg_percent_open') for i in data]
        self.ivx120_chg_percent_open = [i.get('ivx120_chg_percent_open') for i in data]
        self.ivx150_chg_percent_open = [i.get('ivx150_chg_percent_open') for i in data]
        self.ivx180_chg_percent_open = [i.get('ivx180_chg_percent_open') for i in data]
        self.ivx270_chg_percent_open = [i.get('ivx270_chg_percent_open') for i in data]
        self.ivx360_chg_percent_open = [i.get('ivx360_chg_percent_open') for i in data]
        self.ivx720_chg_percent_open = [i.get('ivx720_chg_percent_open') for i in data]
        self.ivx1080_chg_percent_open = [i.get('ivx1080_chg_percent_open') for i in data]
        self.high = [i.get('high') for i in data]
        self.low = [i.get('low') for i in data]
        self.open = [i.get('open') for i in data]
        self.price = [i.get('price') for i in data]
        self.prev_close = [i.get('prev_close') for i in data]
        self.open_interest = [i.get('open_interest') for i in data]
        self.high_price_52wk = [i.get('high_price_52wk') for i in data]
        self.low_price_52wk = [i.get('low_price_52wk') for i in data]
        self.change = [i.get('change') for i in data]
        self.change_percent = [i.get('change_percent') for i in data]
        self.change_open = [i.get('change_open') for i in data]
        self.change_percent_open = [i.get('change_percent_open') for i in data]
        self.call_vol = [i.get('call_vol') for i in data]
        self.put_vol = [i.get('put_vol') for i in data]
        self.hv10 = [i.get('hv10') for i in data]
        self.hv20 = [i.get('hv20') for i in data]
        self.hv30 = [i.get('hv30') for i in data]
        self.hv60 = [i.get('hv60') for i in data]
        self.hv90 = [i.get('hv90') for i in data]
        self.hv120 = [i.get('hv120') for i in data]
        self.hv150 = [i.get('hv150') for i in data]
        self.hv180 = [i.get('hv180') for i in data]
        self.hvp10 = [i.get('hvp10') for i in data]
        self.hvp20 = [i.get('hvp20') for i in data]
        self.hvp30 = [i.get('hvp30') for i in data]
        self.hvp60 = [i.get('hvp60') for i in data]
        self.hvp90 = [i.get('hvp90') for i in data]
        self.hvp120 = [i.get('hvp120') for i in data]
        self.hvp150 = [i.get('hvp150') for i in data]
        self.hvp180 = [i.get('hvp180') for i in data]
        self.beta10d = [i.get('beta10d') for i in data]
        self.beta20d = [i.get('beta20d') for i in data]
        self.beta30d = [i.get('beta30d') for i in data]
        self.beta60d = [i.get('beta60d') for i in data]
        self.beta90d = [i.get('beta90d') for i in data]
        self.beta120d = [i.get('beta120d') for i in data]
        self.beta150d = [i.get('beta150d') for i in data]
        self.beta180d = [i.get('beta180d') for i in data]
        self.beta_ratio = [i.get('beta_ratio') for i in data]
        self.corr10d = [i.get('corr10d') for i in data]
        self.corr20d = [i.get('corr20d') for i in data]
        self.corr30d = [i.get('corr30d') for i in data]
        self.corr60d = [i.get('corr60d') for i in data]
        self.corr90d = [i.get('corr90d') for i in data]
        self.corr120d = [i.get('corr120d') for i in data]
        self.corr150d = [i.get('corr150d') for i in data]
        self.corr180d = [i.get('corr180d') for i in data]
        self.outstanding_shares = [i.get('outstanding_shares') for i in data]
        self.market_cap = [i.get('market_cap') for i in data]
        self.update_date = [i.get('update_date') for i in data]
        self.at_close = [i.get('at_close') for i in data]
        self.currency = [i.get('currency') for i in data]
        self.last_date = [i.get('last_date') for i in data]
        self.eps = [i.get('eps') for i in data]
        self.pe = [i.get('pe') for i in data]
        self.industry = [i.get('industry') for i in data]
        self.ivp30 = [i.get('ivp30') for i in data]
        self.ivp60 = [i.get('ivp60') for i in data]
        self.ivp90 = [i.get('ivp90') for i in data]
        self.sentiment = [i.get('sentiment') for i in data]
        self.volatile_rank = [i.get('volatile_rank') for i in data]
        self.volatility_per_share = [i.get('volatility_per_share') for i in data]
        self.ivr30 = [i.get('ivr30') for i in data]
        self.ivr60 = [i.get('ivr60') for i in data]
        self.ivr90 = [i.get('ivr90') for i in data]
        self.ivr120 = [i.get('ivr120') for i in data]
        self.ivr150 = [i.get('ivr150') for i in data]
        self.ivr180 = [i.get('ivr180') for i in data]
        self.iv_rank = [i.get('iv_rank') for i in data]
        self.avg_opt_vol_1mo = [i.get('avg_opt_vol_1mo') for i in data]
        self.avg_opt_oi_1mo = [i.get('avg_opt_oi_1mo') for i in data]
        self.iv_ratio = [i.get('iv_ratio') for i in data]
        self.earnings_yield = [i.get('earnings_yield') for i in data]
        self.dividend_payout_ratio = [i.get('dividend_payout_ratio') for i in data]
        self.spread = [i.get('spread') for i in data]
        self.insertion_timestamp = [i.get('insertion_timestamp') for i in data]


        self.data_dict = {
            'ticker': self.ticker,
            'dividend_date': self.dividend_date,
            'dividend_amount': self.dividend_amount,
            'dividend_frequency': self.dividend_frequency,
            'yield': self.yield_,  # Note: alias for reserved keyword
            'bid_ask_ratio': self.bid_ask_ratio,
            'bid_size': self.bid_size,
            'ask_size': self.ask_size,
            'opt_vol': self.opt_vol,
            'stock_vol': self.stock_vol,
            'ivx7': self.ivx7,
            'ivx14': self.ivx14,
            'ivx21': self.ivx21,
            'ivx30': self.ivx30,
            'ivx60': self.ivx60,
            'ivx90': self.ivx90,
            'ivx120': self.ivx120,
            'ivx150': self.ivx150,
            'ivx180': self.ivx180,
            'ivx270': self.ivx270,
            'ivx360': self.ivx360,
            'ivx720': self.ivx720,
            'ivx1080': self.ivx1080,
            'ivx7_chg': self.ivx7_chg,
            'ivx14_chg': self.ivx14_chg,
            'ivx21_chg': self.ivx21_chg,
            'ivx30_chg': self.ivx30_chg,
            'ivx60_chg': self.ivx60_chg,
            'ivx90_chg': self.ivx90_chg,
            'ivx120_chg': self.ivx120_chg,
            'ivx150_chg': self.ivx150_chg,
            'ivx180_chg': self.ivx180_chg,
            'ivx270_chg': self.ivx270_chg,
            'ivx360_chg': self.ivx360_chg,
            'ivx720_chg': self.ivx720_chg,
            'ivx1080_chg': self.ivx1080_chg,
            'ivx7_chg_percent': self.ivx7_chg_percent,
            'ivx14_chg_percent': self.ivx14_chg_percent,
            'ivx21_chg_percent': self.ivx21_chg_percent,
            'ivx30_chg_percent': self.ivx30_chg_percent,
            'ivx60_chg_percent': self.ivx60_chg_percent,
            'ivx90_chg_percent': self.ivx90_chg_percent,
            'ivx120_chg_percent': self.ivx120_chg_percent,
            'ivx150_chg_percent': self.ivx150_chg_percent,
            'ivx180_chg_percent': self.ivx180_chg_percent,
            'ivx270_chg_percent': self.ivx270_chg_percent,
            'ivx360_chg_percent': self.ivx360_chg_percent,
            'ivx720_chg_percent': self.ivx720_chg_percent,
            'ivx1080_chg_percent': self.ivx1080_chg_percent,
            'ivx7_chg_open': self.ivx7_chg_open,
            'ivx14_chg_open': self.ivx14_chg_open,
            'ivx21_chg_open': self.ivx21_chg_open,
            'ivx30_chg_open': self.ivx30_chg_open,
            'ivx60_chg_open': self.ivx60_chg_open,
            'ivx90_chg_open': self.ivx90_chg_open,
            'ivx120_chg_open': self.ivx120_chg_open,
            'ivx150_chg_open': self.ivx150_chg_open,
            'ivx180_chg_open': self.ivx180_chg_open,
            'ivx270_chg_open': self.ivx270_chg_open,
            'ivx360_chg_open': self.ivx360_chg_open,
            'ivx720_chg_open': self.ivx720_chg_open,
            'ivx1080_chg_open': self.ivx1080_chg_open,
            'ivx7_chg_percent_open': self.ivx7_chg_percent_open,
            'ivx14_chg_percent_open': self.ivx14_chg_percent_open,
            'ivx21_chg_percent_open': self.ivx21_chg_percent_open,
            'ivx30_chg_percent_open': self.ivx30_chg_percent_open,
            'ivx60_chg_percent_open': self.ivx60_chg_percent_open,
            'ivx90_chg_percent_open': self.ivx90_chg_percent_open,
            'ivx120_chg_percent_open': self.ivx120_chg_percent_open,
            'ivx150_chg_percent_open': self.ivx150_chg_percent_open,
            'ivx180_chg_percent_open': self.ivx180_chg_percent_open,
            'ivx270_chg_percent_open': self.ivx270_chg_percent_open,
            'ivx360_chg_percent_open': self.ivx360_chg_percent_open,
            'ivx720_chg_percent_open': self.ivx720_chg_percent_open,
            'ivx1080_chg_percent_open': self.ivx1080_chg_percent_open,
            'high': self.high,
            'low': self.low,
            'open': self.open,
            'price': self.price,
            'prev_close': self.prev_close,
            'open_interest': self.open_interest,
            'high_price_52wk': self.high_price_52wk,
            'low_price_52wk': self.low_price_52wk,
            'change': self.change,
            'change_percent': self.change_percent,
            'change_open': self.change_open,
            'change_percent_open': self.change_percent_open,
            'call_vol': self.call_vol,
            'put_vol': self.put_vol,
            'hv10': self.hv10,
            'hv20': self.hv20,
            'hv30': self.hv30,
            'hv60': self.hv60,
            'hv90': self.hv90,
            'hv120': self.hv120,
            'hv150': self.hv150,
            'hv180': self.hv180,
            'hvp10': self.hvp10,
            'hvp20': self.hvp20,
            'hvp30': self.hvp30,
            'hvp60': self.hvp60,
            'hvp90': self.hvp90,
            'hvp120': self.hvp120,
            'hvp150': self.hvp150,
            'hvp180': self.hvp180,
            'beta10d': self.beta10d,
            'beta20d': self.beta20d,
            'beta30d': self.beta30d,
            'beta60d': self.beta60d,
            'beta90d': self.beta90d,
            'beta120d': self.beta120d,
            'beta150d': self.beta150d,
            'beta180d': self.beta180d,
            'beta_ratio': self.beta_ratio,
            'corr10d': self.corr10d,
            'corr20d': self.corr20d,
            'corr30d': self.corr30d,
            'corr60d': self.corr60d,
            'corr90d': self.corr90d,
            'corr120d': self.corr120d,
            'corr150d': self.corr150d,
            'corr180d': self.corr180d,
            'outstanding_shares': self.outstanding_shares,
            'market_cap': self.market_cap,
            'update_date': self.update_date,
            'at_close': self.at_close,
            'currency': self.currency,
            'last_date': self.last_date,
            'eps': self.eps,
            'pe': self.pe,
            'industry': self.industry,
            'ivp30': self.ivp30,
            'ivp60': self.ivp60,
            'ivp90': self.ivp90,
            'sentiment': self.sentiment,
            'volatile_rank': self.volatile_rank,
            'volatility_per_share': self.volatility_per_share,
            'ivr30': self.ivr30,
            'ivr60': self.ivr60,
            'ivr90': self.ivr90,
            'ivr120': self.ivr120,
            'ivr150': self.ivr150,
            'ivr180': self.ivr180,
            'iv_rank': self.iv_rank,
            'avg_opt_vol_1mo': self.avg_opt_vol_1mo,
            'avg_opt_oi_1mo': self.avg_opt_oi_1mo,
            'iv_ratio': self.iv_ratio,
            'earnings_yield': self.earnings_yield,
            'dividend_payout_ratio': self.dividend_payout_ratio,
            'spread': self.spread,
            'insertion_timestamp': self.insertion_timestamp
        }
        self.as_dataframe = pd.DataFrame(self.data_dict)

class WbOptsTable:
    """
    Represents option contract data pulled from Webull.

    This table includes rich intraday and historical option data, including Greeks,
    volume, open interest, bid/ask pricing, and technical changes for each option contract.

    Attributes:
        option_symbol (list): The unique option symbol (e.g., AAPL240719C00175000).
        option_id (list): Webull's internal ID for this specific option contract.
        ticker_id (list): Webull's internal ID for the associated stock ticker.
        ticker (list): The underlying equity symbol (e.g., 'AAPL').
        strike (list): Strike price of the option.
        call_put (list): Type of contract ('call' or 'put').
        expiry (list): Option expiration date (e.g., '2024-07-19').
        open (list): Opening price for the option today.
        high (list): Intraday high for this option.
        low (list): Intraday low for this option.
        close (list): Most recent closing price for the option.
        volume (list): Total contract volume traded today.
        ask_volume (list): Contracts sitting on the ask side.
        bid_volume (list): Contracts sitting on the bid side.
        ask_price (list): Current best ask price.
        bid_price (list): Current best bid price.
        oi (list): Current open interest for the contract.
        oi_change (list): Change in open interest vs. previous day.
        trade_time (list): Timestamp of the most recent trade.
        trade_stamp (list): Unix timestamp format of trade_time.
        delta (list): Delta Greek value.
        gamma (list): Gamma Greek value.
        theta (list): Theta Greek value.
        vega (list): Vega Greek value.
        rho (list): Rho Greek value.
        iv (list): Implied volatility for this contract.
        activity (list): Qualitative label like "unusual", "sweep", or "block".
        latest_volume (list): Volume from most recent burst of activity.
        change (list): Net price change on the day.
        change_pct (list): Percent change on the day.
        insertion_timestamp (list): Timestamp when data was added to the database.
    """
    def compute_drima(self):
        df = self.as_dataframe.copy()
        
        # Only valid rows with numeric strikes and IVs
        df = df[df['strike'].notnull() & df['iv'].notnull()]
        
        # Prepare empty column
        df['drima'] = None

        # Group by ticker, expiry, and call/put
        grouped = df.groupby(['ticker', 'expiry', 'call_put'])

        all_rows = []
        for (ticker, expiry, call_put), group in grouped:
            sorted_group = group.sort_values('strike').reset_index(drop=True)
            
            ivs = sorted_group['iv'].values
            strikes = sorted_group['strike'].values
            
            drima_vals = []
            for i in range(len(ivs)):
                left_diff = abs(ivs[i] - ivs[i - 1]) if i > 0 else None
                right_diff = abs(ivs[i] - ivs[i + 1]) if i < len(ivs) - 1 else None

                # Use average of both differences if both neighbors exist
                if left_diff is not None and right_diff is not None:
                    drima = (left_diff + right_diff) / 2
                elif left_diff is not None:
                    drima = left_diff
                elif right_diff is not None:
                    drima = right_diff
                else:
                    drima = None

                drima_vals.append(drima)
            
            sorted_group['drima'] = drima_vals
            all_rows.append(sorted_group)
        # Merge all groups back into the main dataframe
        self.as_dataframe = pd.concat(all_rows, ignore_index=True)
        self.data_dict['drima'] = self.as_dataframe['drima'].tolist()
        self.drima = self.data_dict['drima']

    def __init__(self, data):
        self.option_symbol       = [i.get('option_symbol')       for i in data]
        self.option_id           = [i.get('option_id')           for i in data]
        self.ticker_id           = [i.get('ticker_id')           for i in data]
        self.ticker              = [i.get('ticker')              for i in data]
        self.strike              = [i.get('strike')              for i in data]
        self.call_put            = [i.get('call_put')            for i in data]
        self.expiry              = [i.get('expiry')              for i in data]
        self.open                = [i.get('open')                for i in data]
        self.high                = [i.get('high')                for i in data]
        self.low                 = [i.get('low')                 for i in data]
        self.close               = [i.get('close')               for i in data]
        self.volume              = [i.get('volume')              for i in data]
        self.ask_volume          = [i.get('ask_volume')          for i in data]
        self.bid_volume          = [i.get('bid_volume')          for i in data]
        self.ask_price           = [i.get('ask_price')           for i in data]
        self.bid_price           = [i.get('bid_price')           for i in data]
        self.oi                  = [i.get('oi')                  for i in data]
        self.oi_change           = [i.get('oi_change')           for i in data]
        self.trade_time          = [i.get('trade_time')          for i in data]
        self.trade_stamp         = [i.get('trade_stamp')         for i in data]
        self.delta               = [i.get('delta')               for i in data]
        self.gamma               = [i.get('gamma')               for i in data]
        self.theta               = [i.get('theta')               for i in data]
        self.vega                = [i.get('vega')                for i in data]
        self.rho                 = [i.get('rho')                 for i in data]
        self.iv                  = [i.get('iv')                  for i in data]
        self.activity            = [i.get('activity')            for i in data]
        self.latest_volume       = [i.get('latest_volume')       for i in data]
        self.change              = [i.get('change')              for i in data]
        self.change_pct          = [i.get('change_pct')          for i in data]
        self.insertion_timestamp = [i.get('insertion_timestamp') for i in data]


        self.data_dict = {
            'option_symbol': self.option_symbol,
            'option_id': self.option_id,
            'ticker_id': self.ticker_id,
            'ticker': self.ticker,
            'strike': self.strike,
            'call_put': self.call_put,
            'expiry': self.expiry,
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'volume': self.volume,
            'ask_volume': self.ask_volume,
            'bid_volume': self.bid_volume,
            'ask_price': self.ask_price,
            'bid_price': self.bid_price,
            'oi': self.oi,
            'oi_change': self.oi_change,
            'trade_time': self.trade_time,
            'trade_stamp': self.trade_stamp,
            'delta': self.delta,
            'gamma': self.gamma,
            'theta': self.theta,
            'vega': self.vega,
            'rho': self.rho,
            'iv': self.iv,
            'activity': self.activity,
            'latest_volume': self.latest_volume,
            'change': self.change,
            'change_pct': self.change_pct,
            'insertion_timestamp': self.insertion_timestamp
        }
        self.as_dataframe = pd.DataFrame(self.data_dict)





class MostActive:
    """
    Represents the most actively traded stocks from Webull's ranking engine.

    This table helps identify volume leaders, top movers, and potential momentum plays.

    Attributes:
        ticker_id (list): Webull's internal ID for the ticker.
        name (list): Full name of the company.
        ticker (list): Ticker symbol (e.g., 'TSLA').
        trade_time (list): Timestamp of the latest recorded trade.
        status (list): Status indicator (e.g., 'open', 'closed').
        close (list): Most recent price.
        change (list): Absolute price change from previous close.
        change_ratio (list): Percent change from previous close.
        market_value (list): Market cap or valuation estimate.
        volume (list): Intraday trading volume.
        turnover_rate (list): Percent of float traded today.
        dividend (list): Dividend yield or most recent payout.
        fifty_high (list): 52-week high price.
        fifty_low (list): 52-week low price.
        open (list): Opening price of the day.
        high (list): High price of the day.
        low (list): Low price of the day.
        vibration (list): Webull volatility rating for the ticker.
        rank_value (list): Numeric score used to rank this ticker.
        is_ratio (list): Flag used internally for ranking adjustments.
        quant_rating (list): Quantitative rating score (0–100).
        debt_assets_ratio (list): Debt-to-assets financial metric.
        rank_type (list): Rank category (e.g., 'volume_leaders', 'top_gainers').
        insertion_timestamp (list): When the data was pulled and logged.
    """
    def __init__(self, data):
        self.ticker_id           = [i.get('ticker_id')           for i in data]
        self.name                = [i.get('name')                for i in data]
        self.ticker              = [i.get('ticker')              for i in data]
        self.trade_time          = [i.get('trade_time')          for i in data]
        self.status              = [i.get('status')              for i in data]
        self.close               = [i.get('close')               for i in data]
        self.change              = [i.get('change')              for i in data]
        self.change_ratio        = [i.get('change_ratio')        for i in data]
        self.market_value        = [i.get('market_value')        for i in data]
        self.volume              = [i.get('volume')              for i in data]
        self.turnover_rate       = [i.get('turnover_rate')       for i in data]
        self.dividend            = [i.get('dividend')            for i in data]
        self.fifty_high          = [i.get('fifty_high')          for i in data]
        self.fifty_low           = [i.get('fifty_low')           for i in data]
        self.open                = [i.get('open')                for i in data]
        self.high                = [i.get('high')                for i in data]
        self.low                 = [i.get('low')                 for i in data]
        self.vibration           = [i.get('vibration')           for i in data]
        self.rank_value          = [i.get('rank_value')          for i in data]
        self.is_ratio            = [i.get('is_ratio')            for i in data]
        self.quant_rating        = [i.get('quant_rating')        for i in data]
        self.debt_assets_ratio   = [i.get('debt_assets_ratio')   for i in data]
        self.rank_type           = [i.get('rank_type')           for i in data]
        self.insertion_timestamp = [i.get('insertion_timestamp') for i in data]




class PlaysTable:
    """
    Represents detailed technical and statistical signals for a financial instrument (typically options or equities),
    including candle data, statistical deviation channels (SDC), Bollinger Bands, RSI, MACD, linear regression, and
    TD Sequential indicators. Each attribute is a list corresponding to one row per timestamped observation.

    Attributes:
        ts (list): Timestamps of each observation.
        o (list): Open price.
        c (list): Close price.
        h (list): High price.
        l (list): Low price.
        v (list): Volume traded during the interval.
        vwap (list): Volume-weighted average price.
        roll_mean_sdc (list): Rolling mean used in SDC calculations.
        roll_std_sdc (list): Rolling standard deviation used in SDC calculations.
        sdc_upper1 (list): First upper boundary of the SDC channel.
        sdc_signal (list): Boolean or numeric indicator signaling an SDC event.
        rsi (list): Relative Strength Index (default 14-period).
        middle_band (list): Middle line of Bollinger Bands (usually the rolling mean).
        upper_band (list): Upper Bollinger Band.
        lower_band (list): Lower Bollinger Band.
        upper_bb_trend (list): Direction/trend component of the upper Bollinger Band.
        lower_bb_trend (list): Direction/trend component of the lower Bollinger Band.
        upper_bb_angle (list): Angle of the upper Bollinger Band (absolute).
        middle_bb_angle (list): Angle of the middle Bollinger Band (absolute).
        lower_bb_angle (list): Angle of the lower Bollinger Band (absolute).
        upper_bb_rel_angle (list): Angle of upper Bollinger Band relative to slope baseline.
        middle_bb_rel_angle (list): Angle of middle Bollinger Band relative to slope baseline.
        lower_bb_rel_angle (list): Angle of lower Bollinger Band relative to slope baseline.
        candle_above_upper (list): Boolean flag if any part of candle is above upper BB.
        candle_below_lower (list): Boolean flag if any part of candle is below lower BB.
        candle_completely_above_upper (list): True if high and low are both above upper BB.
        candle_partially_above_upper (list): True if high is above upper BB, but low is not.
        candle_completely_below_lower (list): True if high and low are both below lower BB.
        candle_partially_below_lower (list): True if low is below lower BB, but high is not.
        td_buy_count (list): TD Sequential buy setup count.
        td_sell_count (list): TD Sequential sell setup count.
        macd_curvature (list): Curvature or slope change of the MACD line.
        timespan (list): Timeframe of the observation (e.g., 'm1', 'm5', 'm60', 'd1').
        ticker (list): Ticker symbol (e.g., 'AAPL').
        insertion_timestamp (list): Timestamp when this row was inserted into the database.
        sdc_base (list): Base value used in SDC calculation.
        sdc_lower1 (list): First lower boundary of the SDC channel.
        linreg_slope (list): Slope of linear regression over windowed interval.
        linreg_intercept (list): Intercept of the linear regression.
        linreg_std (list): Standard deviation of points from the linear regression line.
        sdc_upper (list): Full upper bound of the SDC range.
        sdc_lower (list): Full lower bound of the SDC range.
        sym (list): Option symbol or alias, if applicable.
        td (list): TD Sequential count direction (buy/sell side).
        macd (list): Current MACD value (difference between MACD line and signal line).
        expiry (list): Option expiry date (if applicable).
        strike (list): Option strike price.
        call_put (list): Type of option ('call' or 'put').
        mid (list): Mid price of the option (average of bid/ask).
        symbol (list): Full option symbol (e.g., 'AAPL_081624C200').
        rsi_35 (list): Alternative RSI calculated over a 35-period window.
    """
    def __init__(self, data):
        self.ts                            = [i.get('ts')                            for i in data]
        self.o                             = [i.get('o')                             for i in data]
        self.c                             = [i.get('c')                             for i in data]
        self.h                             = [i.get('h')                             for i in data]
        self.l                             = [i.get('l')                             for i in data]
        self.v                             = [i.get('v')                             for i in data]
        self.vwap                          = [i.get('vwap')                          for i in data]
        self.roll_mean_sdc                 = [i.get('roll_mean_sdc')                 for i in data]
        self.roll_std_sdc                  = [i.get('roll_std_sdc')                  for i in data]
        self.sdc_upper1                    = [i.get('sdc_upper1')                    for i in data]
        self.sdc_signal                    = [i.get('sdc_signal')                    for i in data]
        self.rsi                           = [i.get('rsi')                           for i in data]
        self.middle_band                   = [i.get('middle_band')                   for i in data]
        self.upper_band                    = [i.get('upper_band')                    for i in data]
        self.lower_band                    = [i.get('lower_band')                    for i in data]
        self.upper_bb_trend                = [i.get('upper_bb_trend')                for i in data]
        self.lower_bb_trend                = [i.get('lower_bb_trend')                for i in data]
        self.upper_bb_angle                = [i.get('upper_bb_angle')                for i in data]
        self.middle_bb_angle               = [i.get('middle_bb_angle')               for i in data]
        self.lower_bb_angle                = [i.get('lower_bb_angle')                for i in data]
        self.upper_bb_rel_angle            = [i.get('upper_bb_rel_angle')            for i in data]
        self.middle_bb_rel_angle           = [i.get('middle_bb_rel_angle')           for i in data]
        self.lower_bb_rel_angle            = [i.get('lower_bb_rel_angle')            for i in data]
        self.candle_above_upper            = [i.get('candle_above_upper')            for i in data]
        self.candle_below_lower            = [i.get('candle_below_lower')            for i in data]
        self.candle_completely_above_upper = [i.get('candle_completely_above_upper') for i in data]
        self.candle_partially_above_upper  = [i.get('candle_partially_above_upper')  for i in data]
        self.candle_completely_below_lower = [i.get('candle_completely_below_lower') for i in data]
        self.candle_partially_below_lower  = [i.get('candle_partially_below_lower')  for i in data]
        self.td_buy_count                  = [i.get('td_buy_count')                  for i in data]
        self.td_sell_count                 = [i.get('td_sell_count')                 for i in data]
        self.macd_curvature                = [i.get('macd_curvature')                for i in data]
        self.timespan                      = [i.get('timespan')                      for i in data]
        self.ticker                        = [i.get('ticker')                        for i in data]
        self.insertion_timestamp           = [i.get('insertion_timestamp')           for i in data]
        self.sdc_base                      = [i.get('sdc_base')                      for i in data]
        self.sdc_lower1                    = [i.get('sdc_lower1')                    for i in data]
        self.linreg_slope                  = [i.get('linreg_slope')                  for i in data]
        self.linreg_intercept              = [i.get('linreg_intercept')              for i in data]
        self.linreg_std                    = [i.get('linreg_std')                    for i in data]
        self.sdc_upper                     = [i.get('sdc_upper')                     for i in data]
        self.sdc_lower                     = [i.get('sdc_lower')                     for i in data]
        self.sym                           = [i.get('sym')                           for i in data]
        self.td                            = [i.get('td')                            for i in data]
        self.macd                          = [i.get('macd')                          for i in data]
        self.expiry                        = [i.get('expiry')                        for i in data]
        self.strike                        = [i.get('strike')                        for i in data]
        self.call_put                      = [i.get('call_put')                      for i in data]
        self.mid                           = [i.get('mid')                           for i in data]
        self.symbol                        = [i.get('symbol')                        for i in data]
        self.rsi_35                        = [i.get('rsi_35')                        for i in data]

        self.data_dict = {
            'ts': self.ts,
            'o': self.o,
            'c': self.c,
            'h': self.h,
            'l': self.l,
            'v': self.v,
            'vwap': self.vwap,
            'roll_mean_sdc': self.roll_mean_sdc,
            'roll_std_sdc': self.roll_std_sdc,
            'sdc_upper1': self.sdc_upper1,
            'sdc_signal': self.sdc_signal,
            'rsi': self.rsi,
            'middle_band': self.middle_band,
            'upper_band': self.upper_band,
            'lower_band': self.lower_band,
            'upper_bb_trend': self.upper_bb_trend,
            'lower_bb_trend': self.lower_bb_trend,
            'upper_bb_angle': self.upper_bb_angle,
            'middle_bb_angle': self.middle_bb_angle,
            'lower_bb_angle': self.lower_bb_angle,
            'upper_bb_rel_angle': self.upper_bb_rel_angle,
            'middle_bb_rel_angle': self.middle_bb_rel_angle,
            'lower_bb_rel_angle': self.lower_bb_rel_angle,
            'candle_above_upper': self.candle_above_upper,
            'candle_below_lower': self.candle_below_lower,
            'candle_completely_above_upper': self.candle_completely_above_upper,
            'candle_partially_above_upper': self.candle_partially_above_upper,
            'candle_completely_below_lower': self.candle_completely_below_lower,
            'candle_partially_below_lower': self.candle_partially_below_lower,
            'td_buy_count': self.td_buy_count,
            'td_sell_count': self.td_sell_count,
            'macd_curvature': self.macd_curvature,
            'timespan': self.timespan,
            'ticker': self.ticker,
            'insertion_timestamp': self.insertion_timestamp,
            'sdc_base': self.sdc_base,
            'sdc_lower1': self.sdc_lower1,
            'linreg_slope': self.linreg_slope,
            'linreg_intercept': self.linreg_intercept,
            'linreg_std': self.linreg_std,
            'sdc_upper': self.sdc_upper,
            'sdc_lower': self.sdc_lower,
            'sym': self.sym,
            'td': self.td,
            'macd': self.macd,
            'expiry': self.expiry,
            'strike': self.strike,
            'call_put': self.call_put,
            'mid': self.mid,
            'symbol': self.symbol,
            'rsi_35': self.rsi_35
        }
        self.as_dataframe = pd.DataFrame(self.data_dict)


class AnalystsTable:
    """
    Represents analyst ratings distribution for a given stock ticker.

    This table captures the sentiment breakdown from analysts,
    allowing users to quickly gauge the market consensus (buy/sell/hold).

    Attributes:
        strong_buy (list): Count of analysts who rated the ticker as a 'Strong Buy'.
        buy (list): Count of analysts who rated it as a 'Buy'.
        hold (list): Count of analysts recommending to hold the position.
        underperform (list): Count of analysts expecting the ticker to underperform.
        sell (list): Count of analysts who rated the ticker as a 'Sell'.
        ticker (list): The ticker symbol being analyzed.
        insertion_timestamp (list): Timestamp when the record was inserted into the database.
    """
    def __init__(self, data):

        self.strong_buy          = [i.get('strong_buy') for i in data]
        self.buy                 = [i.get('buy') for i in data]
        self.hold                = [i.get('hold') for i in data]
        self.underperform        = [i.get('underperform') for i in data]
        self.sell                = [i.get('sell') for i in data]
        self.ticker              = [i.get('ticker') for i in data]
        self.insertion_timestamp = [i.get('insertion_timestamp') for i in data]
        self.data_dict = {
            'strong_buy': self.strong_buy,
            'buy': self.buy,
            'hold': self.hold,
            'underperform': self.underperform,
            'sell': self.sell,
            'ticker': self.ticker,
            'insertion_timestamp': self.insertion_timestamp
        }


        self.as_dataframe = pd.DataFrame(self.data_dict)

class VolAnalTable:
    """
    Represents volume analysis by sentiment for a specific ticker at a given time.

    This table allows sentiment-based breakdowns of volume and trade counts.

    Attributes:
        ticker (list): The ticker symbol being analyzed.
        avg_price (list): Average trade price across all trades.
        total_num (list): Total number of trades.
        total_volume (list): Total volume traded.
        buy_volume (list): Volume classified as buyer-initiated.
        sell_volume (list): Volume classified as seller-initiated.
        neut_volume (list): Volume considered neutral or indeterminate.
        buy_pct (list): Percentage of buy volume out of total.
        sell_pct (list): Percentage of sell volume out of total.
        neut_pct (list): Percentage of neutral volume out of total.
        insertion_timestamp (list): Timestamp of when the data was captured and logged.
    """
    def __init__(self, data):
        self.ticker              = [i.get('ticker')              for i in data]
        self.avg_price           = [i.get('avg_price')           for i in data]
        self.total_num           = [i.get('total_num')           for i in data]
        self.total_volume        = [i.get('total_volume')        for i in data]
        self.buy_volume          = [i.get('buy_volume')          for i in data]
        self.sell_volume         = [i.get('sell_volume')         for i in data]
        self.neut_volume         = [i.get('neut_volume')         for i in data]
        self.buy_pct             = [i.get('buy_pct')             for i in data]
        self.sell_pct            = [i.get('sell_pct')            for i in data]
        self.neut_pct            = [i.get('neut_pct')            for i in data]
        self.insertion_timestamp = [i.get('insertion_timestamp') for i in data]

        self.data_dict = {
            'ticker': self.ticker,
            'avg_price': self.avg_price,
            'total_num': self.total_num,
            'total_volume': self.total_volume,
            'buy_volume': self.buy_volume,
            'sell_volume': self.sell_volume,
            'neut_volume': self.neut_volume,
            'buy_pct': self.buy_pct,
            'sell_pct': self.sell_pct,
            'neut_pct': self.neut_pct,
            'insertion_timestamp': self.insertion_timestamp
        }

        self.as_dataframe = pd.DataFrame(self.data_dict)
class YfEarningsEstimateTable:
    """
    Represents forward-looking earnings per share (EPS) estimates by analysts.

    This table is useful for evaluating expectations for future growth and market pricing.

    Attributes:
        period (list): Time period for the estimate (e.g., Q2 2025, FY2024).
        avg (list): Average EPS estimate across all analysts.
        low (list): Lowest EPS estimate among analysts.
        high (list): Highest EPS estimate among analysts.
        yearAgoEps (list): Reported EPS for the same period last year.
        numberOfAnalysts (list): Number of analysts contributing to the estimate.
        growth (list): Expected percentage growth compared to the year-ago EPS.
        ticker (list): Ticker symbol of the company being analyzed.
        insertion_timestamp (list): Timestamp of when the data was inserted.
    """
    def __init__(self, data):
        self.period              = [i.get('period')              for i in data]
        self.avg                 = [i.get('avg')                 for i in data]
        self.low                 = [i.get('low')                 for i in data]
        self.high                = [i.get('high')                for i in data]
        self.yearAgoEps          = [i.get('yearAgoEps')          for i in data]
        self.numberOfAnalysts    = [i.get('numberOfAnalysts')    for i in data]
        self.growth              = [i.get('growth')              for i in data]
        self.ticker              = [i.get('ticker')              for i in data]
        self.insertion_timestamp = [i.get('insertion_timestamp') for i in data]

        self.data_dict = {
            'period': self.period,
            'avg': self.avg,
            'low': self.low,
            'high': self.high,
            'yearAgoEps': self.yearAgoEps,
            'numberOfAnalysts': self.numberOfAnalysts,
            'growth': self.growth,
            'ticker': self.ticker,
            'insertion_timestamp': self.insertion_timestamp
        }
        self.as_dataframe = pd.DataFrame(self.data_dict)

class EarningsSoonTable:
    """
    Represents upcoming earnings events, including expected release times and analyst estimates.

    This table is useful for preparing ahead of earnings reports and understanding potential market catalysts.

    Attributes:
        ticker (list): Ticker symbol of the company.
        name (list): Company name.
        price (list): Last known trading price before earnings.
        volume (list): Trading volume.
        change_ratio (list): Price change ratio before earnings.
        start_time (list): Scheduled earnings release start time.
        end_time (list): Scheduled earnings release end time.
        year (list): Fiscal year of the upcoming earnings.
        quarter (list): Fiscal quarter of the upcoming earnings.
        last_release (list): Timestamp of the last earnings release.
        eps_last (list): Reported EPS from the last earnings.
        eps_estimate (list): Current EPS estimate for this quarter.
        eps_estimate_date (list): Date of the most recent EPS estimate.
        revenue_estimate (list): Current revenue estimate for this quarter.
        revenue_last (list): Reported revenue from last earnings.
        insertion_timestamp (list): Time this record was inserted into the database.
    """
    def __init__(self, data):
        self.ticker              = [i.get('ticker')              for i in data]
        self.name                = [i.get('name')                for i in data]
        self.price               = [i.get('price')               for i in data]
        self.volume              = [i.get('volume')              for i in data]
        self.change_ratio        = [i.get('change_ratio')        for i in data]
        self.start_time          = [i.get('start_time')          for i in data]
        self.end_time            = [i.get('end_time')            for i in data]
        self.year                = [i.get('year')                for i in data]
        self.quarter             = [i.get('quarter')             for i in data]
        self.last_release        = [i.get('last_release')        for i in data]
        self.eps_last            = [i.get('eps_last')            for i in data]
        self.eps_estimate        = [i.get('eps_estimate')        for i in data]
        self.eps_estimate_date   = [i.get('eps_estimate_date')   for i in data]
        self.revenue_estimate    = [i.get('revenue_estimate')    for i in data]
        self.revenue_last        = [i.get('revenue_last')        for i in data]
        self.insertion_timestamp = [i.get('insertion_timestamp') for i in data]

        self.data_dict = {
            'ticker': self.ticker,
            'name': self.name,
            'price': self.price,
            'volume': self.volume,
            'change_ratio': self.change_ratio,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'year': self.year,
            'quarter': self.quarter,
            'last_release': self.last_release,
            'eps_last': self.eps_last,
            'eps_estimate': self.eps_estimate,
            'eps_estimate_date': self.eps_estimate_date,
            'revenue_estimate': self.revenue_estimate,
            'revenue_last': self.revenue_last,
            'insertion_timestamp': self.insertion_timestamp
        }

        self.as_dataframe = pd.DataFrame(self.data_dict)

        
class YfInsiderRosterHoldingsTable:
    """
    Represents insider holdings and transactions for executives and major stakeholders from Yahoo Finance data.

    This table aggregates direct and indirect ownership along with recent transaction activity.

    Attributes:
        name (list): Insider's full name (e.g., CEO, CFO, board member).
        position (list): Role or title within the company.
        url (list): Direct URL to the insider's Yahoo Finance profile.
        most_recent_transaction (list): Description of the latest trade (e.g., 'Buy', 'Sell', 'Award').
        latest_transaction_date (list): Date of the most recent transaction.
        shares_owned_directly (list): Number of shares held directly by the insider.
        position_direct_date (list): Date on which direct ownership position was last updated.
        ticker (list): Ticker symbol of the company.
        insertion_timestamp (list): When this row was added to the database.
        shares_owned_indirectly (list): Number of shares held indirectly (e.g., via trusts or spouse).
        position_indirect_date (list): Date on which indirect ownership was last updated.
        positionsummary (list): Overall ownership summary (combination of direct/indirect holdings).
        positionsummarydate (list): Date corresponding to the position summary.
    """

    def __init__(self, data):
        self.name                    = [i.get('name')                    for i in data]
        self.position                = [i.get('position')                for i in data]
        self.url                     = [i.get('url')                     for i in data]
        self.most_recent_transaction = [i.get('most_recent_transaction') for i in data]
        self.latest_transaction_date = [i.get('latest_transaction_date') for i in data]
        self.shares_owned_directly   = [i.get('shares_owned_directly')   for i in data]
        self.position_direct_date    = [i.get('position_direct_date')    for i in data]
        self.ticker                  = [i.get('ticker')                  for i in data]
        self.insertion_timestamp     = [i.get('insertion_timestamp')     for i in data]
        self.shares_owned_indirectly = [i.get('shares_owned_indirectly') for i in data]
        self.position_indirect_date  = [i.get('position_indirect_date')  for i in data]
        self.positionsummary         = [i.get('positionsummary')         for i in data]
        self.positionsummarydate     = [i.get('positionsummarydate')     for i in data]
        self.data_dict = {
            'name': self.name,
            'position': self.position,
            'url': self.url,
            'most_recent_transaction': self.most_recent_transaction,
            'latest_transaction_date': self.latest_transaction_date,
            'shares_owned_directly': self.shares_owned_directly,
            'position_direct_date': self.position_direct_date,
            'ticker': self.ticker,
            'insertion_timestamp': self.insertion_timestamp,
            'shares_owned_indirectly': self.shares_owned_indirectly,
            'position_indirect_date': self.position_indirect_date,
            'positionsummary': self.positionsummary,
            'positionsummarydate': self.positionsummarydate
        }
        self.as_dataframe = pd.DataFrame(self.data_dict)




class YfPtTable:
    """
    Contains analyst price target statistics for a given stock, sourced from Yahoo Finance.

    This data reflects current market sentiment among analysts and institutions.

    Attributes:
        current (list): The current average price target.
        high (list): The highest price target among analysts.
        low (list): The lowest price target among analysts.
        average (list): Mean of all price targets.
        median (list): Median of the reported price targets.
        ticker (list): Ticker symbol of the stock.
        insertion_timestamp (list): When this record was stored.
    """

    def __init__(self, data):
        self.current             = [i.get('current')             for i in data]
        self.high                = [i.get('high')                for i in data]
        self.low                 = [i.get('low')                 for i in data]
        self.average             = [i.get('average')             for i in data]
        self.median              = [i.get('median')              for i in data]
        self.ticker              = [i.get('ticker')              for i in data]
        self.insertion_timestamp = [i.get('insertion_timestamp') for i in data]

        self.data_dict = { 
            'current': self.current,
            'high': self.high,
            'low': self.low,
            'average': self.average,
            'median': self.median,
            'ticker': self.ticker
        }
        self.as_dataframe = pd.DataFrame(self.data_dict)

class YfNewsTable:
    """
    Stores news articles and financial updates related to a stock from Yahoo Finance's RSS or content feed.

    Each entry corresponds to a news headline with metadata like provider and publication date.

    Attributes:
        id (list): Unique ID for the news item.
        content_type (list): Type of content (e.g., 'news', 'video', 'article').
        title (list): Headline or title of the news piece.
        description (list): Brief teaser or sub-headline.
        summary (list): Condensed content summary.
        pub_date (list): Date and time the article was published.
        thumbnail (list): Link to the thumbnail image (if available).
        provider (list): News provider (e.g., Bloomberg, Reuters, Yahoo Finance).
        url (list): Direct link to the full article.
        ticker (list): Associated stock ticker symbol.
        insertion_timestamp (list): When this article was added to the database.
    """

    def __init__(self, data):
        self.id                  = [i.get('id')                  for i in data]
        self.content_type        = [i.get('content_type')        for i in data]
        self.title               = [i.get('title')               for i in data]
        self.description         = [i.get('description')         for i in data]
        self.summary             = [i.get('summary')             for i in data]
        self.pub_date            = [i.get('pub_date')            for i in data]
        self.thumbnail           = [i.get('thumbnail')           for i in data]
        self.provider            = [i.get('provider')            for i in data]
        self.url                 = [i.get('url')                 for i in data]
        self.ticker              = [i.get('ticker')              for i in data]
        self.insertion_timestamp = [i.get('insertion_timestamp') for i in data]

        self.data_dict = {
            'id': self.id,
            'content_type': self.content_type,
            'title': self.title,
            'description': self.description,
            'summary': self.summary,
            'pub_date': self.pub_date,
            'thumbnail': self.thumbnail,
            'provider': self.provider,
            'url': self.url,
            'ticker': self.ticker,
            'insertion_timestamp': self.insertion_timestamp
        }

        self.as_dataframe = pd.DataFrame(self.data_dict)
class BuySurgeTable:
    """
    Represents a filtered snapshot of options contracts experiencing a **surge in buy-side volume**.

    This table highlights contracts with elevated buyer activity relative to sells and neutral trades, often used to detect momentum positioning or unusual interest.

    Attributes:
        ticker (list): Ticker symbol of the underlying stock.
        strike (list): Strike price of the option contract.
        call_put (list): Option type — 'call' or 'put'.
        expiry (list): Expiration date of the contract.
        volume (list): Total volume traded during the observed window.
        buy_volume (list): Volume identified as buyer-initiated.
        sell_volume (list): Volume identified as seller-initiated.
        neutral_volume (list): Volume classified as neutral (e.g., mid-market).
        total_trades (list): Number of individual trades included.
        avg_price (list): Average execution price of all trades.
        ask (list): Current ask price.
        bid (list): Current bid price.
        insertion_timestamp (list): When this row was inserted into the table.

    Use Cases:
        - Detecting aggressive buying pressure
        - Surfacing bullish option flow
        - Building trade alerts around buy-dominant contracts
    """

    def __init__(self, data):
        self.ticker              = [i.get('ticker')              for i in data]
        self.strike              = [i.get('strike')              for i in data]
        self.call_put            = [i.get('call_put')            for i in data]
        self.expiry              = [i.get('expiry')              for i in data]
        self.volume              = [i.get('volume')              for i in data]
        self.buy_volume          = [i.get('buy_volume')          for i in data]
        self.sell_volume         = [i.get('sell_volume')         for i in data]
        self.neutral_volume      = [i.get('neutral_volume')      for i in data]
        self.total_trades        = [i.get('total_trades')        for i in data]
        self.avg_price           = [i.get('avg_price')           for i in data]
        self.ask                 = [i.get('ask')                 for i in data]
        self.bid                 = [i.get('bid')                 for i in data]
        self.insertion_timestamp = [i.get('insertion_timestamp') for i in data]




class VolumeSurgeTable:
    """
    Contains detailed data on **options contracts experiencing a volume surge**, including price action, Greeks, and trade statistics.

    Designed for detecting unusual volume spikes across calls and puts, along with directional sentiment and implied volatility.

    Attributes:
        option_symbol (list): Full option symbol (e.g., TSLA_081624C300).
        option_id (list): Internal or vendor-specific option contract ID.
        ticker_id (list): Internal ID for the underlying ticker.
        ticker (list): Ticker symbol of the underlying stock.
        strike (list): Option strike price.
        call_put (list): Option type — 'call' or 'put'.
        expiry (list): Option expiration date.
        open (list): Opening price of the option for the session.
        high (list): Highest trade price during the session.
        low (list): Lowest trade price during the session.
        close (list): Most recent trade price or session close.
        volume (list): Total volume traded for the contract.
        ask_volume (list): Volume traded at or near ask price (buy pressure).
        bid_volume (list): Volume traded at or near bid price (sell pressure).
        ask_price (list): Current best ask price.
        bid_price (list): Current best bid price.
        oi (list): Open interest (contracts outstanding).
        oi_change (list): Change in open interest since last report.
        trade_time (list): Timestamp of last trade.
        trade_stamp (list): Numerical or formatted trade time.
        delta (list): Option delta (price sensitivity to underlying).
        gamma (list): Option gamma (delta sensitivity).
        theta (list): Time decay value.
        vega (list): Sensitivity to implied volatility.
        rho (list): Interest rate sensitivity.
        iv (list): Implied volatility.
        activity (list): Labeled activity tag (e.g., 'sweep', 'block', or 'unusual').
        latest_volume (list): Volume detected in the latest scan window.
        change (list): Net price change for the day.
        change_pct (list): Percentage price change for the day.
        insertion_timestamp (list): When this row was recorded.

    Use Cases:
        - Identifying unusual option flow
        - Detecting real-time spikes in trade volume
        - Building scanners based on volume+IV or Greek patterns
        - Analyzing retail vs institutional positioning
    """

    def __init__(self, data):
        self.option_symbol       = [i.get('option_symbol')       for i in data]
        self.option_id           = [i.get('option_id')           for i in data]
        self.ticker_id           = [i.get('ticker_id')           for i in data]
        self.ticker              = [i.get('ticker')              for i in data]
        self.strike              = [i.get('strike')              for i in data]
        self.call_put            = [i.get('call_put')            for i in data]
        self.expiry              = [i.get('expiry')              for i in data]
        self.open                = [i.get('open')                for i in data]
        self.high                = [i.get('high')                for i in data]
        self.low                 = [i.get('low')                 for i in data]
        self.close               = [i.get('close')               for i in data]
        self.volume              = [i.get('volume')              for i in data]
        self.ask_volume          = [i.get('ask_volume')          for i in data]
        self.bid_volume          = [i.get('bid_volume')          for i in data]
        self.ask_price           = [i.get('ask_price')           for i in data]
        self.bid_price           = [i.get('bid_price')           for i in data]
        self.oi                  = [i.get('oi')                  for i in data]
        self.oi_change           = [i.get('oi_change')           for i in data]
        self.trade_time          = [i.get('trade_time')          for i in data]
        self.trade_stamp         = [i.get('trade_stamp')         for i in data]
        self.delta               = [i.get('delta')               for i in data]
        self.gamma               = [i.get('gamma')               for i in data]
        self.theta               = [i.get('theta')               for i in data]
        self.vega                = [i.get('vega')                for i in data]
        self.rho                 = [i.get('rho')                 for i in data]
        self.iv                  = [i.get('iv')                  for i in data]
        self.activity            = [i.get('activity')            for i in data]
        self.latest_volume       = [i.get('latest_volume')       for i in data]
        self.change              = [i.get('change')              for i in data]
        self.change_pct          = [i.get('change_pct')          for i in data]
        self.insertion_timestamp = [i.get('insertion_timestamp') for i in data]


        self.data_dict = {
            'option_symbol': self.option_symbol,
            'option_id': self.option_id,
            'ticker_id': self.ticker_id,
            'ticker': self.ticker,
            'strike': self.strike,
            'call_put': self.call_put,
            'expiry': self.expiry,
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'volume': self.volume,
            'ask_volume': self.ask_volume,
            'bid_volume': self.bid_volume,
            'ask_price': self.ask_price,
            'bid_price': self.bid_price,
            'oi': self.oi,
            'oi_change': self.oi_change,
            'trade_time': self.trade_time,
            'trade_stamp': self.trade_stamp,
            'delta': self.delta,
            'gamma': self.gamma,
            'theta': self.theta,
            'vega': self.vega,
            'rho': self.rho,
            'iv': self.iv,
            'activity': self.activity,
            'latest_volume': self.latest_volume,
            'change': self.change,
            'change_pct': self.change_pct,
            'insertion_timestamp': self.insertion_timestamp
        }
        self.as_dataframe = pd.DataFrame(self.data_dict)

class ShortInterestTable:
    """
    Represents historical short interest data for a given stock ticker.

    Each row corresponds to a FINRA/NYSE-reported short interest snapshot on a specific settlement date.

    Attributes:
        settlement_date (list): The official date on which short interest was recorded (typically biweekly).
        short_interest (list): Total number of shares currently sold short but not yet covered.
        average_volume (list): Average daily volume used to calculate days to cover.
        days_to_cover (list): Number of days it would take to cover all shorts at the average daily volume.
        ticker (list): The stock symbol.
        outstanding_shares (list): Total shares outstanding as of that date.
        pct_float_shorted (list): Percentage of the float (tradable shares) currently sold short.
        insertion_timestamp (list): The timestamp when this row was inserted into the database.
    """

    def __init__(self, data):
        self.settlement_date     = [i.get('settlement_date')     for i in data]
        self.short_interest      = [i.get('short_interest')      for i in data]
        self.average_volume      = [i.get('average_volume')      for i in data]
        self.days_to_cover       = [i.get('days_to_cover')       for i in data]
        self.ticker              = [i.get('ticker')              for i in data]
        self.outstanding_shares  = [i.get('outstanding_shares')  for i in data]
        self.pct_float_shorted   = [i.get('pct_float_shorted')   for i in data]
        self.insertion_timestamp = [i.get('insertion_timestamp') for i in data]
        self.data_dict = {
            'settlement_date': self.settlement_date,
            'short_interest': self.short_interest,
            'average_volume': self.average_volume,
            'days_to_cover': self.days_to_cover,
            'ticker': self.ticker,
            'outstanding_shares': self.outstanding_shares,
            'pct_float_shorted': self.pct_float_shorted,
            'insertion_timestamp': self.insertion_timestamp
        }
        self.as_dataframe = pd.DataFrame(self.data_dict)

class YfMfHoldersTable:
    """
    Represents mutual fund and institutional ownership data for a given stock (ticker),
    typically sourced from Yahoo Finance's reported institutional filings.

    Tracks changes in fund shareholding, ownership percentage, and value over time.

    Attributes:
        date_reported (list): Date when the mutual fund holding was last reported.
        holder (list): Name of the mutual fund or institutional holder.
        pctheld (list): Percentage of the total outstanding shares held by the fund.
        shares (list): Total number of shares held by the fund.
        value (list): Market value of the fund's holdings in the stock (usually in USD).
        pctchange (list): Percentage change in the number of shares held since the last report.
        ticker (list): Ticker symbol of the underlying security (e.g., 'AAPL').
        insertion_timestamp (list): Timestamp when the data was inserted into the database.
    """

    def __init__(self, data):
        self.date_reported       = [i.get('date_reported')       for i in data]
        self.holder              = [i.get('holder')              for i in data]
        self.pctheld             = [i.get('pctheld')             for i in data]
        self.shares              = [i.get('shares')              for i in data]
        self.value               = [i.get('value')               for i in data]
        self.pctchange           = [i.get('pctchange')           for i in data]
        self.ticker              = [i.get('ticker')              for i in data]
        self.insertion_timestamp = [i.get('insertion_timestamp') for i in data]
        self.data_dict = {
            'date_reported': self.date_reported,
            'holder': self.holder,
            'pctheld': self.pctheld,
            'shares': self.shares,
            'value': self.value,
            'pctchange': self.pctchange,
            'ticker': self.ticker,
            'insertion_timestamp': self.insertion_timestamp
        }
        self.as_dataframe = pd.DataFrame(self.data_dict)
        
class CostDistributionTable:
    """
    Tracks cost basis distribution data for a given stock ticker on a specific date.

    Typically used to visualize the average price levels at which holders are profitable or underwater.

    Attributes:
        ticker (list): The stock symbol.
        date (list): The snapshot date of the cost basis distribution.
        price (list): The specific price bucket or level being measured.
        cost_sentiment (list): The percentage of holders who are in profit at this price level.
        average_cost (list): The weighted average cost basis across all holders as of that date.
        insertion_timestamp (list): The timestamp when this row was inserted into the database.
    """

    def __init__(self, data):
        self.ticker              = [i.get('ticker')              for i in data]
        self.date                = [i.get('date')                for i in data]
        self.price               = [i.get('price')               for i in data]
        self.profit_ratio        = [i.get('cost_sentiment')        for i in data]
        self.average_cost        = [i.get('average_cost')        for i in data]
        self.insertion_timestamp = [i.get('insertion_timestamp') for i in data]

        self.data_dict = {
            'ticker': self.ticker,
            'date': self.date,
            'price': self.price,
            'profit_ratio': self.profit_ratio,
            'average_cost': self.average_cost,
            'insertion_timestamp': self.insertion_timestamp
        }

        self.as_dataframe = pd.DataFrame(self.data_dict)
class RiseFallTables:
    """
    Represents ranked stock movements for biggest risers and fallers.

    This table captures detailed change metrics and valuation signals for stocks rising or falling
    in price, helping traders identify breakout momentum or panic selloffs.

    Attributes:
        ticker_id (list): Internal ticker ID reference.
        name (list): Company name.
        symbol (list): Stock ticker symbol (e.g., 'NVDA').
        trade_time (list): Timestamp of the most recent trade.
        close (list): Last closing price.
        change (list): Absolute price change from prior close.
        change_pct (list): Percent change from prior close.
        last_price (list): Most recently traded price.
        price (list): Synonym for `last_price`.
        last_change (list): Net change vs. previous price.
        last_change_pct (list): Percent change vs. previous price.
        market_value (list): Estimated market cap.
        volume (list): Trading volume today.
        turnover_rate (list): Percentage of float traded today.
        high (list): Daily high.
        low (list): Daily low.
        vibration (list): Volatility or price "vibration" rating.
        peTtm (list): Trailing 12-month price/earnings ratio.
        quant_rating (list): AI-generated quantitative score.
        debt_assets_ratio (list): Financial leverage ratio.
        rise_or_fall (list): Flag - 'rise' or 'fall'.
        rank_type (list): Type of rank used ('percentage', 'absolute', etc.).
        insertion_timestamp (list): Timestamp when the row was inserted.
    """

    def __init__(self, data):
        self.ticker_id           = [i.get('ticker_id')           for i in data]
        self.name                = [i.get('name')                for i in data]
        self.symbol              = [i.get('symbol')              for i in data]
        self.trade_time          = [i.get('trade_time')          for i in data]
        self.close               = [i.get('close')               for i in data]
        self.change              = [i.get('change')              for i in data]
        self.change_pct          = [i.get('change_pct')          for i in data]
        self.last_price          = [i.get('last_price')          for i in data]
        self.price               = [i.get('price')               for i in data]
        self.last_change         = [i.get('last_change')         for i in data]
        self.last_change_pct     = [i.get('last_change_pct')     for i in data]
        self.market_value        = [i.get('market_value')        for i in data]
        self.volume              = [i.get('volume')              for i in data]
        self.turnover_rate       = [i.get('turnover_rate')       for i in data]
        self.high                = [i.get('high')                for i in data]
        self.low                 = [i.get('low')                 for i in data]
        self.vibration           = [i.get('vibration')           for i in data]
        self.peTtm               = [i.get('peTtm')               for i in data]
        self.quant_rating        = [i.get('quant_rating')        for i in data]
        self.debt_assets_ratio   = [i.get('debt_assets_ratio')   for i in data]
        self.rise_or_fall        = [i.get('rise_or_fall')        for i in data]
        self.rank_type           = [i.get('rank_type')           for i in data]
        self.insertion_timestamp = [i.get('insertion_timestamp') for i in data]
        self.data_dict = {
            'ticker_id': self.ticker_id,
            'name': self.name,
            'symbol': self.symbol,
            'trade_time': self.trade_time,
            'close': self.close,
            'change': self.change,
            'change_pct': self.change_pct,
            'last_price': self.last_price,
            'price': self.price,
            'last_change': self.last_change,
            'last_change_pct': self.last_change_pct,
            'market_value': self.market_value,
            'volume': self.volume,
            'turnover_rate': self.turnover_rate,
            'high': self.high,
            'low': self.low,
            'vibration': self.vibration,
            'peTtm': self.peTtm,
            'quant_rating': self.quant_rating,
            'debt_assets_ratio': self.debt_assets_ratio,
            'rise_or_fall': self.rise_or_fall,
            'rank_type': self.rank_type,
            'insertion_timestamp': self.insertion_timestamp
        }
        self.as_dataframe = pd.DataFrame(self.data_dict)

class HighDividendsTable:
    """
    Represents top dividend-paying stocks ranked by yield and dividend metrics.

    This dataset focuses on income-generating equities and dividend-focused screening.

    Attributes:
        ticker_id (list): Internal ID for the stock.
        name (list): Full company name.
        ticker (list): Stock ticker symbol (e.g., 'T', 'KO').
        trade_time (list): Last trade timestamp.
        open (list): Opening price.
        high (list): High of the day.
        low (list): Low of the day.
        close (list): Most recent close price.
        change (list): Net change in price.
        change_pct (list): Percent price change.
        market_value (list): Company market cap.
        volume (list): Total traded shares today.
        turnover_rate (list): Share turnover vs. float.
        pe_ttm (list): Price-to-earnings ratio, trailing 12 months.
        dividend_x (list): Reported dividend amount.
        fifty_high (list): 52-week high.
        fifty_low (list): 52-week low.
        vibration (list): Volatility metric.
        yield_ (list): Dividend yield (renamed from `yield` due to keyword conflict).
        dividend_y (list): Adjusted dividend metric.
        ex_date (list): Last ex-dividend date.
        insertion_timestamp (list): When this data was logged.
    """

    def __init__(self, data):
        self.ticker_id           = [i.get('ticker_id')           for i in data]
        self.name                = [i.get('name')                for i in data]
        self.ticker              = [i.get('ticker')              for i in data]
        self.trade_time          = [i.get('trade_time')          for i in data]
        self.open                = [i.get('open')                for i in data]
        self.high                = [i.get('high')                for i in data]
        self.low                 = [i.get('low')                 for i in data]
        self.close               = [i.get('close')               for i in data]
        self.change              = [i.get('change')              for i in data]
        self.change_pct          = [i.get('change_pct')          for i in data]
        self.market_value        = [i.get('market_value')        for i in data]
        self.volume              = [i.get('volume')              for i in data]
        self.turnover_rate       = [i.get('turnover_rate')       for i in data]
        self.pe_ttm              = [i.get('pe_ttm')              for i in data]
        self.dividend_x          = [i.get('dividend_x')          for i in data]
        self.fifty_high          = [i.get('fifty_high')          for i in data]
        self.fifty_low           = [i.get('fifty_low')           for i in data]
        self.vibration           = [i.get('vibration')           for i in data]
        self.yield_              = [i.get('yield')               for i in data]
        self.dividend_y          = [i.get('dividend_y')          for i in data]
        self.ex_date             = [i.get('ex_date')             for i in data]
        self.insertion_timestamp = [i.get('insertion_timestamp') for i in data]
        self.data_dict = {
            'ticker_id': self.ticker_id,
            'name': self.name,
            'ticker': self.ticker,
            'trade_time': self.trade_time,
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'change': self.change,
            'change_pct': self.change_pct,
            'market_value': self.market_value,
            'volume': self.volume,
            'turnover_rate': self.turnover_rate,
            'pe_ttm': self.pe_ttm,
            'dividend_x': self.dividend_x,
            'fifty_high': self.fifty_high,
            'fifty_low': self.fifty_low,
            'vibration': self.vibration,
            'yield': self.yield_,
            'dividend_y': self.dividend_y,
            'ex_date': self.ex_date,
            'insertion_timestamp': self.insertion_timestamp
        }

        self.as_dataframe = pd.DataFrame(self.data_dict)

class MultiQuoteTable:
    """
    Core stock quote metadata from Webull or other APIs. Includes valuation, pricing, technicals, and financials.

    Used to quickly snapshot full market view across multiple tickers.

    Attributes:
        ticker_id (list): Internal ID for the ticker.
        name (list): Company name.
        ticker (list): Ticker symbol.
        mk_trade_time (list): Last recorded market trade timestamp.
        close (list): Latest close price.
        change (list): Net price change.
        change_ratio (list): Price percent change.
        market_value (list): Market capitalization.
        volume (list): Total traded shares.
        turnover_rate (list): Float turnover rate.
        overnight (list): Overnight % change.
        pre_close (list): Previous day's close price.
        open (list): Opening price of the day.
        high (list): Daily high.
        low (list): Daily low.
        vibrate_ratio (list): Volatility score.
        avg_vol_10d (list): 10-day average volume.
        avg_vol_3m (list): 3-month average volume.
        neg_market_value (list): Negative market cap entries (if any).
        pe (list): Price-to-earnings ratio.
        forward_pe (list): Projected PE ratio.
        indicated_pe (list): Implied PE ratio.
        pe_ttm (list): Trailing PE ratio.
        eps (list): Earnings per share (latest).
        eps_ttm (list): Earnings per share TTM.
        pb (list): Price/book ratio.
        total_shares (list): Total outstanding shares.
        outstanding_shares (list): Actively floating shares.
        fifty_high (list): 52-week high price.
        fifty_low (list): 52-week low price.
        dividend (list): Dividend amount (most recent).
        yield_ (list): Dividend yield (renamed from `yield`).
        latest_dividend_date (list): Date of most recent dividend.
        latest_split_date (list): Date of most recent stock split.
        latest_earnings_date (list): Last reported earnings date.
        ps (list): Price/sales ratio.
        bps (list): Book value per share.
        estimate_earnings_date (list): Estimated next earnings date.
        next_earning_day (list): Projected earnings calendar entry.
        insertion_timestamp (list): Timestamp of data capture.
        sector (list): Industry sector classification.
    """

    def __init__(self, data):
        self.ticker_id              = [i.get('ticker_id')              for i in data]
        self.name                   = [i.get('name')                   for i in data]
        self.ticker                 = [i.get('ticker')                 for i in data]
        self.mk_trade_time          = [i.get('mk_trade_time')          for i in data]
        self.close                  = [i.get('close')                  for i in data]
        self.change                 = [i.get('change')                 for i in data]
        self.change_ratio           = [i.get('change_ratio')           for i in data]
        self.market_value           = [i.get('market_value')           for i in data]
        self.volume                 = [i.get('volume')                 for i in data]
        self.turnover_rate          = [i.get('turnover_rate')          for i in data]
        self.overnight              = [i.get('overnight')              for i in data]
        self.pre_close              = [i.get('pre_close')              for i in data]
        self.open                   = [i.get('open')                   for i in data]
        self.high                   = [i.get('high')                   for i in data]
        self.low                    = [i.get('low')                    for i in data]
        self.vibrate_ratio          = [i.get('vibrate_ratio')          for i in data]
        self.avg_vol_10d            = [i.get('avg_vol_10d')            for i in data]
        self.avg_vol_3m             = [i.get('avg_vol_3m')             for i in data]
        self.neg_market_value       = [i.get('neg_market_value')       for i in data]
        self.pe                     = [i.get('pe')                     for i in data]
        self.forward_pe             = [i.get('forward_pe')             for i in data]
        self.indicated_pe           = [i.get('indicated_pe')           for i in data]
        self.pe_ttm                 = [i.get('pe_ttm')                 for i in data]
        self.eps                    = [i.get('eps')                    for i in data]
        self.eps_ttm                = [i.get('eps_ttm')                for i in data]
        self.pb                     = [i.get('pb')                     for i in data]
        self.total_shares           = [i.get('total_shares')           for i in data]
        self.outstanding_shares     = [i.get('outstanding_shares')     for i in data]
        self.fifty_high             = [i.get('fifty_high')             for i in data]
        self.fifty_low              = [i.get('fifty_low')              for i in data]
        self.dividend               = [i.get('dividend')               for i in data]
        self.yield_                 = [i.get('yield')                  for i in data]  # 'yield' is a keyword
        self.latest_dividend_date   = [i.get('latest_dividend_date')   for i in data]
        self.latest_split_date      = [i.get('latest_split_date')      for i in data]
        self.latest_earnings_date   = [i.get('latest_earnings_date')   for i in data]
        self.ps                     = [i.get('ps')                     for i in data]
        self.bps                    = [i.get('bps')                    for i in data]
        self.estimate_earnings_date = [i.get('estimate_earnings_date') for i in data]
        self.next_earning_day       = [i.get('next_earning_day')       for i in data]
        self.insertion_timestamp    = [i.get('insertion_timestamp')    for i in data]
        self.sector                 = [i.get('sector')                 for i in data]

        self.data_dict = {
            'ticker_id': self.ticker_id,
            'name': self.name,
            'ticker': self.ticker,
            'mk_trade_time': self.mk_trade_time,
            'close': self.close,
            'change': self.change,
            'change_ratio': self.change_ratio,
            'market_value': self.market_value,
            'volume': self.volume,
            'turnover_rate': self.turnover_rate,
            'overnight': self.overnight,
            'pre_close': self.pre_close,
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'vibrate_ratio': self.vibrate_ratio,
            'avg_vol_10d': self.avg_vol_10d,
            'avg_vol_3m': self.avg_vol_3m,
            'neg_market_value': self.neg_market_value,
            'pe': self.pe,
            'forward_pe': self.forward_pe,
            'indicated_pe': self.indicated_pe,
            'pe_ttm': self.pe_ttm,
            'eps': self.eps,
            'eps_ttm': self.eps_ttm,
            'pb': self.pb,
            'total_shares': self.total_shares,
            'outstanding_shares': self.outstanding_shares,
            'fifty_high': self.fifty_high,
            'fifty_low': self.fifty_low,
            'dividend': self.dividend,
            'yield': self.yield_,  # Aliased due to keyword conflict
            'latest_dividend_date': self.latest_dividend_date,
            'latest_split_date': self.latest_split_date,
            'latest_earnings_date': self.latest_earnings_date,
            'ps': self.ps,
            'bps': self.bps,
            'estimate_earnings_date': self.estimate_earnings_date,
            'next_earning_day': self.next_earning_day,
            'insertion_timestamp': self.insertion_timestamp,
            'sector': self.sector
        }
        self.as_dataframe = pd.DataFrame(self.data_dict)

class OvernightTable:
    """
    Holds **overnight price and volume data** for multiple tickers.

    Attributes:
        ticker_id (list): Unique IDs for each ticker.
        name (list): Company names for each ticker.
        ticker (list): Ticker symbols.
        close (list): Previous closing prices.
        change (list): Change in price from previous close.
        change_pct (list): Percentage change from previous close.
        ovn_volume (list): Overnight volume.
        ovn_price (list): Overnight price.
        ovn_change (list): Change in price during overnight session.
        ovn_change_pct (list): Percentage change during overnight session.
        insertion_timestamp (list): Timestamps of record insertion.
    """
    def __init__(self, data):
        """
        Initialize the OvernightTable with data for each ticker.

        Args:
            data (list of dict): Raw data rows from the overnight price/volume table.
        """
        self.ticker_id           = [i.get('ticker_id')           for i in data]
        self.name                = [i.get('name')                for i in data]
        self.ticker              = [i.get('ticker')              for i in data]
        self.close               = [i.get('close')               for i in data]
        self.change              = [i.get('change')              for i in data]
        self.change_pct          = [i.get('change_pct')          for i in data]
        self.ovn_volume          = [i.get('ovn_volume')          for i in data]
        self.ovn_price           = [i.get('ovn_price')           for i in data]
        self.ovn_change          = [i.get('ovn_change')          for i in data]
        self.ovn_change_pct      = [i.get('ovn_change_pct')      for i in data]
        self.insertion_timestamp = [i.get('insertion_timestamp') for i in data]
        self.data_dict = {
            "ticker_id": self.ticker_id,
            "name": self.name,
            "ticker": self.ticker,
            "close": self.close,
            "change": self.change,
            "change_pct": self.change_pct,
            "ovn_volume": self.ovn_volume,
            "ovn_price": self.ovn_price,
            "ovn_change": self.ovn_change,
            "ovn_change_pct": self.ovn_change_pct,
            "insertion_timestamp": self.insertion_timestamp,
        }

        self.as_dataframe = pd.DataFrame(self.data_dict)

class YfInsidersTable:
    """
    Holds **insider trading data** (purchases and sales) from Yahoo Finance for one or more tickers.

    Attributes:
        ticker (list): Ticker symbols.
        shares_purchased (list): Number of shares purchased by insiders.
        shares_sold (list): Number of shares sold by insiders.
        net_shares_purchased (list): Net shares purchased (purchased - sold).
        total_shares_held (list): Total shares held by insiders after transactions.
        pct_net_shares_purchased (list): Percent net shares purchased.
        pct_buy_shares (list): Percent of transactions that are buys.
        pct_sell_shares (list): Percent of transactions that are sells.
        purchases_trans (list): Number of purchase transactions.
        sales_trans (list): Number of sale transactions.
        net_trans (list): Net number of transactions (purchases - sales).
        insertion_timestamp (list): Timestamps of record insertion.
    """
    def __init__(self, data):
        """
        Initialize the YfInsidersTable with insider trade data.

        Args:
            data (list of dict): Raw data rows from Yahoo Finance insider activity.
        """
        self.ticker                   = [i.get('ticker')                   for i in data]
        self.shares_purchased         = [i.get('shares_purchased')         for i in data]
        self.shares_sold              = [i.get('shares_sold')              for i in data]
        self.net_shares_purchased     = [i.get('net_shares_purchased')     for i in data]
        self.total_shares_held        = [i.get('total_shares_held')        for i in data]
        self.pct_net_shares_purchased = [i.get('pct_net_shares_purchased') for i in data]
        self.pct_buy_shares           = [i.get('pct_buy_shares')           for i in data]
        self.pct_sell_shares          = [i.get('pct_sell_shares')          for i in data]
        self.purchases_trans          = [i.get('purchases_trans')          for i in data]
        self.sales_trans              = [i.get('sales_trans')              for i in data]
        self.net_trans                = [i.get('net_trans')                for i in data]
        self.insertion_timestamp      = [i.get('insertion_timestamp')      for i in data]
        self.data_dict = {
            'ticker': self.ticker,
            'shares_purchased': self.shares_purchased,
            'shares_sold': self.shares_sold,
            'net_shares_purchased': self.net_shares_purchased,
            'total_shares_held': self.total_shares_held,
            'pct_net_shares_purchased': self.pct_net_shares_purchased,
            'pct_buy_shares': self.pct_buy_shares,
            'pct_sell_shares': self.pct_sell_shares,
            'purchases_trans': self.purchases_trans,
            'sales_trans': self.sales_trans,
            'net_trans': self.net_trans,
            'insertion_timestamp': self.insertion_timestamp
        }
        self.as_dataframe = pd.DataFrame(self.data_dict)
class IvSkewTable:
    """
    Holds **options IV skew and volume data** for multiple contracts and expiries.

    Attributes:
        ticker (list): Ticker symbols.
        strike (list): Option strike prices.
        call_put (list): Whether the option is a call or put.
        expiry (list): Expiration dates.
        option_symbol (list): Option symbol strings.
        option_id (list): Option contract IDs.
        iv (list): Implied volatility values.
        oi (list): Open interest values.
        oi_change (list): Change in open interest.
        total_trades (list): Total number of trades for the contract.
        avg_price (list): Average price.
        buy_vol (list): Buy-side volume.
        sell_vol (list): Sell-side volume.
        neut_vol (list): Neutral volume.
        insertion_timestamp (list): Timestamps of record insertion.
        skew_type (list): Type of IV skew (e.g., relative to ATM).
        skew_diff (list): Difference in IV skew.
    """
    def __init__(self, data):
        """
        Initialize the IvSkewTable with data about options IV skew and trading volume.

        Args:
            data (list of dict): Raw data rows for options IV skew analysis.
        """
        self.ticker              = [i.get('ticker') for i in data]
        self.strike              = [float(i.get('strike')) if i.get('strike') is not None else None for i in data]
        self.call_put            = [i.get('call_put') for i in data]
        self.expiry              = [i.get('expiry') for i in data]
        self.option_symbol       = [i.get('option_symbol') for i in data]
        self.option_id           = [int(i.get('option_id')) if i.get('option_id') is not None else None for i in data]
        self.iv                  = [float(i.get('iv')) if i.get('iv') is not None else None for i in data]
        self.oi                  = [float(i.get('oi')) if i.get('oi') is not None else None for i in data]
        self.oi_change           = [float(i.get('oi_change')) if i.get('oi_change') is not None else None for i in data]
        self.total_trades        = [int(i.get('total_trades')) if i.get('total_trades') is not None else None for i in data]
        self.avg_price           = [float(i.get('avg_price')) if i.get('avg_price') is not None else None for i in data]
        self.buy_vol             = [int(i.get('buy_vol')) if i.get('buy_vol') is not None else None for i in data]
        self.sell_vol            = [int(i.get('sell_vol')) if i.get('sell_vol') is not None else None for i in data]
        self.neut_vol            = [int(i.get('neut_vol')) if i.get('neut_vol') is not None else None for i in data]
        self.insertion_timestamp = [i.get('insertion_timestamp') for i in data]
        self.skew_type           = [i.get('skew_type') for i in data]
        self.skew_diff           = [float(i.get('skew_diff')) if i.get('skew_diff') is not None else None for i in data]

        self.data_dict = {
            'ticker': self.ticker,
            'strike': self.strike,
            'call_put': self.call_put,
            'expiry': self.expiry,
            'option_symbol': self.option_symbol,
            'option_id': self.option_id,
            'iv': self.iv,
            'oi': self.oi,
            'oi_change': self.oi_change,
            'total_trades': self.total_trades,
            'avg_price': self.avg_price,
            'buy_vol': self.buy_vol,
            'sell_vol': self.sell_vol,
            'neut_vol': self.neut_vol,
            'insertion_timestamp': self.insertion_timestamp,
            'skew_type': self.skew_type,
            'skew_diff': self.skew_diff
        }
        self.as_dataframe = pd.DataFrame(self.data_dict)

    def chat(self, prompt: str, max_rows: int = 5, model: str = "gpt-4o") -> str:
        """
        Send a prompt along with a summary of the table to OpenAI's chat model.

        Args:
            prompt (str): The user prompt/question.
            max_rows (int): Maximum number of table rows to include in the context.
            model (str): Which OpenAI model to use.

        Returns:
            str: The assistant's reply.
        """

        # Prepare a summary of up to `max_rows` from the table.
        table_preview = []
        for idx in range(min(max_rows, len(self.ticker))):
            row = {
                "ticker": self.ticker[idx],
                "strike": self.strike[idx],
                "call_put": self.call_put[idx],
                "expiry": self.expiry[idx],
                "iv": self.iv[idx],
                "oi": self.oi[idx],
                "buy_vol": self.buy_vol[idx],
                "sell_vol": self.sell_vol[idx],
                "skew_diff": self.skew_diff[idx],
            }
            table_preview.append(row)

        context = (
            f"Here is a sample of the options IV skew table data (first {len(table_preview)} rows):\n"
            + "\n".join(str(row) for row in table_preview)
        )

        # Compose full message for the model
        full_prompt = f"{context}\n\n{prompt}"

        # Call the OpenAI API
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful financial data analyst."},
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.4,
        )

        # Return the text response
        content = response.choices[0].message.content
        return content.strip() if content is not None else ""
    


class BalanceSheetTable:
    """
    Represents a company's balance sheet data extracted from financial reports.  
    This table includes assets, liabilities, equity, and debt breakdowns per fiscal period.

    Attributes:
        quote_id (list): Internal quote identifier.
        type (list): Classification type (e.g., annual=0, quarterly=1).
        fiscal_year (list): Fiscal year of the report.
        fiscal_period (list): Fiscal quarter (e.g., 1, 2, 3, 4).
        end_date (list): Reporting period end date (ISO string).
        publish_date (list): Date the report was published.
        
        # Assets
        total_assets (list): Total company assets.
        total_current_assets (list): Sum of current assets.
        cash_and_short_term_invest (list): Cash and near-cash instruments.
        cash (list): Cash holdings only.
        cash_equivalents (list): Highly liquid short-term investments.
        short_term_investments (list): Non-cash short-term financial instruments.
        total_receivables_net (list): Net receivables after provisions.
        accounts_rece_trade_net (list): Net accounts receivable from trade.
        total_inventory (list): Value of current inventory.
        other_current_assets_total (list): All other current assets.
        total_non_current_assets (list): All long-term/non-current assets.
        ppe_total_net (list): Net property, plant & equipment (after depreciation).
        ppe_total_gross (list): Gross PPE before depreciation.
        accumulated_depreciation_total (list): Total depreciation on assets.
        long_term_investments (list): Non-current investment holdings.
        other_long_term_assets_total (list): All other long-term assets.

        # Liabilities
        total_liabilities (list): Sum of current + non-current liabilities.
        total_current_liabilities (list): Liabilities due within a year.
        accounts_payable (list): Payables to vendors and suppliers.
        accrued_expenses (list): Liabilities for expenses incurred but not paid.
        notes_payable_short_term_debt (list): Short-term debt and notes payable.
        current_port_of_lt_debt_capital_leases (list): Current portion of long-term debt.
        other_current_liabilities_total (list): Other miscellaneous current liabilities.
        total_non_current_liabilities (list): Liabilities due beyond a year.
        total_long_term_debt (list): All long-term debt.
        long_term_debt (list): Debt obligations beyond 12 months.
        capital_lease_obligations (list): Long-term lease obligations.
        total_debt (list): Combined short-term and long-term debt.
        other_liabilities_total (list): Non-classified liabilities.

        # Equity
        total_equity (list): Shareholder equity + retained earnings.
        total_stockhoders_equity (list): Common + preferred equity.
        common_stock (list): Value of common shares issued.
        additional_paid_in_capital (list): Paid-in capital above par value.
        retained_earnings (list): Cumulative earnings retained.
        other_equity_total (list): Other equity instruments or adjustments.
        total_liabilities_shareholders_equity (list): Should equal total assets.
        total_common_shares_outstanding (list): Number of outstanding common shares.

        ticker (list): Stock symbol.
        insertion_timestamp (list): When this row was inserted into the database.
    """

    def __init__(self, data):
        self.quote_id                               = [i.get('quote_id') for i in data]
        self.type                                   = [i.get('type') for i in data]
        self.fiscal_year                            = [i.get('fiscal_year') for i in data]
        self.fiscal_period                          = [i.get('fiscal_period') for i in data]
        self.end_date                               = [i.get('end_date') for i in data]
        self.publish_date                           = [i.get('publish_date') for i in data]
        self.total_assets                           = [i.get('total_assets') for i in data]
        self.total_current_assets                   = [i.get('total_current_assets') for i in data]
        self.cash_and_short_term_invest             = [i.get('cash_and_short_term_invest') for i in data]
        self.cash                                   = [i.get('cash') for i in data]
        self.cash_equivalents                       = [i.get('cash_equivalents') for i in data]
        self.short_term_investments                 = [i.get('short_term_investments') for i in data]
        self.total_receivables_net                  = [i.get('total_receivables_net') for i in data]
        self.accounts_rece_trade_net                = [i.get('accounts_rece_trade_net') for i in data]
        self.total_inventory                        = [i.get('total_inventory') for i in data]
        self.other_current_assets_total             = [i.get('other_current_assets_total') for i in data]
        self.total_non_current_assets               = [i.get('total_non_current_assets') for i in data]
        self.ppe_total_net                          = [i.get('ppe_total_net') for i in data]
        self.ppe_total_gross                        = [i.get('ppe_total_gross') for i in data]
        self.accumulated_depreciation_total         = [i.get('accumulated_depreciation_total') for i in data]
        self.long_term_investments                  = [i.get('long_term_investments') for i in data]
        self.other_long_term_assets_total           = [i.get('other_long_term_assets_total') for i in data]
        self.total_liabilities                      = [i.get('total_liabilities') for i in data]
        self.total_current_liabilities              = [i.get('total_current_liabilities') for i in data]
        self.accounts_payable                       = [i.get('accounts_payable') for i in data]
        self.accrued_expenses                       = [i.get('accrued_expenses') for i in data]
        self.notes_payable_short_term_debt          = [i.get('notes_payable_short_term_debt') for i in data]
        self.current_port_of_lt_debt_capital_leases = [i.get('current_port_of_lt_debt_capital_leases') for i in data]
        self.other_current_liabilities_total        = [i.get('other_current_liabilities_total') for i in data]
        self.total_non_current_liabilities          = [i.get('total_non_current_liabilities') for i in data]
        self.total_long_term_debt                   = [i.get('total_long_term_debt') for i in data]
        self.long_term_debt                         = [i.get('long_term_debt') for i in data]
        self.capital_lease_obligations              = [i.get('capital_lease_obligations') for i in data]
        self.total_debt                             = [i.get('total_debt') for i in data]
        self.other_liabilities_total                = [i.get('other_liabilities_total') for i in data]
        self.total_equity                           = [i.get('total_equity') for i in data]
        self.total_stockhoders_equity               = [i.get('total_stockhoders_equity') for i in data]
        self.common_stock                           = [i.get('common_stock') for i in data]
        self.additional_paid_in_capital             = [i.get('additional_paid_in_capital') for i in data]
        self.retained_earnings                      = [i.get('retained_earnings') for i in data]
        self.other_equity_total                     = [i.get('other_equity_total') for i in data]
        self.total_liabilities_shareholders_equity  = [i.get('total_liabilities_shareholders_equity') for i in data]
        self.total_common_shares_outstanding        = [i.get('total_common_shares_outstanding') for i in data]
        self.ticker                                 = [i.get('ticker') for i in data]
        self.insertion_timestamp                    = [i.get('insertion_timestamp') for i in data]
        self.data_dict = {
            'quote_id': self.quote_id,
            'type': self.type,
            'fiscal_year': self.fiscal_year,
            'fiscal_period': self.fiscal_period,
            'end_date': self.end_date,
            'publish_date': self.publish_date,
            'total_assets': self.total_assets,
            'total_current_assets': self.total_current_assets,
            'cash_and_short_term_invest': self.cash_and_short_term_invest,
            'cash': self.cash,
            'cash_equivalents': self.cash_equivalents,
            'short_term_investments': self.short_term_investments,
            'total_receivables_net': self.total_receivables_net,
            'accounts_rece_trade_net': self.accounts_rece_trade_net,
            'total_inventory': self.total_inventory,
            'other_current_assets_total': self.other_current_assets_total,
            'total_non_current_assets': self.total_non_current_assets,
            'ppe_total_net': self.ppe_total_net,
            'ppe_total_gross': self.ppe_total_gross,
            'accumulated_depreciation_total': self.accumulated_depreciation_total,
            'long_term_investments': self.long_term_investments,
            'other_long_term_assets_total': self.other_long_term_assets_total,
            'total_liabilities': self.total_liabilities,
            'total_current_liabilities': self.total_current_liabilities,
            'accounts_payable': self.accounts_payable,
            'accrued_expenses': self.accrued_expenses,
            'notes_payable_short_term_debt': self.notes_payable_short_term_debt,
            'current_port_of_lt_debt_capital_leases': self.current_port_of_lt_debt_capital_leases,
            'other_current_liabilities_total': self.other_current_liabilities_total,
            'total_non_current_liabilities': self.total_non_current_liabilities,
            'total_long_term_debt': self.total_long_term_debt,
            'long_term_debt': self.long_term_debt,
            'capital_lease_obligations': self.capital_lease_obligations,
            'total_debt': self.total_debt,
            'other_liabilities_total': self.other_liabilities_total,
            'total_equity': self.total_equity,
            'total_stockhoders_equity': self.total_stockhoders_equity,
            'common_stock': self.common_stock,
            'additional_paid_in_capital': self.additional_paid_in_capital,
            'retained_earnings': self.retained_earnings,
            'other_equity_total': self.other_equity_total,
            'total_liabilities_shareholders_equity': self.total_liabilities_shareholders_equity,
            'total_common_shares_outstanding': self.total_common_shares_outstanding,
            'ticker': self.ticker,
            'insertion_timestamp': self.insertion_timestamp
        }
        self.as_dataframe = pd.DataFrame(self.data_dict)

class IncomeStatementTable:
    """
    Represents the financial income statement of a publicly traded company.
    Each attribute maps to a field in the `income_statement` table,
    capturing performance for a specific fiscal period.

    Attributes:
        quote_id (list): Internal reference ID.
        type (list): 0 = Annual, 1 = Quarterly.
        fiscal_year (list): The fiscal year of the statement.
        fiscal_period (list): The quarter number (1–4).
        end_date (list): Period ending date (e.g., '2023-12-31').
        publish_date (list): Date the earnings report was published.

        # Revenue & Profit
        total_revenue (list): Top-line revenue including all segments.
        revenue (list): Core business revenue.
        cost_of_revenue_total (list): Direct costs of goods/services sold.
        gross_profit (list): Revenue minus cost of revenue.

        # Expenses
        operating_expense (list): Total operating expenses.
        sell_gen_admin_expenses (list): SG&A: sales, general, and admin.
        research_development (list): R&D expenses for innovation.

        # Operating Income
        operating_income (list): Gross profit minus operating expenses.
        other_net_income (list): Other income (e.g., interest, one-offs).
        net_income_before_tax (list): Income before tax obligations.
        income_tax (list): Income taxes owed.
        net_income_after_tax (list): Net income after taxes.

        # Net Income Breakdown
        net_income_before_extra (list): Net income before extraordinary items.
        total_extraordinary_items (list): Gains/losses outside core operations.
        net_income (list): Final reported net income.
        income_ava_to_com_excl_extra_ord (list): Net income to common shareholders excluding extraordinary items.
        income_ava_to_com_incl_extra_ord (list): Net income to common shareholders including extraordinary items.

        # Diluted Metrics
        diluted_net_income (list): Net income assuming dilution.
        diluted_weighted_average_shares (list): Diluted shares outstanding.
        diluted_eps_excl_extra_items (list): EPS excluding extraordinary items.
        diluted_eps_incl_extra_items (list): EPS including extraordinary items.
        dividends_per_share (list): Dividends paid per share.
        diluted_normalized_eps (list): Adjusted diluted EPS (normalized).

        # Alternative Income Names
        operating_profit (list): Alias for operating income.
        earning_after_tax (list): Alias for net income after tax.
        earning_before_tax (list): Alias for net income before tax.

        ticker (list): Stock ticker symbol.
        insertion_timestamp (list): Time when the data was inserted.
    """

    def __init__(self, data):
        self.quote_id                         = [i.get('quote_id') for i in data]
        self.type                             = [i.get('type') for i in data]
        self.fiscal_year                      = [i.get('fiscal_year') for i in data]
        self.fiscal_period                    = [i.get('fiscal_period') for i in data]
        self.end_date                         = [i.get('end_date') for i in data]
        self.publish_date                     = [i.get('publish_date') for i in data]
        self.total_revenue                    = [i.get('total_revenue') for i in data]
        self.revenue                          = [i.get('revenue') for i in data]
        self.cost_of_revenue_total            = [i.get('cost_of_revenue_total') for i in data]
        self.gross_profit                     = [i.get('gross_profit') for i in data]
        self.operating_expense                = [i.get('operating_expense') for i in data]
        self.sell_gen_admin_expenses          = [i.get('sell_gen_admin_expenses') for i in data]
        self.research_development             = [i.get('research_development') for i in data]
        self.operating_income                 = [i.get('operating_income') for i in data]
        self.other_net_income                 = [i.get('other_net_income') for i in data]
        self.net_income_before_tax            = [i.get('net_income_before_tax') for i in data]
        self.income_tax                       = [i.get('income_tax') for i in data]
        self.net_income_after_tax             = [i.get('net_income_after_tax') for i in data]
        self.net_income_before_extra          = [i.get('net_income_before_extra') for i in data]
        self.total_extraordinary_items        = [i.get('total_extraordinary_items') for i in data]
        self.net_income                       = [i.get('net_income') for i in data]
        self.income_ava_to_com_excl_extra_ord = [i.get('income_ava_to_com_excl_extra_ord') for i in data]
        self.income_ava_to_com_incl_extra_ord = [i.get('income_ava_to_com_incl_extra_ord') for i in data]
        self.diluted_net_income               = [i.get('diluted_net_income') for i in data]
        self.diluted_weighted_average_shares  = [i.get('diluted_weighted_average_shares') for i in data]
        self.diluted_eps_excl_extra_items     = [i.get('diluted_eps_excl_extra_items') for i in data]
        self.diluted_eps_incl_extra_items     = [i.get('diluted_eps_incl_extra_items') for i in data]
        self.dividends_per_share              = [i.get('dividends_per_share') for i in data]
        self.diluted_normalized_eps           = [i.get('diluted_normalized_eps') for i in data]
        self.operating_profit                 = [i.get('operating_profit') for i in data]
        self.earning_after_tax                = [i.get('earning_after_tax') for i in data]
        self.earning_before_tax               = [i.get('earning_before_tax') for i in data]
        self.ticker                           = [i.get('ticker') for i in data]
        self.insertion_timestamp              = [i.get('insertion_timestamp') for i in data]

        self.data_dict = {
            'quote_id': self.quote_id,
            'type': self.type,
            'fiscal_year': self.fiscal_year,
            'fiscal_period': self.fiscal_period,
            'end_date': self.end_date,
            'publish_date': self.publish_date,
            'total_revenue': self.total_revenue,
            'revenue': self.revenue,
            'cost_of_revenue_total': self.cost_of_revenue_total,
            'gross_profit': self.gross_profit,
            'operating_expense': self.operating_expense,
            'sell_gen_admin_expenses': self.sell_gen_admin_expenses,
            'research_development': self.research_development,
            'operating_income': self.operating_income,
            'other_net_income': self.other_net_income,
            'net_income_before_tax': self.net_income_before_tax,
            'income_tax': self.income_tax,
            'net_income_after_tax': self.net_income_after_tax,
            'net_income_before_extra': self.net_income_before_extra,
            'total_extraordinary_items': self.total_extraordinary_items,
            'net_income': self.net_income,
            'income_ava_to_com_excl_extra_ord': self.income_ava_to_com_excl_extra_ord,
            'income_ava_to_com_incl_extra_ord': self.income_ava_to_com_incl_extra_ord,
            'diluted_net_income': self.diluted_net_income,
            'diluted_weighted_average_shares': self.diluted_weighted_average_shares,
            'diluted_eps_excl_extra_items': self.diluted_eps_excl_extra_items,
            'diluted_eps_incl_extra_items': self.diluted_eps_incl_extra_items,
            'dividends_per_share': self.dividends_per_share,
            'diluted_normalized_eps': self.diluted_normalized_eps,
            'operating_profit': self.operating_profit,
            'earning_after_tax': self.earning_after_tax,
            'earning_before_tax': self.earning_before_tax,
            'ticker': self.ticker,
            'insertion_timestamp': self.insertion_timestamp
        }

        self.as_dataframe = pd.DataFrame(self.data_dict)

class CashFlowTable:
    """
    Represents a company's cash flow statement data for a specific fiscal period.
    This class maps each row from the `cash_flow` table into structured attributes.

    Attributes:
        quote_id (list): Internal reference ID.
        type (list): 0 = Annual report, 1 = Quarterly report.
        fiscal_year (list): Year of the fiscal report.
        fiscal_period (list): Fiscal quarter (1–4).
        end_date (list): Period ending date (string format).
        publish_date (list): Date when the cash flow report was published.

        # Operating Activities
        cash_from_operating_activities (list): Net cash inflow from core operations.
        net_income (list): Net income reported in the period.
        depreciation_and_amortization (list): Non-cash depreciation & amortization.
        non_cash_items (list): Other adjustments for non-cash activities.
        changes_in_working_capital (list): Changes in current assets/liabilities.

        # Investing Activities
        cash_from_investing_activities (list): Cash used for or received from investments.
        capital_expenditures (list): Capital spending on assets (usually negative).
        other_investing_cash_flow_items_total (list): Miscellaneous investing cash flows.

        # Financing Activities
        cash_from_financing_activities (list): Net cash from financing activities.
        financing_cash_flow_items (list): Cash from issuing/repaying debt or equity.
        total_cash_dividends_paid (list): Dividends paid out in cash.
        issuance_retirement_of_stock_net (list): Net cash from issuing or buying back stock.
        issuance_retirement_of_debt_net (list): Net cash from issuing or retiring debt.

        # Summary
        net_change_in_cash (list): Total change in cash from all activities.
        cash_taxes_paid (list): Taxes paid in cash during the period.

        ticker (list): Stock ticker of the reporting company.
        insertion_timestamp (list): Timestamp when this record was inserted.
    """

    def __init__(self, data):
        self.quote_id                              = [i.get('quote_id') for i in data]
        self.type                                  = [i.get('type') for i in data]
        self.fiscal_year                           = [i.get('fiscal_year') for i in data]
        self.fiscal_period                         = [i.get('fiscal_period') for i in data]
        self.end_date                              = [i.get('end_date') for i in data]
        self.publish_date                          = [i.get('publish_date') for i in data]
        self.cash_from_operating_activities        = [i.get('cash_from_operating_activities') for i in data]
        self.net_income                            = [i.get('net_income') for i in data]
        self.depreciation_and_amortization         = [i.get('depreciation_and_amortization') for i in data]
        self.non_cash_items                        = [i.get('non_cash_items') for i in data]
        self.changes_in_working_capital            = [i.get('changes_in_working_capital') for i in data]
        self.cash_from_investing_activities        = [i.get('cash_from_investing_activities') for i in data]
        self.capital_expenditures                  = [i.get('capital_expenditures') for i in data]
        self.other_investing_cash_flow_items_total = [i.get('other_investing_cash_flow_items_total') for i in data]
        self.cash_from_financing_activities        = [i.get('cash_from_financing_activities') for i in data]
        self.financing_cash_flow_items             = [i.get('financing_cash_flow_items') for i in data]
        self.total_cash_dividends_paid             = [i.get('total_cash_dividends_paid') for i in data]
        self.issuance_retirement_of_stock_net      = [i.get('issuance_retirement_of_stock_net') for i in data]
        self.issuance_retirement_of_debt_net       = [i.get('issuance_retirement_of_debt_net') for i in data]
        self.net_change_in_cash                    = [i.get('net_change_in_cash') for i in data]
        self.cash_taxes_paid                       = [i.get('cash_taxes_paid') for i in data]
        self.ticker                                = [i.get('ticker') for i in data]
        self.insertion_timestamp                   = [i.get('insertion_timestamp') for i in data]

        self.data_dict = {
            'quote_id': self.quote_id,
            'type': self.type,
            'fiscal_year': self.fiscal_year,
            'fiscal_period': self.fiscal_period,
            'end_date': self.end_date,
            'publish_date': self.publish_date,
            'cash_from_operating_activities': self.cash_from_operating_activities,
            'net_income': self.net_income,
            'depreciation_and_amortization': self.depreciation_and_amortization,
            'non_cash_items': self.non_cash_items,
            'changes_in_working_capital': self.changes_in_working_capital,
            'cash_from_investing_activities': self.cash_from_investing_activities,
            'capital_expenditures': self.capital_expenditures,
            'other_investing_cash_flow_items_total': self.other_investing_cash_flow_items_total,
            'cash_from_financing_activities': self.cash_from_financing_activities,
            'financing_cash_flow_items': self.financing_cash_flow_items,
            'total_cash_dividends_paid': self.total_cash_dividends_paid,
            'issuance_retirement_of_stock_net': self.issuance_retirement_of_stock_net,
            'issuance_retirement_of_debt_net': self.issuance_retirement_of_debt_net,
            'net_change_in_cash': self.net_change_in_cash,
            'cash_taxes_paid': self.cash_taxes_paid,
            'ticker': self.ticker,
            'insertion_timestamp': self.insertion_timestamp
        }
        self.as_dataframe = pd.DataFrame(self.data_dict)
class TechnicalEventsTable:
    """
    Represents a list of technical analysis events for financial instruments,
    as stored in the `technical_events` table.

    Each instance attribute contains a list of values for the corresponding column in the table.
    """

    def __init__(self, data):
        """
        Initialize the TechnicalEventsTable with raw data.

        :param data: List of dictionaries, each representing a row from the technical_events table.
        """
        self.ticker_id           = [i.get('ticker_id') for i in data]
        self.name                = [i.get('name') for i in data]
        self.ticker              = [i.get('ticker') for i in data]
        self.type                = [i.get('type') for i in data]  # e.g., moving average crossover, RSI, MACD
        self.time_horizon        = [i.get('time_horizon') for i in data]  # e.g., m1, m5, m15, h1
        self.trade_time          = [i.get('trade_time') for i in data]  # timestamp of the trade
        self.close               = [i.get('close') for i in data]
        self.open                = [i.get('open') for i in data]
        self.high                = [i.get('high') for i in data]
        self.low                 = [i.get('low') for i in data]
        self.volume              = [i.get('volume') for i in data]
        self.change              = [i.get('change') for i in data]  # raw price change
        self.change_pct          = [i.get('change_pct') for i in data]  # percent change
        self.change_pct_ms       = [i.get('change_pct_ms') for i in data]  # change % over millisecond interval
        self.market_value        = [i.get('market_value') for i in data]  # market cap or price x volume
        self.pe_ttm              = [i.get('pe_ttm') for i in data]  # price-to-earnings trailing twelve months
        self.turnover_rate       = [i.get('turnover_rate') for i in data]
        self.vibration           = [i.get('vibration') for i in data]  # measure of price range volatility
        self.signal              = [i.get('signal') for i in data]  # buy/sell/neutral/etc.
        self.score               = [i.get('score') for i in data]  # confidence score or intensity
        self.insertion_timestamp = [i.get('insertion_timestamp') for i in data]  # data load timestamp
        self.data_dict = {
            'ticker_id': self.ticker_id,
            'name': self.name,
            'ticker': self.ticker,
            'type': self.type,
            'time_horizon': self.time_horizon,
            'trade_time': self.trade_time,
            'close': self.close,
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'volume': self.volume,
            'change': self.change,
            'change_pct': self.change_pct,
            'change_pct_ms': self.change_pct_ms,
            'market_value': self.market_value,
            'pe_ttm': self.pe_ttm,
            'turnover_rate': self.turnover_rate,
            'vibration': self.vibration,
            'signal': self.signal,
            'score': self.score,
            'insertion_timestamp': self.insertion_timestamp
        }
        self.as_dataframe = pd.DataFrame(self.data_dict)
class ContractsTable:
    """
    Represents option contracts with a focus on buy-side volume and trade data,
    as stored in the `buy_contracts` table.

    Each attribute is a list of column values for a batch of entries.
    """

    def __init__(self, data):
        """
        Initialize the BuyContractsTable with a list of records (typically from a database query).

        :param data: List[Dict], where each dict maps column names to their values.
        """
        self.option_id           = [i.get('option_id') for i in data]  # Unique identifier for the option
        self.ticker              = [i.get('ticker') for i in data]  # Ticker symbol of the underlying asset
        self.strike              = [i.get('strike') for i in data]  # Strike price of the contract
        self.call_put            = [i.get('call_put') for i in data]  # 'CALL' or 'PUT'
        self.expiry              = [i.get('expiry') for i in data]  # Expiration date as a string (e.g., '2025-07-19')
        self.total_trades        = [i.get('total_trades') for i in data]  # Number of trades for the contract
        self.total_vol           = [i.get('total_vol') for i in data]  # Total volume traded
        self.oi                  = [i.get('oi') for i in data]  # Open interest (contracts currently open)
        self.buy_vol             = [i.get('buy_vol') for i in data]  # Volume categorized as buy orders
        self.sell_vol            = [i.get('sell_vol') for i in data]  # Volume categorized as sell orders
        self.neut_vol            = [i.get('neut_vol') for i in data]  # Neutral or uncategorized volume
        self.insertion_timestamp = [i.get('insertion_timestamp') for i in data]  # Timestamp when data was inserted
        self.data_dict = {
            'option_id': self.option_id,
            'ticker': self.ticker,
            'strike': self.strike,
            'call_put': self.call_put,
            'expiry': self.expiry,
            'total_trades': self.total_trades,
            'total_vol': self.total_vol,
            'oi': self.oi,
            'buy_vol': self.buy_vol,
            'sell_vol': self.sell_vol,
            'neut_vol': self.neut_vol,
            'insertion_timestamp': self.insertion_timestamp
        }

        self.as_dataframe = pd.DataFrame(self.data_dict)

class StockMonitorTable:
    def __init__(self, data):
        self.atclose_eod         = [i.get('atclose_eod') for i in data]
        self.close_eod           = [i.get('close_eod') for i in data]
        self.companyname         = [i.get('companyname') for i in data]
        self.exchange            = [i.get('exchange') for i in data]
        self.hv20_eod            = [i.get('hv20_eod') for i in data]
        self.industry            = [i.get('industry') for i in data]
        self.openinterest_eod    = [i.get('openinterest_eod') for i in data]
        self.regionid            = [i.get('regionid') for i in data]
        self.stockid             = [i.get('stockid') for i in data]
        self.ticker              = [i.get('ticker') for i in data]
        self.ask                 = [i.get('ask') for i in data]
        self.bid                 = [i.get('bid') for i in data]
        self.change              = [i.get('change') for i in data]
        self.changepercent       = [i.get('changepercent') for i in data]
        self.high                = [i.get('high') for i in data]
        self.ivx1080             = [i.get('ivx1080') for i in data]
        self.ivx120              = [i.get('ivx120') for i in data]
        self.ivx14               = [i.get('ivx14') for i in data]
        self.ivx150              = [i.get('ivx150') for i in data]
        self.ivx180              = [i.get('ivx180') for i in data]
        self.ivx21               = [i.get('ivx21') for i in data]
        self.ivx270              = [i.get('ivx270') for i in data]
        self.ivx30               = [i.get('ivx30') for i in data]
        self.ivx360              = [i.get('ivx360') for i in data]
        self.ivx60               = [i.get('ivx60') for i in data]
        self.ivx7                = [i.get('ivx7') for i in data]
        self.ivx720              = [i.get('ivx720') for i in data]
        self.ivx90               = [i.get('ivx90') for i in data]
        self.last                = [i.get('last') for i in data]
        self.low                 = [i.get('low') for i in data]
        self.open                = [i.get('open') for i in data]
        self.optvol              = [i.get('optvol') for i in data]
        self.optvolcall          = [i.get('optvolcall') for i in data]
        self.optvolput           = [i.get('optvolput') for i in data]
        self.updatedate          = [i.get('updatedate') for i in data]
        self.insertion_timestamp = [i.get('insertion_timestamp') for i in data]

        self.data_dict = {
            'atclose_eod': self.atclose_eod,
            'close_eod': self.close_eod,
            'companyname': self.companyname,
            'exchange': self.exchange,
            'hv20_eod': self.hv20_eod,
            'industry': self.industry,
            'openinterest_eod': self.openinterest_eod,
            'regionid': self.regionid,
            'stockid': self.stockid,
            'ticker': self.ticker,
            'ask': self.ask,
            'bid': self.bid,
            'change': self.change,
            'changepercent': self.changepercent,
            'high': self.high,
            'ivx1080': self.ivx1080,
            'ivx120': self.ivx120,
            'ivx14': self.ivx14,
            'ivx150': self.ivx150,
            'ivx180': self.ivx180,
            'ivx21': self.ivx21,
            'ivx270': self.ivx270,
            'ivx30': self.ivx30,
            'ivx360': self.ivx360,
            'ivx60': self.ivx60,
            'ivx7': self.ivx7,
            'ivx720': self.ivx720,
            'ivx90': self.ivx90,
            'last': self.last,
            'low': self.low,
            'open': self.open,
            'optvol': self.optvol,
            'optvolcall': self.optvolcall,
            'optvolput': self.optvolput,
            'updatedate': self.updatedate,
            'insertion_timestamp': self.insertion_timestamp
        }

        self.as_dataframe = pd.DataFrame(self.data_dict)



class VolumeSummaryTable:
    """Sort by expiry asc"""
    def __init__(self, data):
        self.expiry              = [i.get('expiry') for i in data]
        self.call_volume         = [i.get('call_volume') for i in data]
        self.put_volume          = [i.get('put_volume') for i in data]
        self.ticker              = [i.get('ticker') for i in data]
        self.insertion_timestamp = [i.get('insertion_timestamp') for i in data]

        self.data_dict = {
            'expiry': self.expiry,
            'call_volume': self.call_volume,
            'put_volume': self.put_volume,
            'ticker': self.ticker,
            'insertion_timestamp': self.insertion_timestamp
        }


        self.as_dataframe = pd.DataFrame(self.data_dict)


class OISummaryTable:
    """Sort by expiry asc"""
    def __init__(self, data):
        self.expiry              = [i.get('expiry') for i in data]
        self.call_volume         = [i.get('call_volume') for i in data]
        self.put_volume          = [i.get('put_volume') for i in data]
        self.ticker              = [i.get('ticker') for i in data]
        self.insertion_timestamp = [i.get('insertion_timestamp') for i in data]

        self.data_dict = {
            'expiry': self.expiry,
            'call_volume': self.call_volume,
            'put_volume': self.put_volume,
            'ticker': self.ticker,
            'insertion_timestamp': self.insertion_timestamp
        }


        self.as_dataframe = pd.DataFrame(self.data_dict)



class OptionsMonitorTable:
    def __init__(self, data):
        self.call_change_eod = [i.get('call_change_eod') for i in data]
        self.call_ivbid = [i.get('call_ivbid') for i in data]
        self.call_iv_eod = [i.get('call_iv_eod') for i in data]
        self.put_theta_eod = [i.get('put_theta_eod') for i in data]
        self.call_ivask = [i.get('call_ivask') for i in data]
        self.call_days = [i.get('call_days') for i in data]
        self.call_mean_eod = [i.get('call_mean_eod') for i in data]
        self.call_ivint = [i.get('call_ivint') for i in data]
        self.put_asksize = [i.get('put_asksize') for i in data]
        self.call_delta_eod = [i.get('call_delta_eod') for i in data]
        self.call_bid_eod = [i.get('call_bid_eod') for i in data]
        self.call_theoprice_eod = [i.get('call_theoprice_eod') for i in data]
        self.put_iv = [i.get('put_iv') for i in data]
        self.call_ivint_eod = [i.get('call_ivint_eod') for i in data]
        self.call_ask_eod = [i.get('call_ask_eod') for i in data]
        self.call_iv = [i.get('call_iv') for i in data]
        self.put_days = [i.get('put_days') for i in data]
        self.put_iv_eod = [i.get('put_iv_eod') for i in data]
        self.call_volume_eod = [i.get('call_volume_eod') for i in data]
        self.put_change_eod = [i.get('put_change_eod') for i in data]
        self.call_ask = [i.get('call_ask') for i in data]
        self.call_bidtime = [i.get('call_bidtime') for i in data]
        self.call_rho = [i.get('call_rho') for i in data]
        self.call_forwardprice_eod = [i.get('call_forwardprice_eod') for i in data]
        self.call_mean = [i.get('call_mean') for i in data]
        self.put_bid_eod = [i.get('put_bid_eod') for i in data]
        self.call_bid = [i.get('call_bid') for i in data]
        self.call_volume = [i.get('call_volume') for i in data]
        self.call_alpha = [i.get('call_alpha') for i in data]
        self.call_vega = [i.get('call_vega') for i in data]
        self.put_bidtime = [i.get('put_bidtime') for i in data]
        self.put_theta = [i.get('put_theta') for i in data]
        self.put_symbol = [i.get('put_symbol') for i in data]
        self.put_ivask = [i.get('put_ivask') for i in data]
        self.put_changepercent_eod = [i.get('put_changepercent_eod') for i in data]
        self.put_ask = [i.get('put_ask') for i in data]
        self.put_rho = [i.get('put_rho') for i in data]
        self.call_openinterest_eod = [i.get('call_openinterest_eod') for i in data]
        self.put_ivint = [i.get('put_ivint') for i in data]
        self.put_theoprice = [i.get('put_theoprice') for i in data]
        self.call_asktime = [i.get('call_asktime') for i in data]
        self.put_bid = [i.get('put_bid') for i in data]
        self.call_gamma_eod = [i.get('call_gamma_eod') for i in data]
        self.put_ask_eod = [i.get('put_ask_eod') for i in data]
        self.call_symbol = [i.get('call_symbol') for i in data]
        self.put_paramvolapercent_eod = [i.get('put_paramvolapercent_eod') for i in data]
        self.call_asksize = [i.get('call_asksize') for i in data]
        self.put_volume = [i.get('put_volume') for i in data]
        self.call_alpha_eod = [i.get('call_alpha_eod') for i in data]
        self.put_volume_eod = [i.get('put_volume_eod') for i in data]
        self.put_ivbid = [i.get('put_ivbid') for i in data]
        self.call_pos = [i.get('call_pos') for i in data]
        self.put_delta_eod = [i.get('put_delta_eod') for i in data]
        self.put_changepercent = [i.get('put_changepercent') for i in data]
        self.put_mean_eod = [i.get('put_mean_eod') for i in data]
        self.call_changepercent = [i.get('call_changepercent') for i in data]
        self.put_asktime = [i.get('put_asktime') for i in data]
        self.put_pos = [i.get('put_pos') for i in data]
        self.put_theoprice_eod = [i.get('put_theoprice_eod') for i in data]
        self.put_gamma = [i.get('put_gamma') for i in data]
        self.call_days_eod = [i.get('call_days_eod') for i in data]
        self.call_bidsize = [i.get('call_bidsize') for i in data]
        self.call_delta = [i.get('call_delta') for i in data]
        self.put_change = [i.get('put_change') for i in data]
        self.call_paramvolapercent_eod = [i.get('call_paramvolapercent_eod') for i in data]
        self.call_theta_eod = [i.get('call_theta_eod') for i in data]
        self.call_change = [i.get('call_change') for i in data]
        self.put_ivint_eod = [i.get('put_ivint_eod') for i in data]
        self.call_theta = [i.get('call_theta') for i in data]
        self.put_vega = [i.get('put_vega') for i in data]
        self.put_days_eod = [i.get('put_days_eod') for i in data]
        self.put_forwardprice = [i.get('put_forwardprice') for i in data]
        self.call_rho_eod = [i.get('call_rho_eod') for i in data]
        self.quotetime = [i.get('quotetime') for i in data]
        self.put_vega_eod = [i.get('put_vega_eod') for i in data]
        self.strike = [i.get('strike') for i in data]
        self.put_mean = [i.get('put_mean') for i in data]
        self.put_forwardprice_eod = [i.get('put_forwardprice_eod') for i in data]
        self.expiry = [i.get('expiry') for i in data]
        self.call_forwardprice = [i.get('call_forwardprice') for i in data]
        self.call_gamma = [i.get('call_gamma') for i in data]
        self.put_alpha_eod = [i.get('put_alpha_eod') for i in data]
        self.put_delta = [i.get('put_delta') for i in data]
        self.put_openinterest_eod = [i.get('put_openinterest_eod') for i in data]
        self.call_changepercent_eod = [i.get('call_changepercent_eod') for i in data]
        self.put_gamma_eod = [i.get('put_gamma_eod') for i in data]
        self.put_bidsize = [i.get('put_bidsize') for i in data]
        self.call_vega_eod = [i.get('call_vega_eod') for i in data]
        self.put_rho_eod = [i.get('put_rho_eod') for i in data]
        self.put_alpha = [i.get('put_alpha') for i in data]
        self.call_theoprice = [i.get('call_theoprice') for i in data]
        self.ticker = [i.get('ticker') for i in data]
        self.insertion_timestamp = [i.get('insertion_timestamp') for i in data]

        self.data_dict = {
            'call_change_eod': self.call_change_eod,
            'call_ivbid': self.call_ivbid,
            'call_iv_eod': self.call_iv_eod,
            'put_theta_eod': self.put_theta_eod,
            'call_ivask': self.call_ivask,
            'call_days': self.call_days,
            'call_mean_eod': self.call_mean_eod,
            'call_ivint': self.call_ivint,
            'put_asksize': self.put_asksize,
            'call_delta_eod': self.call_delta_eod,
            'call_bid_eod': self.call_bid_eod,
            'call_theoprice_eod': self.call_theoprice_eod,
            'put_iv': self.put_iv,
            'call_ivint_eod': self.call_ivint_eod,
            'call_ask_eod': self.call_ask_eod,
            'call_iv': self.call_iv,
            'put_days': self.put_days,
            'put_iv_eod': self.put_iv_eod,
            'call_volume_eod': self.call_volume_eod,
            'put_change_eod': self.put_change_eod,
            'call_ask': self.call_ask,
            'call_bidtime': self.call_bidtime,
            'call_rho': self.call_rho,
            'call_forwardprice_eod': self.call_forwardprice_eod,
            'call_mean': self.call_mean,
            'put_bid_eod': self.put_bid_eod,
            'call_bid': self.call_bid,
            'call_volume': self.call_volume,
            'call_alpha': self.call_alpha,
            'call_vega': self.call_vega,
            'put_bidtime': self.put_bidtime,
            'put_theta': self.put_theta,
            'put_symbol': self.put_symbol,
            'put_ivask': self.put_ivask,
            'put_changepercent_eod': self.put_changepercent_eod,
            'put_ask': self.put_ask,
            'put_rho': self.put_rho,
            'call_openinterest_eod': self.call_openinterest_eod,
            'put_ivint': self.put_ivint,
            'put_theoprice': self.put_theoprice,
            'call_asktime': self.call_asktime,
            'put_bid': self.put_bid,
            'call_gamma_eod': self.call_gamma_eod,
            'put_ask_eod': self.put_ask_eod,
            'call_symbol': self.call_symbol,
            'put_paramvolapercent_eod': self.put_paramvolapercent_eod,
            'call_asksize': self.call_asksize,
            'put_volume': self.put_volume,
            'call_alpha_eod': self.call_alpha_eod,
            'put_volume_eod': self.put_volume_eod,
            'put_ivbid': self.put_ivbid,
            'call_pos': self.call_pos,
            'put_delta_eod': self.put_delta_eod,
            'put_changepercent': self.put_changepercent,
            'put_mean_eod': self.put_mean_eod,
            'call_changepercent': self.call_changepercent,
            'put_asktime': self.put_asktime,
            'put_pos': self.put_pos,
            'put_theoprice_eod': self.put_theoprice_eod,
            'put_gamma': self.put_gamma,
            'call_days_eod': self.call_days_eod,
            'call_bidsize': self.call_bidsize,
            'call_delta': self.call_delta,
            'put_change': self.put_change,
            'call_paramvolapercent_eod': self.call_paramvolapercent_eod,
            'call_theta_eod': self.call_theta_eod,
            'call_change': self.call_change,
            'put_ivint_eod': self.put_ivint_eod,
            'call_theta': self.call_theta,
            'put_vega': self.put_vega,
            'put_days_eod': self.put_days_eod,
            'put_forwardprice': self.put_forwardprice,
            'call_rho_eod': self.call_rho_eod,
            'quotetime': self.quotetime,
            'put_vega_eod': self.put_vega_eod,
            'strike': self.strike,
            'put_mean': self.put_mean,
            'put_forwardprice_eod': self.put_forwardprice_eod,
            'expiry': self.expiry,
            'call_forwardprice': self.call_forwardprice,
            'call_gamma': self.call_gamma,
            'put_alpha_eod': self.put_alpha_eod,
            'put_delta': self.put_delta,
            'put_openinterest_eod': self.put_openinterest_eod,
            'call_changepercent_eod': self.call_changepercent_eod,
            'put_gamma_eod': self.put_gamma_eod,
            'put_bidsize': self.put_bidsize,
            'call_vega_eod': self.call_vega_eod,
            'put_rho_eod': self.put_rho_eod,
            'put_alpha': self.put_alpha,
            'call_theoprice': self.call_theoprice,
            'ticker': self.ticker,
            'insertion_timestamp': self.insertion_timestamp,
        }
        self.as_dataframe = pd.DataFrame(self.data_dict)
class AlertsTable:
    def __init__(self, data):
        self.ticker = [i.get('ticker') for i in data]
        self.alert = [i.get('alert') for i in data]
        self.volume = [i.get('volume') for i in data]
        self.change_ratio = [i.get('change_ratio') for i in data]
        self.sid = [i.get('sid') for i in data]
        self.insertion_timestamp = [i.get('insertion_timestamp') for i in data]


        self.data_dict = { 
            'ticker': self.ticker,
            'alert': self.alert,
            'volume': self.volume,
            'change_ratio': self.change_ratio,
            'sid': self.sid,
            'insertion_timestamp': self.insertion_timestamp
        }


        self.as_dataframe = pd.DataFrame(self.data_dict)



class InstitutionsTable:
    def __init__(self, data):
        self.holding_count         = [i.get('holding_count')         for i in data]
        self.holding_change        = [i.get('holding_change')        for i in data]
        self.holding_ratio         = [i.get('holding_ratio')         for i in data]
        self.ratio_change          = [i.get('ratio_change')          for i in data]
        self.institution_count     = [i.get('institution_count')     for i in data]
        self.new_count_change      = [i.get('new_count_change')      for i in data]
        self.new_institution_count = [i.get('new_institution_count') for i in data]
        self.increased_count       = [i.get('increased_count')       for i in data]
        self.increased_change      = [i.get('increased_change')      for i in data]
        self.sold_count            = [i.get('sold_count')            for i in data]
        self.sold_change           = [i.get('sold_change')           for i in data]
        self.decrease_count        = [i.get('decrease_count')        for i in data]
        self.decrease_change       = [i.get('decrease_change')       for i in data]
        self.ticker                = [i.get('ticker')                for i in data]
        self.insertion_timestamp   = [i.get('insertion_timestamp')   for i in data]

        self.data_dict = {
            'holding_count': self.holding_count,
            'holding_change': self.holding_change,
            'holding_ratio': self.holding_ratio,
            'ratio_change': self.ratio_change,
            'institution_count': self.institution_count,
            'new_count_change': self.new_count_change,
            'new_institution_count': self.new_institution_count,
            'increased_count': self.increased_count,
            'increased_change': self.increased_change,
            'sold_count': self.sold_count,
            'sold_change': self.sold_change,
            'decrease_count': self.decrease_count,
            'decrease_change': self.decrease_change,
            'ticker': self.ticker,
            'insertion_timestamp': self.insertion_timestamp
        }
        self.as_dataframe = pd.DataFrame(self.data_dict)



class EtfHoldingsTable:
    def __init__(self, data):
        self.fund_id             = [i.get('fund_id')             for i in data]
        self.fund_name           = [i.get('fund_name')           for i in data]
        self.change_pct          = [i.get('change_pct')          for i in data]
        self.share_number        = [i.get('share_number')        for i in data]
        self.ratio               = [i.get('ratio')               for i in data]
        self.ticker_id           = [i.get('ticker_id')           for i in data]
        self.ticker_name         = [i.get('ticker_name')         for i in data]
        self.ticker              = [i.get('ticker')              for i in data]
        self.insertion_timestamp = [i.get('insertion_timestamp') for i in data]

        self.data_dict = {
            'fund_id': self.fund_id,
            'fund_name': self.fund_name,
            'change_pct': self.change_pct,
            'share_number': self.share_number,
            'ratio': self.ratio,
            'ticker_id': self.ticker_id,
            'ticker_name': self.ticker_name,
            'ticker': self.ticker,
            'insertion_timestamp': self.insertion_timestamp,
        }


        self.as_dataframe = pd.DataFrame(self.data_dict)



class CapitalFlowTable:
    def __init__(self, data):
        self.super_inflow            = [i.get('super_inflow') for i in data]
        self.super_netflow           = [i.get('super_netflow') for i in data]
        self.super_outflow           = [i.get('super_outflow') for i in data]
        self.large_inflow            = [i.get('large_inflow') for i in data]
        self.large_netflow           = [i.get('large_netflow') for i in data]
        self.large_outflow           = [i.get('large_outflow') for i in data]
        self.newlarge_inflow         = [i.get('newlarge_inflow') for i in data]
        self.newlarge_outflow        = [i.get('newlarge_outflow') for i in data]
        self.newlarge_netflow        = [i.get('newlarge_netflow') for i in data]
        self.newlarge_inflow_ratio   = [i.get('newlarge_inflow_ratio') for i in data]
        self.newlarge_outflow_ratio  = [i.get('newlarge_outflow_ratio') for i in data]
        self.medium_inflow           = [i.get('medium_inflow') for i in data]
        self.medium_outflow          = [i.get('medium_outflow') for i in data]
        self.medium_netflow          = [i.get('medium_netflow') for i in data]
        self.medium_inflow_ratio     = [i.get('medium_inflow_ratio') for i in data]
        self.medium_outflow_ratio    = [i.get('medium_outflow_ratio') for i in data]
        self.small_inflow            = [i.get('small_inflow') for i in data]
        self.small_outflow           = [i.get('small_outflow') for i in data]
        self.small_netflow           = [i.get('small_netflow') for i in data]
        self.small_inflow_ratio      = [i.get('small_inflow_ratio') for i in data]
        self.small_outflow_ratio     = [i.get('small_outflow_ratio') for i in data]
        self.major_inflow            = [i.get('major_inflow') for i in data]
        self.major_outflow           = [i.get('major_outflow') for i in data]
        self.major_netflow           = [i.get('major_netflow') for i in data]
        self.major_inflow_ratio      = [i.get('major_inflow_ratio') for i in data]
        self.major_outflow_ratio     = [i.get('major_outflow_ratio') for i in data]
        self.retail_inflow           = [i.get('retail_inflow') for i in data]
        self.retail_inflow_ratio     = [i.get('retail_inflow_ratio') for i in data]
        self.retail_outflow          = [i.get('retail_outflow') for i in data]
        self.retail_outflow_ratio    = [i.get('retail_outflow_ratio') for i in data]
        self.date                    = [i.get('date') for i in data]
        self.ticker                  = [i.get('ticker') for i in data]
        self.insertion_timestamp     = [i.get('insertion_timestamp') for i in data]
        self.latest                  = [i.get('latest') for i in data]

        self.data_dict = {
            'super_inflow': self.super_inflow,
            'super_netflow': self.super_netflow,
            'super_outflow': self.super_outflow,
            'large_inflow': self.large_inflow,
            'large_netflow': self.large_netflow,
            'large_outflow': self.large_outflow,
            'newlarge_inflow': self.newlarge_inflow,
            'newlarge_outflow': self.newlarge_outflow,
            'newlarge_netflow': self.newlarge_netflow,
            'newlarge_inflow_ratio': self.newlarge_inflow_ratio,
            'newlarge_outflow_ratio': self.newlarge_outflow_ratio,
            'medium_inflow': self.medium_inflow,
            'medium_outflow': self.medium_outflow,
            'medium_netflow': self.medium_netflow,
            'medium_inflow_ratio': self.medium_inflow_ratio,
            'medium_outflow_ratio': self.medium_outflow_ratio,
            'small_inflow': self.small_inflow,
            'small_outflow': self.small_outflow,
            'small_netflow': self.small_netflow,
            'small_inflow_ratio': self.small_inflow_ratio,
            'small_outflow_ratio': self.small_outflow_ratio,
            'major_inflow': self.major_inflow,
            'major_outflow': self.major_outflow,
            'major_netflow': self.major_netflow,
            'major_inflow_ratio': self.major_inflow_ratio,
            'major_outflow_ratio': self.major_outflow_ratio,
            'retail_inflow': self.retail_inflow,
            'retail_inflow_ratio': self.retail_inflow_ratio,
            'retail_outflow': self.retail_outflow,
            'retail_outflow_ratio': self.retail_outflow_ratio,
            'date': self.date,
            'ticker': self.ticker,
            'insertion_timestamp': self.insertion_timestamp,
            'latest': self.latest,
        }

        self.as_dataframe = pd.DataFrame(self.data_dict)



class TickerBondsTable:
    def __init__(self, data):
        self.ticker_id           = [i.get('ticker_id') for i in data]
        self.bond_ticker         = [i.get('bond_ticker') for i in data]
        self.isin                = [i.get('isin') for i in data]
        self.full_name           = [i.get('full_name') for i in data]
        self.name                = [i.get('name') for i in data]
        self.expiry              = [i.get('expiry') for i in data]
        self.par_value           = [i.get('par_value') for i in data]
        self.coupon              = [i.get('coupon') for i in data]
        self.accrued_interest    = [i.get('accrued_interest') for i in data]
        self.coupon_frequency    = [i.get('coupon_frequency') for i in data]
        self.coupon_freq_desc    = [i.get('coupon_freq_desc') for i in data]
        self.term                = [i.get('term') for i in data]
        self.close               = [i.get('close') for i in data]
        self.change              = [i.get('change') for i in data]
        self.change_ratio        = [i.get('change_ratio') for i in data]
        self.bond_yield          = [i.get('bond_yield') for i in data]
        self.yield_ytw           = [i.get('yield_ytw') for i in data]
        self.ask_price           = [i.get('ask_price') for i in data]
        self.bid_price           = [i.get('bid_price') for i in data]
        self.ask_min_size        = [i.get('ask_min_size') for i in data]
        self.bid_min_size        = [i.get('bid_min_size') for i in data]
        self.ask_volume          = [i.get('ask_volume') for i in data]
        self.bid_volume          = [i.get('bid_volume') for i in data]
        self.ask_yield           = [i.get('ask_yield') for i in data]
        self.odd_lot_support     = [i.get('odd_lot_support') for i in data]
        self.ask_yield_ytw       = [i.get('ask_yield_ytw') for i in data]
        self.bid_yield           = [i.get('bid_yield') for i in data]
        self.bid_yield_ytw       = [i.get('bid_yield_ytw') for i in data]
        self.rating              = [i.get('rating') for i in data]
        self.duration            = [i.get('duration') for i in data]
        self.convexity           = [i.get('convexity') for i in data]
        self.issue_date          = [i.get('issue_date') for i in data]
        self.issuer_name         = [i.get('issuer_name') for i in data]
        self.is_callable         = [i.get('is_callable') for i in data]
        self.next_call_date      = [i.get('next_call_date') for i in data]
        self.next_call_price     = [i.get('next_call_price') for i in data]
        self.ticker              = [i.get('ticker') for i in data]
        self.insertion_timestamp = [i.get('insertion_timestamp') for i in data]
        self.data_dict = {
                    "ticker_id": self.ticker_id,
                    "bond_ticker": self.bond_ticker,
                    "isin": self.isin,
                    "full_name": self.full_name,
                    "name": self.name,
                    "expiry": self.expiry,
                    "par_value": self.par_value,
                    "coupon": self.coupon,
                    "accrued_interest": self.accrued_interest,
                    "coupon_frequency": self.coupon_frequency,
                    "coupon_freq_desc": self.coupon_freq_desc,
                    "term": self.term,
                    "close": self.close,
                    "change": self.change,
                    "change_ratio": self.change_ratio,
                    "bond_yield": self.bond_yield,
                    "yield_ytw": self.yield_ytw,
                    "ask_price": self.ask_price,
                    "bid_price": self.bid_price,
                    "ask_min_size": self.ask_min_size,
                    "bid_min_size": self.bid_min_size,
                    "ask_volume": self.ask_volume,
                    "bid_volume": self.bid_volume,
                    "ask_yield": self.ask_yield,
                    "odd_lot_support": self.odd_lot_support,
                    "ask_yield_ytw": self.ask_yield_ytw,
                    "bid_yield": self.bid_yield,
                    "bid_yield_ytw": self.bid_yield_ytw,
                    "rating": self.rating,
                    "duration": self.duration,
                    "convexity": self.convexity,
                    "issue_date": self.issue_date,
                    "issuer_name": self.issuer_name,
                    "is_callable": self.is_callable,
                    "next_call_date": self.next_call_date,
                    "next_call_price": self.next_call_price,
                    "ticker": self.ticker,
                    "insertion_timestamp": self.insertion_timestamp
                }
        
        self.as_dataframe = pd.DataFrame(self.data_dict)

class TopFollowedTable:
    def __init__(self, data):
        self.ticker_id           = [i.get('ticker_id') for i in data]
        self.name                = [i.get('name') for i in data]
        self.ticker              = [i.get('ticker') for i in data]
        self.trade_time          = [i.get('trade_time') for i in data]
        self.close               = [i.get('close') for i in data]
        self.change              = [i.get('change') for i in data]
        self.change_pct          = [i.get('change_pct') for i in data]
        self.last_price          = [i.get('last_price') for i in data]
        self.last_change         = [i.get('last_change') for i in data]
        self.last_change_pct     = [i.get('last_change_pct') for i in data]
        self.market_value        = [i.get('market_value') for i in data]
        self.volume              = [i.get('volume') for i in data]
        self.turnover_rate       = [i.get('turnover_rate') for i in data]
        self.high                = [i.get('high') for i in data]
        self.low                 = [i.get('low') for i in data]
        self.vibration           = [i.get('vibration') for i in data]
        self.pe_ttm              = [i.get('pe_ttm') for i in data]
        self.followers           = [i.get('followers') for i in data]
        self.type                = [i.get('type') for i in data]
        self.insertion_timestamp = [i.get('insertion_timestamp') for i in data]

        self.data_dict = {
            "ticker_id": self.ticker_id,
            "name": self.name,
            "ticker": self.ticker,
            "trade_time": self.trade_time,
            "close": self.close,
            "change": self.change,
            "change_pct": self.change_pct,
            "last_price": self.last_price,
            "last_change": self.last_change,
            "last_change_pct": self.last_change_pct,
            "market_value": self.market_value,
            "volume": self.volume,
            "turnover_rate": self.turnover_rate,
            "high": self.high,
            "low": self.low,
            "vibration": self.vibration,
            "pe_ttm": self.pe_ttm,
            "followers": self.followers,
            "type": self.type,
            "insertion_timestamp": self.insertion_timestamp,
        }

        self.as_dataframe = pd.DataFrame(self.data_dict)


class FactorsTable:
    def __init__(self, data):
        self.dates               = [i.get('dates') for i in data]
        self.factor_price_pre    = [i.get('factor_price_pre') for i in data]
        self.factor_price_post   = [i.get('factor_price_post') for i in data]
        self.factor_volume_pre   = [i.get('factor_volume_pre') for i in data]
        self.factor_volume_post  = [i.get('factor_volume_post') for i in data]
        self.timespan            = [i.get('timespan') for i in data]
        self.ticker              = [i.get('ticker') for i in data]
        self.insertion_timestamp = [i.get('insertion_timestamp') for i in data]

        self.data_dict = {
            "dates": self.dates,
            "factor_price_pre": self.factor_price_pre,
            "factor_price_post": self.factor_price_post,
            "factor_volume_pre": self.factor_volume_pre,
            "factor_volume_post": self.factor_volume_post,
            "timespan": self.timespan,
            "ticker": self.ticker,
            "insertion_timestamp": self.insertion_timestamp,
        }

        self.as_dataframe = pd.DataFrame(self.data_dict)



class IposUpcomingTable:
    def __init__(self, data):
        self.ticker              = [i.get('ticker') for i in data]
        self.name                = [i.get('name') for i in data]
        self.issue_down_limit    = [i.get('issue_down_limit') for i in data]
        self.issued_shares       = [i.get('issued_shares') for i in data]
        self.prospectus_date     = [i.get('prospectus_date') for i in data]
        self.purchase_end_date   = [i.get('purchase_end_date') for i in data]
        self.prospectus_url      = [i.get('prospectus_url') for i in data]
        self.ipo_status          = [i.get('ipo_status') for i in data]
        self.close_days          = [i.get('close_days') for i in data]
        self.offering_type       = [i.get('offering_type') for i in data]
        self.change              = [i.get('change') for i in data]
        self.change_pct          = [i.get('change_pct') for i in data]
        self.volume              = [i.get('volume') for i in data]
        self.status              = [i.get('status') for i in data]
        self.insertion_timestamp = [i.get('insertion_timestamp') for i in data]

        self.data_dict = {
            "ticker": self.ticker,
            "name": self.name,
            "issue_down_limit": self.issue_down_limit,
            "issued_shares": self.issued_shares,
            "prospectus_date": self.prospectus_date,
            "purchase_end_date": self.purchase_end_date,
            "prospectus_url": self.prospectus_url,
            "ipo_status": self.ipo_status,
            "close_days": self.close_days,
            "offering_type": self.offering_type,
            "change": self.change,
            "change_pct": self.change_pct,
            "volume": self.volume,
            "status": self.status,
            "insertion_timestamp": self.insertion_timestamp,
        }

        self.as_dataframe = pd.DataFrame(self.data_dict)



class IposFilingTable:
    def __init__(self, data):
        self.ticker              = [i.get('ticker') for i in data]
        self.name                = [i.get('name') for i in data]
        self.issue_down_limit    = [i.get('issue_down_limit') for i in data]
        self.issued_shares       = [i.get('issued_shares') for i in data]
        self.prospectus_date     = [i.get('prospectus_date') for i in data]
        self.purchase_end_date   = [i.get('purchase_end_date') for i in data]
        self.prospectus_url      = [i.get('prospectus_url') for i in data]
        self.ipo_status          = [i.get('ipo_status') for i in data]
        self.close_days          = [i.get('close_days') for i in data]
        self.offering_type       = [i.get('offering_type') for i in data]
        self.change              = [i.get('change') for i in data]
        self.change_pct          = [i.get('change_pct') for i in data]
        self.volume              = [i.get('volume') for i in data]
        self.status              = [i.get('status') for i in data]
        self.insertion_timestamp = [i.get('insertion_timestamp') for i in data]

        self.data_dict = {
            "ticker": self.ticker,
            "name": self.name,
            "issue_down_limit": self.issue_down_limit,
            "issued_shares": self.issued_shares,
            "prospectus_date": self.prospectus_date,
            "purchase_end_date": self.purchase_end_date,
            "prospectus_url": self.prospectus_url,
            "ipo_status": self.ipo_status,
            "close_days": self.close_days,
            "offering_type": self.offering_type,
            "change": self.change,
            "change_pct": self.change_pct,
            "volume": self.volume,
            "status": self.status,
            "insertion_timestamp": self.insertion_timestamp,
        }


        self.as_dataframe = pd.DataFrame(self.data_dict)



class ItmDollarsTable:
    def __init__(self, data):
        self.ticker              = [i.get('ticker') for i in data]
        self.expiry              = [i.get('expiry') for i in data]
        self.call_put            = [i.get('call_put') for i in data]
        self.strike              = [i.get('strike') for i in data]
        self.total_oi            = [i.get('total_oi') for i in data]
        self.intrinsic           = [i.get('intrinsic') for i in data]
        self.itm_dollars         = [i.get('itm_dollars') for i in data]
        self.price               = [i.get('price') for i in data]
        self.insertion_timestamp = [i.get('insertion_timestamp') for i in data]

        self.data_dict = {
            "ticker": self.ticker,
            "expiry": self.expiry,
            "call_put": self.call_put,
            "strike": self.strike,
            "total_oi": self.total_oi,
            "intrinsic": self.intrinsic,
            "itm_dollars": self.itm_dollars,
            "price": self.price,
            "insertion_timestamp": self.insertion_timestamp,
        }

        self.as_dataframe = pd.DataFrame(self.data_dict)



class GapsTable:
    def __init__(self, data):
        self.type                = [i.get('type') for i in data]
        self.from_ts             = [i.get('from_ts') for i in data]
        self.to_ts               = [i.get('to_ts') for i in data]
        self.gap_low             = [i.get('gap_low') for i in data]
        self.gap_high            = [i.get('gap_high') for i in data]
        self.gap_size            = [i.get('gap_size') for i in data]
        self.timespan            = [i.get('timespan') for i in data]
        self.c                   = [i.get('c') for i in data]
        self.gap_low_pct         = [i.get('gap_low_pct') for i in data]
        self.gap_high_pct        = [i.get('gap_high_pct') for i in data]
        self.ticker              = [i.get('ticker') for i in data]
        self.insertion_timestamp = [i.get('insertion_timestamp') for i in data]

        self.data_dict = {
            "type": self.type,
            "from_ts": self.from_ts,
            "to_ts": self.to_ts,
            "gap_low": self.gap_low,
            "gap_high": self.gap_high,
            "gap_size": self.gap_size,
            "timespan": self.timespan,
            "c": self.c,
            "gap_low_pct": self.gap_low_pct,
            "gap_high_pct": self.gap_high_pct,
            "ticker": self.ticker,
            "insertion_timestamp": self.insertion_timestamp,
        }

        self.as_dataframe = pd.DataFrame(self.data_dict)



class HistoricIVXTable:
    def __init__(self, data):
        self.hv20                = [i.get('hv20') for i in data]
        self.ivx30               = [i.get('ivx30') for i in data]
        self.date                = [i.get('date') for i in data]
        self.ticker              = [i.get('ticker') for i in data]
        self.insertion_timestamp = [i.get('insertion_timestamp') for i in data]

        self.data_dict = {
            "hv20": self.hv20,
            "ivx30": self.ivx30,
            "date": self.date,
            "ticker": self.ticker,
            "insertion_timestamp": self.insertion_timestamp,
        }

        self.as_dataframe = pd.DataFrame(self.data_dict)



class OptionsQuery:
    def __init__(self, derivative, query_filters=None): 
        # Defensive: handle missing keys, empty list
        self.tickerId        = [i.get('tickerId', None)        for i in derivative]
        self.symbol          = [i.get('symbol', None)          for i in derivative]
        self.unSymbol        = [i.get('unSymbol', None)        for i in derivative]
        self.belongTickerId  = [i.get('belongTickerId', None)  for i in derivative]
        self.direction       = [i.get('direction', None)       for i in derivative]
        self.expireDate      = [i.get('expireDate', None)      for i in derivative]
        # Safely parse as float, default to None if not present
        self.strikePrice     = [float(i.get('strikePrice', 'nan')) if i.get('strikePrice') is not None else None for i in derivative]
        self.change          = [float(i.get('change', 'nan'))       if i.get('change') is not None else None for i in derivative]
        self.changeRatio     = [float(i.get('changeRatio', 'nan'))  if i.get('changeRatio') is not None else None for i in derivative]

        # Normalized query: always JSON, sorted keys, no None values
        if query_filters:
            clean_filters = {k: v for k, v in query_filters.items() if v is not None}
            query_json = json.dumps(clean_filters, sort_keys=True)
        else:
            query_json = "{}"

        self.data_dict = { 
            'ticker_id':   self.belongTickerId,
            'option_id':   self.tickerId,
            'ticker':      self.unSymbol,
            'strike':      self.strikePrice,
            'call_put':    self.direction,
            'expiry':      self.expireDate,
            'change':      self.change,
            'change_pct':  self.changeRatio,
            'query':       [query_json] * len(self.tickerId)
        }
        self.as_dataframe = pd.DataFrame(self.data_dict)

    def __repr__(self):
        return self.as_dataframe.__repr__()
    
class AMBSLast2Weeks:
    def __init__(self, auctions):
        rows = []

        for auction in auctions:
            base = {
                'auction_status': auction.get('auctionStatus'),
                'operation_id': auction.get('operationId'),
                'operation_date': auction.get('operationDate'),
                'operation_type': auction.get('operationType'),
                'operation_direction': auction.get('operationDirection'),
                'method': auction.get('method'),
                'release_time': auction.get('releaseTime'),
                'close_time': auction.get('closeTime'),
                'class_type': auction.get('classType'),
                'note': auction.get('note'),
                'total_submitted_orig_face': auction.get('totalSubmittedOrigFace'),
                'total_accepted_orig_face': auction.get('totalAcceptedOrigFace'),
                'total_submitted_curr_face': auction.get('totalSubmittedCurrFace'),
                'total_accepted_curr_face': auction.get('totalAcceptedCurrFace'),
                'total_amt_submitted_par': auction.get('totalAmtSubmittedPar'),
                'total_amt_accepted_par': auction.get('totalAmtAcceptedPar'),
                'settlement_date': auction.get('settlementDate'),
                'last_updated': auction.get('lastUpdated'),
            }

            details = auction.get('details', [])
            for detail in details:
                row = base.copy()
                row['security_description'] = detail.get('securityDescription')
                row['cusip'] = detail.get('cusip')
                row['amt_accepted_current'] = detail.get('amtAcceptedCurrent')
                row['amt_accepted_original'] = detail.get('amtAcceptedOriginal')
                rows.append(row)

        self.as_dataframe = pd.DataFrame(rows)





class CentralBankLiquiditySwaps:
    def __init__(self, operations):

        self.operationType = [i.get('operationType') for i in operations]
        self.counterparty = [i.get('counterparty') for i in operations]
        self.currency = [i.get('currency') for i in operations]
        self.tradeDate = [i.get('tradeDate') for i in operations]
        self.settlementDate = [i.get('settlementDate') for i in operations]
        self.maturityDate = [i.get('maturityDate') for i in operations]
        self.termInDays = [i.get('termInDays') for i in operations]
        self.amount = [i.get('amount') for i in operations]
        self.interestRate = [i.get('interestRate') for i in operations]
        self.isSmallValue = [i.get('isSmallValue') for i in operations]
        self.lastUpdated = [i.get('lastUpdated') for i in operations]


        self.data_dict = { 
            'operation_type': self.operationType,
            'counterparty': self.counterparty,
            'currency': self.currency,
            'trade_date': self.tradeDate,
            'settlement_date': self.settlementDate,
            'maturity_date': self.maturityDate,
            'term_in_days': self.termInDays,
            'amount': self.amount,
            'interest_rate': self.interestRate,
            'is_small_value': self.isSmallValue,
            'last_updated': self.lastUpdated
        }


        self.as_dataframe = pd.DataFrame(self.data_dict)



class RepoOperations:
    def __init__(self, data):
        operations = data.get("repo", {}).get("operations", [])
        rows = []

        for op in operations:
            base = {
                "operation_id": op.get("operationId"),
                "auction_status": op.get("auctionStatus"),
                "operation_date": op.get("operationDate"),
                "settlement_date": op.get("settlementDate"),
                "maturity_date": op.get("maturityDate"),
                "operation_type": op.get("operationType"),
                "operation_method": op.get("operationMethod"),
                "settlement_type": op.get("settlementType"),
                "term_calendar_days": op.get("termCalenderDays"),
                "term": op.get("term"),
                "release_time": op.get("releaseTime"),
                "close_time": op.get("closeTime"),
                "note": op.get("note"),
                "last_updated": op.get("lastUpdated"),
                "operation_limit": op.get("operationLimit"),
                "participating_cpty": op.get("participatingCpty"),
                "accepted_cpty": op.get("acceptedCpty"),
                "total_amt_submitted": op.get("totalAmtSubmitted"),
                "total_amt_accepted": op.get("totalAmtAccepted")
            }

            # Flatten details
            details = op.get("details", [])
            for detail in details:
                row = base.copy()
                row["security_type"] = detail.get("securityType")
                row["amt_submitted"] = detail.get("amtSubmitted")
                row["amt_accepted"] = detail.get("amtAccepted")
                row["minimum_bid_rate"] = detail.get("minimumBidRate")
                row["percent_offering_rate"] = detail.get("percentOfferingRate")
                row["percent_award_rate"] = detail.get("percentAwardRate")
                row["percent_high_rate"] = detail.get("percentHighRate")
                row["percent_low_rate"] = detail.get("percentLowRate")
                row["percent_stop_out_rate"] = detail.get("percentStopOutRate")
                row["percent_weighted_average_rate"] = detail.get("percentWeightedAverageRate")
                rows.append(row)

        self.df = pd.DataFrame(rows)

    def to_dataframe(self):
        return self.df
    


class SecuritiesLendingOperations:
    def __init__(self, seclending_data):
        operations = seclending_data.get('seclending', {}).get("operations", [])
        self.rows = []

        for op in operations:
            base = {
                'operation_id': op.get('operationId'),
                'auction_status': op.get('auctionStatus'),
                'operation_type': op.get('operationType'),
                'operation_date': op.get('operationDate'),
                'settlement_date': op.get('settlementDate'),
                'maturity_date': op.get('maturityDate'),
                'release_time': op.get('releaseTime'),
                'close_time': op.get('closeTime'),
                'note': op.get('note'),
                'last_updated': op.get('lastUpdated'),
                'total_par_amt_submitted': op.get('totalParAmtSubmitted'),
                'total_par_amt_accepted': op.get('totalParAmtAccepted'),
            }

            for d in op.get('details', []):
                row = base.copy()
                row.update({
                    'cusip': d.get('cusip'),
                    'security_description': d.get('securityDescription'),
                    'par_amt_submitted': d.get('parAmtSubmitted'),
                    'par_amt_accepted': d.get('parAmtAccepted'),
                    'weighted_average_rate': d.get('weightedAverageRate'),
                    'soma_holdings': d.get('somaHoldings'),
                    'theo_avail_to_borrow': d.get('theoAvailToBorrow'),
                    'actual_avail_to_borrow': d.get('actualAvailToBorrow'),
                    'outstanding_loans': d.get('outstandingLoans'),
                })
                self.rows.append(row)

        self.as_dataframe = pd.DataFrame(self.rows)


class SomaSummary:
    def __init__(self, soma_data):
        records = soma_data.get('soma').get("summary", [])

        # Parse and convert data
        parsed = []
        for row in records:
            parsed.append({
                "as_of_date": row.get("asOfDate"),
                "mbs": float(row.get("mbs", 0) or 0),
                "cmbs": float(row.get("cmbs", 0) or 0),
                "tips": float(row.get("tips", 0) or 0),
                "frn": float(row.get("frn", 0) or 0),
                "tips_inflation_comp": float(row.get("tipsInflationCompensation", 0) or 0),
                "notes_bonds": float(row.get("notesbonds", 0) or 0),
                "bills": float(row.get("bills", 0) or 0),
                "agencies": float(row.get("agencies", 0) or 0),
                "total": float(row.get("total", 0) or 0),
            })

        self.as_dataframe = pd.DataFrame(parsed)



class USBonds:
    def __init__(self, data):
        """Works with both corp_bonds and us_bonds tables."""
        self.tickerId = [int(i.get('tickerId')) if i.get('tickerId') is not None else None for i in data]
        self.symbol = [i.get('symbol') if i.get('symbol') is not None else None for i in data]
        self.isin = [i.get('isin') if i.get('isin') is not None else None for i in data]
        self.type = [i.get('type') if i.get('type') is not None else None for i in data]
        self.fullName = [i.get('fullName') if i.get('fullName') is not None else None for i in data]
        self.name = [i.get('name') if i.get('name') is not None else None for i in data]
        self.expDate = [i.get('expDate') if i.get('expDate') is not None else None for i in data]
        self.treasuryType = [i.get('treasuryType') if i.get('treasuryType') is not None else None for i in data]
        self.treasuryTypeName = [i.get('treasuryTypeName') if i.get('treasuryTypeName') is not None else None for i in data]
        self.parValue = [float(i.get('parValue')) if i.get('parValue') is not None else None for i in data]
        self.coupon = [float(i.get('coupon')) if i.get('coupon') is not None else None for i in data]
        self.accruedInterest = [float(i.get('accruedInterest')) if i.get('accruedInterest') is not None else None for i in data]
        self.couponFrequency = [int(i.get('couponFrequency')) if i.get('couponFrequency') is not None else None for i in data]
        self.couponFreqDesc = [i.get('couponFreqDesc') if i.get('couponFreqDesc') is not None else None for i in data]
        self.term = [i.get('term') if i.get('term') is not None else None for i in data]
        self.close = [float(i.get('close')) if i.get('close') is not None else None for i in data]
        self.change = [float(i.get('change')) if i.get('change') is not None else None for i in data]
        self.changeRatio = [float(i.get('changeRatio')) if i.get('changeRatio') is not None else None for i in data]
        self.bondYield = [float(i.get('bondYield')) if i.get('bondYield') is not None else None for i in data]
        self.yieldYTW = [float(i.get('yieldYTW')) if i.get('yieldYTW') is not None else None for i in data]
        self.askPrice = [float(i.get('askPrice')) if i.get('askPrice') is not None else None for i in data]
        self.bidPrice = [float(i.get('bidPrice')) if i.get('bidPrice') is not None else None for i in data]
        self.askMinSize = [float(i.get('askMinSize')) if i.get('askMinSize') is not None else None for i in data]
        self.bidMinSize = [float(i.get('bidMinSize')) if i.get('bidMinSize') is not None else None for i in data]
        self.askVolume = [float(i.get('askVolume')) if i.get('askVolume') is not None else None for i in data]
        self.bidVolume = [float(i.get('bidVolume')) if i.get('bidVolume') is not None else None for i in data]
        self.askYield = [float(i.get('askYield')) if i.get('askYield') is not None else None for i in data]
        self.askYieldYTW = [float(i.get('askYieldYTW')) if i.get('askYieldYTW') is not None else None for i in data]
        self.bidYield = [float(i.get('bidYield')) if i.get('bidYield') is not None else None for i in data]
        self.bidYieldYTW = [float(i.get('bidYieldYTW')) if i.get('bidYieldYTW') is not None else None for i in data]
        self.duration = [float(i.get('duration')) if i.get('duration') is not None else None for i in data]
        self.convexity = [float(i.get('convexity')) if i.get('convexity') is not None else None for i in data]
        self.issueDate = [i.get('issueDate') if i.get('issueDate') is not None else None for i in data]
        self.issuerName = [i.get('issuerName') if i.get('issuerName') is not None else None for i in data]
        self.isCallable = [i.get('isCallable') if i.get('isCallable') is not None else None for i in data]


        self.data_dict = {
            "ticker_id": self.tickerId,
            "symbol": self.symbol,
            "isin": self.isin,
            "type": self.type,
            "full_name": self.fullName,
            "name": self.name,
            "exp_date": self.expDate,
            "treasury_type": self.treasuryType,
            "treasury_type_name": self.treasuryTypeName,
            "par_value": self.parValue,
            "coupon": self.coupon,
            "accrued_interest": self.accruedInterest,
            "coupon_frequency": self.couponFrequency,
            "coupon_freq_desc": self.couponFreqDesc,
            "term": self.term,
            "close": self.close,
            "change": self.change,
            "change_ratio": self.changeRatio,
            "bond_yield": self.bondYield,
            "yield_ytw": self.yieldYTW,
            "ask_price": self.askPrice,
            "bid_price": self.bidPrice,
            "ask_min_size": self.askMinSize,
            "bid_min_size": self.bidMinSize,
            "ask_volume": self.askVolume,
            "bid_volume": self.bidVolume,
            "ask_yield": self.askYield,
            "ask_yield_ytw": self.askYieldYTW,
            "bid_yield": self.bidYield,
            "bid_yield_ytw": self.bidYieldYTW,
            "duration": self.duration,
            "convexity": self.convexity,
            "issue_date": self.issueDate,
            "issuer_name": self.issuerName,
            "is_callable": self.isCallable,
        }


        self.as_dataframe = pd.DataFrame(self.data_dict)


class FinraShorts:
    def __init__(self, data):
        self.date = [int(i.get("date")) if i.get("date") is not None else None for i in data]
        self.ticker = [i.get("ticker") if i.get("ticker") is not None else None for i in data]
        self.short_volume = [float(i.get("shortVolume")) if i.get("shortVolume") is not None else None for i in data]
        self.short_exempt_volume = [float(i.get("shortExemptVolume")) if i.get("shortExemptVolume") is not None else None for i in data]
        self.total_volume = [float(i.get("totalVolume")) if i.get("totalVolume") is not None else None for i in data]
        self.market = [i.get("market") if i.get("market") is not None else None for i in data]
        self.insertion_timestamp = [pd.Timestamp.utcnow() for _ in data]

        self.data_dict = {
            "date": self.date,
            "ticker": self.ticker,
            "short_volume": self.short_volume,
            "short_exempt_volume": self.short_exempt_volume,
            "total_volume": self.total_volume,
            "market": self.market,
            "insertion_timestamp": self.insertion_timestamp,
        }

        self.as_dataframe = pd.DataFrame(self.data_dict)



class AtmVolAnalTable:
    """
    Holds **ATM options volume and trade breakdown data** for multiple contracts.

    Attributes:
        option_id (list): Option contract IDs.
        ticker (list): Ticker symbols.
        strike (list): Option strike prices.
        call_put (list): Whether the option is a call or put.
        expiry (list): Expiration dates (text).
        total_trades (list): Total number of trades for the contract.
        total_vol (list): Total volume traded.
        avg_price (list): Average price.
        buy_vol (list): Buy-side volume.
        sell_vol (list): Sell-side volume.
        neut_vol (list): Neutral volume.
        ticker_id (list): Internal ticker ID references.
        insertion_timestamp (list): Timestamp of record insertion.
    """
    def __init__(self, data):
        """
        Initialize the AtmVolAnalTable with aggregated ATM option volume and trade breakdowns.

        Args:
            data (list of dict): Raw data rows from the `atm_vol_anal` table.
        """
        self.option_id           = [int(i.get('option_id')) if i.get('option_id') is not None else None for i in data]
        self.ticker              = [i.get('ticker') for i in data]
        self.strike              = [float(i.get('strike')) if i.get('strike') is not None else None for i in data]
        self.call_put            = [i.get('call_put') for i in data]
        self.expiry              = [i.get('expiry') for i in data]
        self.total_trades        = [float(i.get('total_trades')) if i.get('total_trades') is not None else None for i in data]
        self.total_vol           = [float(i.get('total_vol')) if i.get('total_vol') is not None else None for i in data]
        self.avg_price           = [float(i.get('avg_price')) if i.get('avg_price') is not None else None for i in data]
        self.buy_vol             = [float(i.get('buy_vol')) if i.get('buy_vol') is not None else None for i in data]
        self.sell_vol            = [float(i.get('sell_vol')) if i.get('sell_vol') is not None else None for i in data]
        self.neut_vol            = [float(i.get('neut_vol')) if i.get('neut_vol') is not None else None for i in data]
        self.ticker_id           = [float(i.get('ticker_id')) if i.get('ticker_id') is not None else None for i in data]
        self.insertion_timestamp = [i.get('insertion_timestamp') for i in data]

        self.data_dict = {
            'option_id': self.option_id,
            'ticker': self.ticker,
            'strike': self.strike,
            'call_put': self.call_put,
            'expiry': self.expiry,
            'total_trades': self.total_trades,
            'total_vol': self.total_vol,
            'avg_price': self.avg_price,
            'buy_vol': self.buy_vol,
            'sell_vol': self.sell_vol,
            'neut_vol': self.neut_vol,
            'ticker_id': self.ticker_id,
            'insertion_timestamp': self.insertion_timestamp
        }
        self.as_dataframe = pd.DataFrame(self.data_dict)


class AtmOptionsTable:
    """
    Holds detailed at-the-money options data including greeks, pricing, and derived signals.

    Attributes:
        ticker, strike, call_put, expiry: Option identifiers.
        option_symbol, option_id: Contract metadata.
        Pricing, volume, volatility, greeks, activity: Option metrics.
        drima: Proprietary directional risk signal.
    """
    def __init__(self, data):
        self.option_symbol       = [i.get('option_symbol') for i in data]
        self.option_id           = [int(i.get('option_id')) if i.get('option_id') is not None else None for i in data]
        self.ticker_id           = [int(i.get('ticker_id')) if i.get('ticker_id') is not None else None for i in data]
        self.ticker              = [i.get('ticker') for i in data]
        self.strike              = [float(i.get('strike')) if i.get('strike') is not None else None for i in data]
        self.call_put            = [i.get('call_put') for i in data]
        self.expiry              = [i.get('expiry') for i in data]
        self.open                = [float(i.get('open')) if i.get('open') is not None else None for i in data]
        self.high                = [float(i.get('high')) if i.get('high') is not None else None for i in data]
        self.low                 = [float(i.get('low')) if i.get('low') is not None else None for i in data]
        self.close               = [float(i.get('close')) if i.get('close') is not None else None for i in data]
        self.volume              = [float(i.get('volume')) if i.get('volume') is not None else None for i in data]
        self.ask_volume          = [float(i.get('ask_volume')) if i.get('ask_volume') is not None else None for i in data]
        self.bid_volume          = [float(i.get('bid_volume')) if i.get('bid_volume') is not None else None for i in data]
        self.ask_price           = [float(i.get('ask_price')) if i.get('ask_price') is not None else None for i in data]
        self.bid_price           = [float(i.get('bid_price')) if i.get('bid_price') is not None else None for i in data]
        self.oi                  = [float(i.get('oi')) if i.get('oi') is not None else None for i in data]
        self.oi_change           = [float(i.get('oi_change')) if i.get('oi_change') is not None else None for i in data]
        self.trade_time          = [i.get('trade_time') for i in data]
        self.trade_stamp         = [int(i.get('trade_stamp')) if i.get('trade_stamp') is not None else None for i in data]
        self.delta               = [float(i.get('delta')) if i.get('delta') is not None else None for i in data]
        self.gamma               = [float(i.get('gamma')) if i.get('gamma') is not None else None for i in data]
        self.theta               = [float(i.get('theta')) if i.get('theta') is not None else None for i in data]
        self.vega                = [float(i.get('vega')) if i.get('vega') is not None else None for i in data]
        self.rho                 = [float(i.get('rho')) if i.get('rho') is not None else None for i in data]
        self.iv                  = [float(i.get('iv')) if i.get('iv') is not None else None for i in data]
        self.activity            = [float(i.get('activity')) if i.get('activity') is not None else None for i in data]
        self.latest_volume       = [float(i.get('latest_volume')) if i.get('latest_volume') is not None else None for i in data]
        self.change              = [float(i.get('change')) if i.get('change') is not None else None for i in data]
        self.change_pct          = [float(i.get('change_pct')) if i.get('change_pct') is not None else None for i in data]
        self.drima               = [i.get('drima') for i in data]
        self.insertion_timestamp = [i.get('insertion_timestamp') for i in data]

        self.data_dict = {k: getattr(self, k) for k in vars(self) if not k.startswith('_') and k not in ['data_dict', 'as_dataframe']}
        self.as_dataframe = pd.DataFrame(self.data_dict)




class CompanyBoard:
    def __init__(self, board):

        self.companyId = [i.get('companyId') if i.get('companyId') is not None else None for i in board]
        self.name = [i.get('name') if i.get('name') is not None else None for i in board]
        self.title = [i.get('title') if i.get('title') is not None else None for i in board]
        self.sex = [i.get('sex') if i.get('sex') is not None else None for i in board]
        self.modDate = [i.get('modDate') if i.get('modDate') is not None else None for i in board]
        self.age = [int(i.get('age')) if i.get('age') is not None else None for i in board]
        self.totalSalary = [float(i.get('totalSalary')) if i.get('totalSalary') is not None else None for i in board]
        self.education = [i.get('education') if i.get('education') is not None else None for i in board]
        self.rank = [i.get('rank') if i.get('rank') is not None else None for i in board]
        self.biography = [i.get('biography') if i.get('biography') is not None else None for i in board]
        self.isBoard = [i.get('isBoard') if i.get('isBoard') is not None else None for i in board]
        self.isOfficer = [i.get('isOfficer') if i.get('isOfficer') is not None else None for i in board]


        self.data_dict = { 
            'company_id': self.companyId,
            'name': self.name,
            'title': self.title,
            'sex': self.sex,
            'updated_date': self.modDate,
            'age': self.age,
            'total_salary': self.totalSalary,
            'education': self.education,
            'rank': self.rank,
            'biography': self.biography,
            'is_board': self.isBoard,
            'is_officer': self.isOfficer
        }


        self.as_dataframe = pd.DataFrame(self.data_dict)


class CompanyExecutives:
    def __init__(self, executives):

        self.companyId = [i.get('companyId') if i.get('companyId') is not None else None for i in executives]
        self.name = [i.get('name') if i.get('name') is not None else None for i in executives]
        self.title = [i.get('title') if i.get('title') is not None else None for i in executives]
        self.sex = [i.get('sex') if i.get('sex') is not None else None for i in executives]
        self.modDate = [i.get('modDate') if i.get('modDate') is not None else None for i in executives]
        self.age = [i.get('age') if i.get('age') is not None else None for i in executives]
        self.totalSalary = [float(i.get('totalSalary')) if i.get('totalSalary') is not None else None for i in executives]
        self.education = [i.get('education') if i.get('education') is not None else None for i in executives]
        self.rank = [i.get('rank') if i.get('rank') is not None else None for i in executives]
        self.biography = [i.get('biography') if i.get('biography') is not None else None for i in executives]
        self.isBoard = [i.get('isBoard') if i.get('isBoard') is not None else None for i in executives]
        self.isOfficer = [i.get('isOfficer') if i.get('isOfficer') is not None else None for i in executives]


        self.data_dict = { 
            'company_id': self.companyId,
            'name': self.name,
            'title': self.title,
            'sex': self.sex,
            'updated_date': self.modDate,
            'age': self.age,
            'total_salary': self.totalSalary,
            'education': self.education,
            'rank': self.rank,
            'biography': self.biography,
            'is_board': self.isBoard,
            'is_officer': self.isOfficer
        }


        self.as_dataframe = pd.DataFrame(self.data_dict)