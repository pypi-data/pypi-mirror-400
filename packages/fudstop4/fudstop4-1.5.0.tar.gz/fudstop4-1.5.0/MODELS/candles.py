import pandas as pd
import asyncio
import aiohttp
import numpy as np



class Candles:
    def __init__(self):


        # Timespans to fetch
        self.timespans = ['m1', 'd']
        self.timespan_sleep_map = {
            'm1': 0.0,   # possibly no delay
            'm5': 0.05,
            'm15': 0.1,
            'm30': 0.15,
            'm60': 0.2,
            'd': 0.3,
            'w': 0.3,
            'm': 0.3
        }
        # Example: read a CSV that maps ticker -> Webull ID
        self.ticker_df = pd.read_csv('files/ticker_csv.csv')
        self.ticker_to_id_map = dict(zip(self.ticker_df['ticker'], self.ticker_df['id']))
        # Headers needed for Webull
        self.headers = {
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "access_token": "dc_us_tech1.1947846e4d5-6744a616f8644b85b1e3d273e06f982f",
    "app": "global",
    "app-group": "broker",
    "appid": "wb_web_app",
    "device-type": "Web",
    "did": "3uiar5zgvki16rgnpsfca4kyo4scy00a",
    "dnt": "1",
    "hl": "en",
    "origin": "https://app.webull.com",
    "os": "web",
    "osv": "i9zh",
    "platform": "web",
    "priority": "u=1, i",
    "referer": "https://app.webull.com/",
    "reqid": "e9ui2akxdk1xfckga4k11556x5tji_96",
    "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "t_time": "1737087285765",
    "tz": "America/Chicago",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "ver": "5.3.1",
    "x-s": "43a074e7dffdc536c2959edb65527a0f0db0cf0ab142f9fd63b9950aa72a2e6e",
    "x-sv": "xodp2vg9"
}

        # Limit concurrency so we don't overwhelm the API or our system; adjust as needed.
        self.SEM = asyncio.Semaphore(20)

    ###############################################################################
    # 1) Wilder’s RSI
    ###############################################################################
    def compute_wilders_rsi(self, df, window=14):
        """
        Computes Wilder's RSI (iterative smoothing) on a DataFrame assumed sorted ascending by 'ts'.
        Requires a 'c' column for close. Creates an 'RSI' column.
        """
        if len(df) < window:
            df['RSI'] = np.nan
            return df

        # Price change
        df['change'] = df['c'].diff().fillna(0.0)
        df['gain']   = df['change'].clip(lower=0)
        df['loss']   = -df['change'].clip(upper=0)

        # Initialize columns for the Wilder average
        df['avgGain'] = 0.0
        df['avgLoss'] = 0.0

        # First average = simple mean of first 'window' gains/losses
        first_avg_gain = df.loc[:window-1, 'gain'].mean()
        first_avg_loss = df.loc[:window-1, 'loss'].mean()

        df.at[window-1, 'avgGain'] = first_avg_gain
        df.at[window-1, 'avgLoss'] = first_avg_loss

        # Wilder’s smoothing for subsequent rows
        for i in range(window, len(df)):
            df.at[i, 'avgGain'] = ((df.at[i-1, 'avgGain'] * (window - 1)) + df.at[i, 'gain']) / window
            df.at[i, 'avgLoss'] = ((df.at[i-1, 'avgLoss'] * (window - 1)) + df.at[i, 'loss']) / window

        # RSI
        rs = df['avgGain'] / df['avgLoss']
        df['RSI'] = 100 - (100 / (1 + rs))

        # Before we have enough data
        df.loc[:window-1, 'RSI'] = np.nan

        return df

    ###############################################################################
    # 2) MACD and CROSS column (bearish/bullish + "soon")
    ###############################################################################
    def compute_macd(self, df, short_window=12, long_window=26, signal_window=9, epsilon=0.02):
        """
        Computes MACD, Signal, and Histogram on a DataFrame sorted ascending by 'ts'.
        Also adds CROSSOVER:
        - "bullish"  if MACD crosses above signal on this bar,
        - "bearish"  if MACD crosses below signal,
        - "bullish_soon"/"bearish_soon" if near a crossover,
        - "" otherwise.
        """
        # MACD line = EMA(short) - EMA(long)
        ema_short = df['c'].ewm(span=short_window, adjust=False).mean()
        ema_long  = df['c'].ewm(span=long_window,  adjust=False).mean()
        df['MACD'] = ema_short - ema_long

        # Signal line = EMA of MACD
        df['MACD_signal'] = df['MACD'].ewm(span=signal_window, adjust=False).mean()

        # Histogram = MACD - Signal
        df['MACD_hist'] = df['MACD'] - df['MACD_signal']

        # CROSSOVER logic
        df['CROSSOVER'] = ""  # default
        for i in range(1, len(df)):
            prev_diff = df.at[i-1, 'MACD'] - df.at[i-1, 'MACD_signal']
            curr_diff = df.at[i,   'MACD'] - df.at[i,   'MACD_signal']

            # If the sign flips, we have an actual crossover
            if prev_diff < 0 and curr_diff > 0:
                df.at[i, 'CROSSOVER'] = "bullish"
            elif prev_diff > 0 and curr_diff < 0:
                df.at[i, 'CROSSOVER'] = "bearish"
            else:
                # Check if "about to cross" = within epsilon of zero and slope indicates crossing soon
                if abs(curr_diff) < epsilon:
                    slope = curr_diff - prev_diff
                    if curr_diff < 0 and slope > 0:
                        df.at[i, 'CROSSOVER'] = "bullish_soon"
                    elif curr_diff > 0 and slope < 0:
                        df.at[i, 'CROSSOVER'] = "bearish_soon"

        return df

    ###############################################################################
    # 3) TD Sequential (more accurate approach, includes "perfected" checks)
    ###############################################################################
    def compute_td_sequential(self, df):
        """
        Includes:
        - 9-bar setups for BUY/SELL (strictly lower or higher closes vs. 4 bars prior).
        - 'ON_DECK_TD9_BUY/SELL' at count=8, 'CURRENT_TD9_BUY/SELL' at count=9.
        - 'TD9_PERFECTED_BUY/SELL' if bar #9 (or after) trades below the low (for buy)
            or above the high (for sell) of bars #6 or #7.
        - 13-bar countdowns: once a TD9 is established, compare close vs. 2 bars prior;
            if that condition is met, increment the countdown. If it reaches 13 => TD_13_BUY/SELL.
        """
        n = len(df)
        df['ON_DECK_TD9_BUY']   = False
        df['ON_DECK_TD9_SELL']  = False
        df['CURRENT_TD9_BUY']   = False
        df['CURRENT_TD9_SELL']  = False
        df['TD9_PERFECTED_BUY'] = False
        df['TD9_PERFECTED_SELL']= False
        df['TD_13_BUY']         = False
        df['TD_13_SELL']        = False

        buy_setup_count = 0
        sell_setup_count = 0

        # After a TD9 Buy or Sell is established, we track countdown
        buy_countdown = 0
        sell_countdown = 0
        is_buy_countdown_active = False
        is_sell_countdown_active = False

        for i in range(n):
            # 1) TD9 Setup logic
            if i >= 4:
                # BUY setup check
                if df.at[i, 'c'] < df.at[i-4, 'c']:
                    buy_setup_count += 1
                else:
                    buy_setup_count = 0

                # SELL setup check
                if df.at[i, 'c'] > df.at[i-4, 'c']:
                    sell_setup_count += 1
                else:
                    sell_setup_count = 0

                # On-deck at 8
                if buy_setup_count == 8:
                    df.at[i, 'ON_DECK_TD9_BUY'] = True
                if sell_setup_count == 8:
                    df.at[i, 'ON_DECK_TD9_SELL'] = True

                # Current at 9
                if buy_setup_count == 9:
                    df.at[i, 'CURRENT_TD9_BUY'] = True
                    is_buy_countdown_active = True
                    buy_countdown = 0
                if sell_setup_count == 9:
                    df.at[i, 'CURRENT_TD9_SELL'] = True
                    is_sell_countdown_active = True
                    sell_countdown = 0

                # 2) Check for a "perfected" TD9
                if buy_setup_count >= 9:
                    bar6_low = df.at[i-3, 'l'] if (i - 3) >= 0 else np.inf
                    bar7_low = df.at[i-2, 'l'] if (i - 2) >= 0 else np.inf
                    threshold = min(bar6_low, bar7_low)
                    if df.at[i, 'l'] < threshold:
                        df.at[i, 'TD9_PERFECTED_BUY'] = True

                if sell_setup_count >= 9:
                    bar6_high = df.at[i-3, 'h'] if (i - 3) >= 0 else -np.inf
                    bar7_high = df.at[i-2, 'h'] if (i - 2) >= 0 else -np.inf
                    threshold = max(bar6_high, bar7_high)
                    if df.at[i, 'h'] > threshold:
                        df.at[i, 'TD9_PERFECTED_SELL'] = True

            # 3) TD13 Countdown logic
            if i >= 2:
                if is_buy_countdown_active:
                    if df.at[i, 'c'] <= df.at[i-2, 'c']:
                        buy_countdown += 1
                    else:
                        # simplistic approach: reset
                        buy_countdown = 0
                    if buy_countdown == 13:
                        df.at[i, 'TD_13_BUY'] = True
                        is_buy_countdown_active = False

                if is_sell_countdown_active:
                    if df.at[i, 'c'] >= df.at[i-2, 'c']:
                        sell_countdown += 1
                    else:
                        sell_countdown = 0
                    if sell_countdown == 13:
                        df.at[i, 'TD_13_SELL'] = True
                        is_sell_countdown_active = False

        return df

    ###############################################################################
    # 4) Putting it all together: fetch_data_for_timespan()
    ###############################################################################
    async def fetch_data_for_timespan(self,session, ticker, ticker_id, timespan, rsi_window=14):
        """
        Fetches data for a given ticker and timespan, returns a DataFrame with:
        TIMESTAMP, OPEN, HIGH, LOW, CLOSE, VOLUME, VWAP, TICKER, TIMESPAN,
        RSI, MACD, HISTOGRAM, SIGNAL, CROSSOVER,
        ON_DECK_TD9_BUY, ON_DECK_TD9_SELL,
        CURRENT_TD9_BUY, CURRENT_TD9_SELL,
        TD9_PERFECTED_BUY, TD9_PERFECTED_SELL,
        TD_13_BUY, TD_13_SELL.

        Includes dynamic sleep based on the timespan.
        """
        async with self.SEM:
            try:
                url = (
                    f"https://quotes-gw.webullfintech.com/api/quote/charts/query-mini"
                    f"?type={timespan}&count=21&restorationType=1&loadFactor=1&extendTrading=0&tickerId={ticker_id}"
                )
                async with session.get(url, headers=self.headers) as response:
                    data_json = await response.json()

                # If timespan calls for a delay, apply it
                sleep_time = self.timespan_sleep_map.get(timespan, 0.05)

                # Check structure
                if not data_json or not isinstance(data_json, list) or len(data_json) == 0:
                    # If no data or unexpected format
                    await asyncio.sleep(sleep_time)
                    return None

                if 'data' not in data_json[0]:
                    await asyncio.sleep(sleep_time)
                    return None

                raw_data = data_json[0]['data']
                split_data = [row.split(",") for row in raw_data]

                df = pd.DataFrame(
                    split_data,
                    columns=['ts', 'o', 'c', 'h', 'l', 'a', 'v', 'vwap']
                )

                # Convert timestamp
                df['ts'] = pd.to_numeric(df['ts'], errors='coerce')
                df['ts'] = pd.to_datetime(df['ts'], unit='s', utc=True)
                df['ts'] = df['ts'].dt.tz_convert('US/Eastern').dt.tz_localize(None)

                # Reverse to ascending order
                df = df.iloc[::-1].reset_index(drop=True)

                # Convert numeric columns
                for col in ['o', 'c', 'h', 'l', 'v', 'vwap', 'a']:
                    if col in df.columns:
                        df[col] = df[col].replace('null', np.nan).fillna(0).astype(float)

                # Drop 'a' if not needed
                df.drop(columns=['a'], inplace=True, errors='ignore')

                # --- Compute Indicators ---
                df = self.compute_wilders_rsi(df, window=rsi_window)
                df = self.compute_macd(df, short_window=12, long_window=26, signal_window=9, epsilon=0.02)
                df = self.compute_td_sequential(df)

                # Add TICKER, TIMESPAN
                df['ticker']   = ticker
                df['timespan'] = timespan

                # Drop intermediate columns
                to_drop = set(df.columns) & {'change', 'gain', 'loss', 'avgGain', 'avgLoss'}
                df.drop(columns=list(to_drop), inplace=True, errors='ignore')

                # Rename & reorder columns
                df.rename(
                    columns={
                        'ts':         'TIMESTAMP',
                        'o':          'OPEN',
                        'h':          'HIGH',
                        'l':          'LOW',
                        'c':          'CLOSE',
                        'v':          'VOLUME',
                        'vwap':       'VWAP',
                        'ticker':     'TICKER',
                        'timespan':   'TIMESPAN',
                        'MACD_hist':  'HISTOGRAM',
                        'MACD_signal':'SIGNAL'
                    },
                    inplace=True
                )

                final_cols = [
                    'TIMESTAMP', 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME', 'VWAP',
                    'TICKER', 'TIMESPAN', 'RSI', 'MACD', 'HISTOGRAM', 'SIGNAL', 'CROSSOVER',
                    'ON_DECK_TD9_BUY', 'ON_DECK_TD9_SELL',
                    'CURRENT_TD9_BUY', 'CURRENT_TD9_SELL',
                    'TD9_PERFECTED_BUY', 'TD9_PERFECTED_SELL',
                    'TD_13_BUY', 'TD_13_SELL'
                ]
                # Ensure columns exist even if data is too short
                for c in final_cols:
                    if c not in df.columns:
                        df[c] = np.nan
                df = df.reindex(columns=final_cols)

                # Sleep to throttle requests per timespan
                await asyncio.sleep(sleep_time)

                return df

            except Exception as e:
                print(f"fetch_data_for_timespan error on {ticker}, {timespan}: {e}")
                return None

    ###############################################################################
    # 5) Main logic to fetch for ONE ticker (all timespans)
    ###############################################################################
    async def fetch_all_timespans_for_ticker(self,ticker):
        """
        Fetches data for all timespans for a single ticker.
        Returns a dict { timespan: DataFrame }.
        """
        ticker_id = self.ticker_to_id_map.get(ticker, None)
        if not ticker_id:
            # Return an empty dict if not found
            return {}

        async with aiohttp.ClientSession() as session:
            tasks = []
            for ts in self.timespans:
                tasks.append(asyncio.create_task(
                    self.fetch_data_for_timespan(session, ticker, ticker_id, ts, rsi_window=14)
                ))
            results = await asyncio.gather(*tasks)

        out = {}
        for df in results:
            if df is not None and not df.empty:
                out_ts = df['TIMESPAN'].iloc[0]
                out[out_ts] = df
        return out
    
    