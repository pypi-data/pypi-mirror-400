import numpy as np
from numba import njit
import pandas as pd
import sys
from pathlib import Path
import math
from datetime import time
project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)
from scipy.stats import linregress
import aiohttp
import logging
from asyncio import Semaphore, Lock
from typing import Dict,Tuple
import asyncio




def add_parabolic_sar_signals(
    df: pd.DataFrame,
    af_initial: float = 0.23,
    af_max: float = 0.75,
    bb_period: int = 20,
    bb_mult: float = 2.0
) -> pd.DataFrame:
    """
    Compute the Parabolic SAR for each bar, then compare it to Bollinger Bands
    to see if:
      - A 'long' (up) PSAR is below the lower BB.
      - A 'short' (down) PSAR is above the upper BB.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain columns:
            'h': high
            'l': low
            'c': close
        and be sorted in ascending timestamp order.
    af_initial : float
        The initial acceleration factor for the Parabolic SAR.
    af_max : float
        The maximum (acceleration) factor to which AF can increase.
    bb_period : int
        The look-back period for Bollinger Bands (on 'c' by default).
    bb_mult : float
        The standard-deviation multiplier for Bollinger Bands.

    Returns
    -------
    pd.DataFrame
        The original DataFrame with new columns added:
            'psar': the Parabolic SAR value at each bar
            'psar_direction': 'long' or 'short'
            'bb_middle', 'bb_upper', 'bb_lower': Bollinger Band columns
            'psar_long_below_lower_band': boolean
            'psar_short_above_upper_band': boolean

    Notes
    -----
    - This implementation of Parabolic SAR follows Welles Wilder's original
      algorithm. 
    - Bollinger Bands default to 20 bars and 2 std dev, which you can adjust.
    """
    df = df.copy()

    # Safety check: Must have columns h, l, c and be sorted
    required_cols = {'h', 'l', 'c'}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"DataFrame must contain {required_cols} columns.")

    # ─────────────────────────────────────────────────────────────────────────
    # 1) Compute Bollinger Bands on 'close' with rolling mean & std
    # ─────────────────────────────────────────────────────────────────────────
    df["bb_middle"] = df["c"].rolling(bb_period).mean()
    df["bb_std"] = df["c"].rolling(bb_period).std(ddof=0)  # population std
    df["bb_upper"] = df["bb_middle"] + bb_mult * df["bb_std"]
    df["bb_lower"] = df["bb_middle"] - bb_mult * df["bb_std"]

    # ─────────────────────────────────────────────────────────────────────────
    # 2) Compute Parabolic SAR
    #    We'll store the result in df["psar"] and df["psar_direction"].
    # ─────────────────────────────────────────────────────────────────────────
    n = len(df)
    psar = [np.nan] * n
    direction = [None] * n  # 'long' or 'short'
    
    if n < 2:
        # Not enough data to compute a meaningful PSAR
        df["psar"] = psar
        df["psar_direction"] = direction
        return df

    # Initialize the very first PSAR “trend” based on the first two bars:
    # We'll assume that if the second bar's close is higher than the first,
    # we start in an uptrend, else downtrend.
    # Start the PSAR at the first bar's low/high in up/down trend.
    first_bar = 0
    second_bar = 1

    if df.loc[second_bar, "c"] > df.loc[first_bar, "c"]: #type: ignore
        current_direction = "long"
        # Start PSAR at lowest low of first two bars
        psar[first_bar] = df.loc[first_bar, "l"] #type: ignore
        ep = df.loc[first_bar:second_bar, "h"].max()  # highest high so far
    else:
        current_direction = "short"
        # Start PSAR at highest high of first two bars
        psar[first_bar] = df.loc[first_bar, "h"] #type: ignore
        ep = df.loc[first_bar:second_bar, "l"].min()  # lowest low so far

    # For the second bar, we must still finalize the initial PSAR.
    psar[second_bar] = psar[first_bar]
    af = af_initial  # acceleration factor

    direction[first_bar] = current_direction #type: ignore
    direction[second_bar] = current_direction #type: ignore

    # Main loop for bars 2..n-1
    for i in range(2, n):
        prev_psar = psar[i - 1]
        prev_dir = direction[i - 1]

        if prev_dir == "long":
            # Tentative next PSAR:
            new_psar = prev_psar + af * (ep - prev_psar) #type: ignore
            # SAR cannot exceed the last two lows in an uptrend
            new_psar = min(
                new_psar, #type: ignore
                df.loc[i - 1, "l"], #type: ignore
                df.loc[i - 2, "l"] if i - 2 >= 0 else df.loc[i - 1, "l"] #type: ignore
            )

            # Check if we continue or flip direction
            if df.loc[i, "l"] > new_psar:
                # Still in uptrend
                current_direction = "long"
                psar[i] = new_psar
                # Update EP if we made a new high
                if df.loc[i, "h"] > ep: #type: ignore
                    ep = df.loc[i, "h"]
                    af = min(af + af_initial, af_max)
            else:
                # Flip to downtrend
                current_direction = "short"
                psar[i] = ep  #type: ignore
                ep = df.loc[i, "l"]  # reset EP to this bar's low
                af = af_initial  # reset AF
        else:
            # short
            new_psar = prev_psar - af * (prev_psar - ep) #type: ignore
            # SAR cannot be lower than the last two highs in a downtrend
            new_psar = max(
                new_psar, #type: ignore
                df.loc[i - 1, "h"], #type: ignore
                df.loc[i - 2, "h"] if i - 2 >= 0 else df.loc[i - 1, "h"] #type: ignore
            )

            # Check if we continue or flip direction
            if df.loc[i, "h"] < new_psar:
                # Still in downtrend
                current_direction = "short"
                psar[i] = new_psar
                # Update EP if we made a new low
                if df.loc[i, "l"] < ep: #type: ignore
                    ep = df.loc[i, "l"]
                    af = min(af + af_initial, af_max)
            else:
                # Flip to uptrend
                current_direction = "long"
                psar[i] = ep  #type: ignore
                ep = df.loc[i, "h"]  # reset EP to this bar's high
                af = af_initial  # reset AF

        direction[i] = current_direction #type: ignore

    df["psar"] = psar
    df["psar_direction"] = direction

    # ─────────────────────────────────────────────────────────────────────────
    # 3) Identify where PSAR-long is below the lower BB, 
    #    or PSAR-short is above the upper BB
    # ─────────────────────────────────────────────────────────────────────────
    # Safety: Bollinger columns may have NaN in the first ~bb_period rows.
    df["psar_long_below_lower_band"] = (
        (df["psar_direction"] == "long") &
        (df["psar"] < df["bb_lower"])
    )
    
    df["psar_short_above_upper_band"] = (
        (df["psar_direction"] == "short") &
        (df["psar"] > df["bb_upper"])
    )

    # Cleanup: optional drop of the 'bb_std' intermediate column
    df.drop(columns=["bb_std"], inplace=True)

    return df

def compute_volume_profile(df_intraday, num_bins=100):
    """
    Compute POC, VAH, VAL from intraday data using a simple volume profile approach.
    Args:
        df_intraday: DataFrame with columns [open, high, low, close, volume].
                     All rows must be from the SAME period (e.g. the same day or same week).
        num_bins:    How many price bins to use for the volume distribution.
    Returns:
        (poc, vah, val) for the given period.
    """

    # 1) Determine the price range for this period
    period_low = df_intraday['l'].min()
    period_high = df_intraday['h'].max()
    total_volume = df_intraday['v'].sum()

    if period_low == period_high:
        # Edge case: no price range
        return (period_low, period_low, period_low)

    # 2) Create price bins
    bin_edges = np.linspace(period_low, period_high, num_bins + 1)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2.0
    volume_profile = np.zeros(num_bins)

    # 3) Distribute volume across bins
    for idx, row in df_intraday.iterrows():
        bar_low = row['l']
        bar_high = row['h']
        bar_volume = row['v']

        # Simple approach: add this bar's volume to the bin closest to the bar's "mid" price
        bar_mid = (bar_low + bar_high) / 2.0
        closest_bin = np.argmin(np.abs(bin_centers - bar_mid))
        volume_profile[closest_bin] += bar_volume

        # Alternatively, do something more advanced: distribute proportionally from low->high
        # This would require a bit more looping or interpolation.

    # 4) Find the Point of Control (POC): bin with highest volume
    poc_index = np.argmax(volume_profile)
    poc_price = bin_centers[poc_index]

    # 5) Identify Value Area: we want ~70% of total volume around the POC
    # Start from the poc bin, expand up/down until we capture ~70% of volume.
    cum_volume = volume_profile[poc_index]
    lower_idx = poc_index
    upper_idx = poc_index

    # The fraction of total volume we want:
    target_volume = 0.70 * total_volume

    # Expand outwards
    while cum_volume < target_volume:
        # Expand either up or down depending on which side has more volume.
        move_lower = False
        move_upper = False

        # Check if we can move down
        if lower_idx > 0:
            down_vol = volume_profile[lower_idx - 1]
        else:
            down_vol = -1  # can't move lower

        # Check if we can move up
        if upper_idx < num_bins - 1:
            up_vol = volume_profile[upper_idx + 1]
        else:
            up_vol = -1  # can't move higher

        if down_vol > up_vol:
            move_lower = True
        else:
            move_upper = True

        if move_lower and lower_idx > 0:
            lower_idx -= 1
            cum_volume += volume_profile[lower_idx]
        elif move_upper and upper_idx < num_bins - 1:
            upper_idx += 1
            cum_volume += volume_profile[upper_idx]
        else:
            # We can't expand any further
            break

    vah_price = bin_centers[upper_idx]
    val_price = bin_centers[lower_idx]

    return (poc_price, vah_price, val_price)

def add_td9_counts(df: pd.DataFrame) -> pd.DataFrame: #type: ignore
    """
    Adds two columns:
      - td_buy_count: increments if c < c[i-4], else reset to 0
      - td_sell_count: increments if c > c[i-4], else reset to 0
    Continues beyond 9 indefinitely.
    """
    df = df.copy()
    df['td_buy_count'] = 0
    df['td_sell_count'] = 0

    for i in range(len(df)):
        if i < 4:
            continue  # Not enough bars to look back 4
        c_now = df.at[df.index[i], 'c']
        c_4_ago = df.at[df.index[i - 4], 'c']

        # BUY condition
        if c_now < c_4_ago:
            prev_buy = df.at[df.index[i - 1], 'td_buy_count']
            df.at[df.index[i], 'td_buy_count'] = prev_buy + 1 if prev_buy > 0 else 1
        else:
            df.at[df.index[i], 'td_buy_count'] = 0

        # SELL condition
        if c_now > c_4_ago:
            prev_sell = df.at[df.index[i - 1], 'td_sell_count']
            df.at[df.index[i], 'td_sell_count'] = prev_sell + 1 if prev_sell > 0 else 1
        else:
            df.at[df.index[i], 'td_sell_count'] = 0

    return df



# ============================================================================
# OTHER TECHNICAL INDICATORS
# ============================================================================

def compute_bollinger_bands(df: pd.DataFrame, window: int = 20, num_std: float = 2) -> pd.DataFrame:
    """
    Compute Bollinger Bands for the 'c' (close) column.
    Adds columns: 'bb_mid', 'bb_upper', 'bb_lower'
    """
    rolling_mean = df['c'].rolling(window).mean()
    rolling_std = df['c'].rolling(window).std()

    df['bb_mid'] = rolling_mean
    df['bb_upper'] = rolling_mean + (rolling_std * num_std)
    df['bb_lower'] = rolling_mean - (rolling_std * num_std)
    return df

def compute_stochastic_oscillator(df: pd.DataFrame, k_window: int = 14, d_window: int = 3) -> pd.DataFrame:
    """
    Compute the Stochastic Oscillator (%K and %D).
    Adds columns: 'stoch_k', 'stoch_d'
    """
    low_min = df['l'].rolling(window=k_window).min()
    high_max = df['h'].rolling(window=k_window).max()

    df['stoch_k'] = ((df['c'] - low_min) / (high_max - low_min)) * 100
    df['stoch_d'] = df['stoch_k'].rolling(window=d_window).mean()
    return df

def compute_atr(df: pd.DataFrame, window: int = 14) -> pd.DataFrame:
    """
    Compute the Average True Range (ATR).
    Adds column: 'atr'
    """
    # True Range
    df['h-l'] = df['h'] - df['l']
    df['h-pc'] = abs(df['h'] - df['c'].shift(1))
    df['l-pc'] = abs(df['l'] - df['c'].shift(1))

    tr = df[['h-l', 'h-pc', 'l-pc']].max(axis=1)
    df['atr'] = tr.rolling(window).mean()

    # Clean up intermediate columns if desired
    df.drop(['h-l','h-pc','l-pc'], axis=1, inplace=True)
    return df

def compute_supertrend(df: pd.DataFrame, atr_multiplier: float = 3.0, atr_period: int = 10) -> pd.DataFrame:
    """
    Compute the Supertrend indicator.
    Adds columns: 'supertrend', 'supertrend_direction'
    """
    # First compute ATR if not present
    if 'atr' not in df.columns:
        df = compute_atr(df, atr_period)
    
    # Basic upper band & lower band
    hl2 = (df['h'] + df['l']) / 2
    df['basic_ub'] = hl2 + (atr_multiplier * df['atr'])
    df['basic_lb'] = hl2 - (atr_multiplier * df['atr'])

    # Initialize final bands
    df['final_ub'] = df['basic_ub']
    df['final_lb'] = df['basic_lb']

    for i in range(1, len(df)):
        # Final upper band
        if (df['basic_ub'].iloc[i] < df['final_ub'].iloc[i-1]) or (df['c'].iloc[i-1] > df['final_ub'].iloc[i-1]):
            df.at[i, 'final_ub'] = df['basic_ub'].iloc[i]
        else:
            df.at[i, 'final_ub'] = df['final_ub'].iloc[i-1]

        # Final lower band
        if (df['basic_lb'].iloc[i] > df['final_lb'].iloc[i-1]) or (df['c'].iloc[i-1] < df['final_lb'].iloc[i-1]):
            df.at[i, 'final_lb'] = df['basic_lb'].iloc[i]
        else:
            df.at[i, 'final_lb'] = df['final_lb'].iloc[i-1]

    # SuperTrend
    df['supertrend'] = 0.0
    df['supertrend_direction'] = 1

    for i in range(1, len(df)):
        if (df['c'].iloc[i] <= df['final_ub'].iloc[i]):
            df.at[i, 'supertrend'] = df['final_ub'].iloc[i]
            df.at[i, 'supertrend_direction'] = -1
        else:
            df.at[i, 'supertrend'] = df['final_lb'].iloc[i]
            df.at[i, 'supertrend_direction'] = 1
    
    # Optional: drop intermediate columns
    df.drop(['basic_ub','basic_lb','final_ub','final_lb'], axis=1, inplace=True)
    return df


def compute_adx(df: pd.DataFrame, window: int = 14) -> pd.DataFrame:
    """
    Compute the Average Directional Index (ADX).
    Adds columns: '+DI', '-DI', 'adx'.
    """
    # Ensure ATR is computed
    if 'atr' not in df.columns:
        df = compute_atr(df, window)

    # Directional movements
    df['up_move'] = df['h'] - df['h'].shift(1)
    df['down_move'] = df['l'].shift(1) - df['l']

    # +DM and -DM
    df['+DM'] = np.where((df['up_move'] > df['down_move']) & (df['up_move'] > 0), df['up_move'], 0.0)
    df['-DM'] = np.where((df['down_move'] > df['up_move']) & (df['down_move'] > 0), df['down_move'], 0.0)

    # Smooth +DM, -DM
    df['+DM_ema'] = df['+DM'].ewm(alpha=1/window, adjust=False).mean()
    df['-DM_ema'] = df['-DM'].ewm(alpha=1/window, adjust=False).mean()

    # +DI, -DI
    df['+DI'] = (df['+DM_ema'] / df['atr']) * 100
    df['-DI'] = (df['-DM_ema'] / df['atr']) * 100

    # DX
    df['dx'] = (abs(df['+DI'] - df['-DI']) / (df['+DI'] + df['-DI'])) * 100

    # ADX
    df['adx'] = df['dx'].ewm(alpha=1/window, adjust=False).mean()

    # Clean up intermediate columns if desired
    df.drop(['up_move','down_move','+DM','-DM','+DM_ema','-DM_ema','dx'], axis=1, inplace=True)
    return df

def compute_trend(
    series: pd.Series, 
    threshold: float = 0.001, 
    window: int = 5
) -> str:
    """
    Purpose:
        Compute the trend of the final window candles in a time series.
        
    Method:
      - Assumes the incoming series is in *descending* order (most recent first).
      - Reverses to chronological order (oldest -> newest).
      - Takes the last window points to compute a linear regression slope.
      - Divides slope by mean of that subset to get a 'relative slope'.
      - Compares that relative slope to a threshold to label the trend as
        "increasing", "decreasing", or "flattening".

    Returns:
        str: "increasing", "decreasing", or "flattening".

    Notes:
      - If there's insufficient data (< 2 points), returns "flattening".
      - If linregress fails for any reason, returns "flattening".
    """
    chronological_data = series.iloc[::-1].copy()  # flip descending -> ascending
    recent_subset = chronological_data.iloc[-window:]
    
    if len(recent_subset) < 2:
        return "flattening"
    
    x = np.arange(len(recent_subset))
    try:
        result = linregress(x, recent_subset.values)
        slope = result.slope #type: ignore
    except Exception:
        return "flattening"
    
    mean_val = recent_subset.mean()
    relative_slope = slope / mean_val if mean_val != 0 else 0
    
    if relative_slope > threshold:
        return "increasing"
    elif relative_slope < -threshold:
        return "decreasing"
    else:
        return "flattening"

def compute_angle(series: pd.Series) -> float:
    """
    Purpose:
        Compute the angle (in degrees) from a *descending*-order Series
        via linear regression over the entire Series.

    Method:
      1. Reverse the Series so it's chronological (oldest -> newest).
      2. Perform linear regression to get slope.
      3. Convert slope -> angle_radians = atan(slope).
         - Standard geometry: slope=0 => angle=0° from x-axis.
      4. Then 'invert' it so slope=0 => angle=180°:
         angle_degrees = degrees(angle_radians)
         adjusted_angle = 180 - angle_degrees

         => Up slope => angle_degrees > 0 => adjusted_angle < 180
         => Down slope => angle_degrees < 0 => adjusted_angle > 180

    Returns:
        float: the adjusted angle in degrees.

    Notes:
      - If there's insufficient data (< 2 points) or an error, returns 0.0
      - By design, slope=0 => 180°, purely for a custom reference frame.
    """
    chronological_data = series.iloc[::-1].copy()
    
    if len(chronological_data) < 2:
        return 0.0
    
    x = np.arange(len(chronological_data))
    y = chronological_data.values
    
    try:
        result = linregress(x, y)
        slope = result.slope #type: ignore
    except Exception:
        return 0.0
    
    angle_radians = math.atan(slope)         # slope=0 => 0 rad => 0 deg
    angle_degrees = math.degrees(angle_radians)
    
    # 'Invert' so that slope=0 => 180 deg instead of 0 deg
    adjusted_angle = 180.0 - angle_degrees
    return adjusted_angle

def compute_relative_angle(
    band_series: pd.Series,
    price_series: pd.Series,
    points: int = 4
) -> float:
    """
    Purpose:
        Compute the short-window *relative angle* between a Bollinger Band series
        and the price (candle close) series, both in descending order.

    Steps:
      1. Take last points bars from each (descending).
      2. Reverse them to chronological for linear regression.
      3. Compute slopes for band and price.
      4. Convert each slope -> 'adjusted' angle, i.e. slope=0 => 180°.
      5. Return (angle_band - angle_price).

    Interpretation:
      - Because a *larger slope* => *smaller* adjusted angle
        (since angle=180 - degrees(atan(slope))),
        the difference (angle_band - angle_price) will be:
         • Negative if band is sloping up more than price (band slope bigger).
         • Positive if band is sloping down more than price (band slope smaller).

      This is the **opposite** of what's stated in the docstring comment that 
      “A positive result means the band is angled 'up' more.” 
      Actually, the code as written yields:
         - band slope > price slope => band angle < price angle => difference < 0
         => negative
      So if you truly want “positive => band is angled up more,” 
      then you should invert the final line to:

          return (angle_price_deg - angle_band_deg)

      or update your docstring interpretation accordingly.

    Returns:
        float: difference in adjusted angles (angle_band - angle_price).

    Notes:
      - If there's insufficient data, returns 0.0
      - points must be <= length of each series or we default to 0.0
    """
    if len(band_series) < points or len(price_series) < points:
        return 0.0

    # Descending slices
    band_desc = band_series.head(points).copy()
    price_desc = price_series.head(points).copy()

    # Reverse to chronological
    band_chron = band_desc.iloc[::-1].values
    price_chron = price_desc.iloc[::-1].values
    
    x = np.arange(points)
    
    try:
        slope_band = linregress(x, band_chron).slope #type: ignore
        slope_price = linregress(x, price_chron).slope #type: ignore
    except Exception:
        return 0.0
    
    # Convert slopes -> 'adjusted' angles
    angle_band_deg = 180.0 - math.degrees(math.atan(slope_band))
    angle_price_deg = 180.0 - math.degrees(math.atan(slope_price))

    # Return difference
    # NOTE: This means bigger slope (band) => smaller angle => negative difference
    relative_angle = angle_band_deg - angle_price_deg
    return relative_angle


def add_bollinger_bands(
    df: pd.DataFrame,
    window: int = 20,
    num_std: float = 2,
    trend_points: int = 13
) -> pd.DataFrame:
    """
    Adds Bollinger bands (middle, upper, lower) to a DataFrame based on the 'c' column (close prices).
    Additionally, computes the trend for the upper and lower bands using the last `trend_points` values.
    
    The computation is performed on the data sorted in ascending (chronological) order,
    then merged back into the original DataFrame. Finally, the DataFrame is re-sorted
    in descending order (newest first), and the computed trends are assigned only to the
    first (newest) row as new columns 'upper_bb_trend' and 'lower_bb_trend'.
    
    For the upper band:
        - "increasing" becomes "upper_increasing"
        - "decreasing" becomes "upper_decreasing"
    For the lower band:
        - "increasing" becomes "lower_increasing"
        - "decreasing" becomes "lower_decreasing"
    If the computed trend is "flattening" for either band, the flag is "flattening".
    
    Additionally:
      - 'candle_above_upper': True if the candle's high (or close if no 'h' column) exceeds the upper band.
      - 'candle_below_lower': True if the candle's low (or close if no 'l' column) falls below the lower band.
    
    FLAGS:
      - 'candle_completely_above_upper': True if the ENTIRE candle is above the upper band
                                         (i.e., candle low > upper band).
      - 'candle_partially_above_upper':  True if the candle's high is above the upper band
                                         but the low is NOT strictly above it.
      - 'candle_completely_below_lower': True if the ENTIRE candle is below the lower band
                                         (i.e., candle high < lower band).
      - 'candle_partially_below_lower':  True if the candle's low is below the lower band
                                         but the high is NOT strictly below it.

    IMPORTANT BEHAVIOR (fix for live candle false-positives):
      - 'candle_completely_above_upper' and 'candle_completely_below_lower' are shifted by 1 candle
        so the newest row reflects the previous candle’s fully-closed state. This prevents the
        in-progress candle from triggering "completely" flags mid-interval.
    
    Parameters:
        df (pd.DataFrame): DataFrame with at least columns "ts" (timestamp) and "c" (close price).
                           Optionally, it may include "h" (high) and "l" (low) for full candle data.
        window (int): Window size for rolling mean and std.
        num_std (float): Number of standard deviations for the upper/lower bands.
        trend_points (int): Number of rows to use for computing the trend.
        
    Returns:
        pd.DataFrame: DataFrame with added Bollinger bands, trend columns, and candle flags.
    """
    # Work on a copy sorted in ascending order (oldest first) so that rolling works properly.
    try:
        df_sorted = df.copy().sort_values("ts").reset_index(drop=True)
        
        # Calculate the rolling statistics.
        df_sorted["middle_band"] = df_sorted["c"].rolling(window=window, min_periods=window).mean()
        df_sorted["std"] = df_sorted["c"].rolling(window=window, min_periods=window).std()
        df_sorted["upper_band"] = df_sorted["middle_band"] + (num_std * df_sorted["std"])
        df_sorted["lower_band"] = df_sorted["middle_band"] - (num_std * df_sorted["std"])
        
        # Merge the calculated bands back into the original DataFrame based on timestamp.
        df = df.merge(
            df_sorted[["ts", "middle_band", "upper_band", "lower_band"]],
            on="ts",
            how="left"
        )
        
        # Sort descending so that the first row is the most recent.
        df = df.sort_values("ts", ascending=False).reset_index(drop=True)
        
        # Initialize trend columns.
        df["upper_bb_trend"] = pd.Series([None] * len(df), dtype="object")
        df["lower_bb_trend"] = pd.Series([None] * len(df), dtype="object")
        
        # Only compute trends if there are at least 'trend_points' rows.
        if len(df) >= trend_points:
            # Use the most recent `trend_points` rows.
            subset_upper = df["upper_band"].head(trend_points)
            subset_lower = df["lower_band"].head(trend_points)
            
            # Compute trends.
            upper_trend = compute_trend(subset_upper)
            lower_trend = compute_trend(subset_lower)
            
            # Assign prefixed trend values.
            if upper_trend == "increasing":
                df.at[0, "upper_bb_trend"] = "upper_increasing"
            elif upper_trend == "decreasing":
                df.at[0, "upper_bb_trend"] = "upper_decreasing"
            else:
                df.at[0, "upper_bb_trend"] = "flattening"
            
            if lower_trend == "increasing":
                df.at[0, "lower_bb_trend"] = "lower_increasing"
            elif lower_trend == "decreasing":
                df.at[0, "lower_bb_trend"] = "lower_decreasing"
            else:
                df.at[0, "lower_bb_trend"] = "flattening"
        else:
            # If there's not enough data to compute the trend, default to flattening.
            df.at[0, "upper_bb_trend"] = "flattening"
            df.at[0, "lower_bb_trend"] = "flattening"
        
        # Existing flags: candle_above_upper, candle_below_lower
        # If available, use 'h' and 'l'. Otherwise, fallback to 'c'.
        if {"h", "l"}.issubset(df.columns):
            df["candle_above_upper"] = df["h"] > df["upper_band"]
            df["candle_below_lower"] = df["l"] < df["lower_band"]
        else:
            df["candle_above_upper"] = df["c"] > df["upper_band"]
            df["candle_below_lower"] = df["c"] < df["lower_band"]
        
        # NEW FLAGS: completely above/below, partially above/below
        df["candle_completely_above_upper"] = False
        df["candle_partially_above_upper"] = False
        df["candle_completely_below_lower"] = False
        df["candle_partially_below_lower"] = False
        
        if {"h", "l"}.issubset(df.columns):
            # COMPLETELY ABOVE: l > upper_band
            df.loc[df["l"] > df["upper_band"], "candle_completely_above_upper"] = True
            
            # PARTIALLY ABOVE: h > upper_band but l <= upper_band
            df.loc[
                (df["h"] > df["upper_band"]) & (df["l"] <= df["upper_band"]),
                "candle_partially_above_upper"
            ] = True
            
            # COMPLETELY BELOW: h < lower_band
            df.loc[df["h"] < df["lower_band"], "candle_completely_below_lower"] = True
            
            # PARTIALLY BELOW: l < lower_band but h >= lower_band
            df.loc[
                (df["l"] < df["lower_band"]) & (df["h"] >= df["lower_band"]),
                "candle_partially_below_lower"
            ] = True
        else:
            # Fallback for data lacking 'h'/'l' columns (single price per row).
            # COMPLETELY ABOVE: c > upper_band
            df.loc[df["c"] > df["upper_band"], "candle_completely_above_upper"] = True
            
            # COMPLETELY BELOW: c < lower_band
            df.loc[df["c"] < df["lower_band"], "candle_completely_below_lower"] = True
            # partial flags remain False in this fallback scenario.

        # ── FIX: Use the PREVIOUS candle's "completely above/below" status ──
        # Data is sorted newest first, so shift(-1) pulls the previous candle (index+1) onto the current row.
        df["candle_completely_above_upper"] = (
            df["candle_completely_above_upper"].shift(-1, fill_value=False)
        )
        df["candle_completely_below_lower"] = (
            df["candle_completely_below_lower"].shift(-1, fill_value=False)
        )
        
        return df
    except Exception as e:
        print(f"{e}")

def _prep_indicator_df(df: pd.DataFrame) -> Tuple[pd.DataFrame, bool]:
    """
    Return a copy sorted by ts (if present) and a flag for order restoration.
    """
    df = df.copy()
    if "ts" in df.columns:
        df["__orig_order"] = np.arange(len(df))
        df = df.sort_values("ts")
        return df, True
    return df, False

def _restore_indicator_df(df: pd.DataFrame, restore: bool) -> pd.DataFrame:
    if restore:
        df = df.sort_values("__orig_order")
        df.drop(columns=["__orig_order"], inplace=True)
    return df

def _true_range(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
    prev_close = close.shift(1)
    return pd.concat(
        [
            (high - low).abs(),
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1
    ).max(axis=1)

def _wilder_smooth(series: pd.Series, window: int) -> pd.Series:
    if window <= 1:
        return series
    smoothed = series.rolling(window=window, min_periods=window).mean()
    values = smoothed.to_numpy()
    raw = series.to_numpy()
    for i in range(window, len(values)):
        prev_val = values[i - 1]
        if np.isnan(prev_val):
            continue
        values[i] = (prev_val * (window - 1) + raw[i]) / window
    return pd.Series(values, index=series.index)

def add_atr(df: pd.DataFrame, window: int = 14) -> pd.DataFrame:
    """
    Adds Average True Range (ATR) using Wilder's smoothing.
    """
    df, restore = _prep_indicator_df(df)

    high = df["h"].astype(float)
    low = df["l"].astype(float)
    close = df["c"].astype(float)
    tr = _true_range(high, low, close)
    df["atr"] = _wilder_smooth(tr, window)

    df = _restore_indicator_df(df, restore)
    return df


def add_stochastic_oscillator(df, window=14, smooth_window=3):
    """
    Adds the Stochastic Oscillator (%K and %D) to the dataframe.
    %K = 100 * (close - lowest low) / (highest high - lowest low)
    %D = Simple moving average of %K over 'smooth_window' periods.
    """
    df['lowest_low'] = df['l'].rolling(window=window).min()
    df['highest_high'] = df['h'].rolling(window=window).max()
    df['stoch_k'] = 100 * (df['c'] - df['lowest_low']) / (df['highest_high'] - df['lowest_low'])
    df['stoch_d'] = df['stoch_k'].rolling(window=smooth_window).mean()
    df.drop(columns=['lowest_low', 'highest_high'], inplace=True)
    return df


def add_cci(df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    """
    Adds the Commodity Channel Index (CCI).
    """
    df, restore = _prep_indicator_df(df)

    tp = (df["h"] + df["l"] + df["c"]) / 3.0
    tp_ma = tp.rolling(window=window, min_periods=window).mean()
    mean_dev = tp.rolling(window=window, min_periods=window).apply(
        lambda x: np.mean(np.abs(x - x.mean())),
        raw=True
    )
    denom = 0.015 * mean_dev.replace(0, np.nan)
    df["cci"] = (tp - tp_ma) / denom

    df = _restore_indicator_df(df, restore)
    return df

def add_williams_r(df: pd.DataFrame, window: int = 14) -> pd.DataFrame:
    """
    Adds Williams %R.
    """
    df, restore = _prep_indicator_df(df)

    highest_high = df["h"].rolling(window=window, min_periods=window).max()
    lowest_low = df["l"].rolling(window=window, min_periods=window).min()
    range_ = (highest_high - lowest_low).replace(0, np.nan)
    df["williams_r"] = -100.0 * (highest_high - df["c"]) / range_

    df = _restore_indicator_df(df, restore)
    return df

def add_mfi(df: pd.DataFrame, window: int = 14) -> pd.DataFrame:
    """
    Adds Money Flow Index (MFI).
    """
    df, restore = _prep_indicator_df(df)

    tp = (df["h"] + df["l"] + df["c"]) / 3.0
    raw_money_flow = tp * df["v"]
    tp_diff = tp.diff()

    positive_flow = raw_money_flow.where(tp_diff > 0, 0.0)
    negative_flow = raw_money_flow.where(tp_diff < 0, 0.0)

    pos_sum = positive_flow.rolling(window=window, min_periods=window).sum()
    neg_sum = negative_flow.rolling(window=window, min_periods=window).sum()

    money_flow_ratio = pos_sum / neg_sum.replace(0, np.nan)
    mfi = 100.0 - (100.0 / (1.0 + money_flow_ratio))
    mfi = mfi.mask((neg_sum == 0) & (pos_sum > 0), 100.0)
    mfi = mfi.mask((pos_sum == 0) & (neg_sum > 0), 0.0)

    df["mfi"] = mfi

    df = _restore_indicator_df(df, restore)
    return df

def add_roc(df: pd.DataFrame, window: int = 12) -> pd.DataFrame:
    """
    Adds Rate of Change (ROC) in percent.
    """
    df, restore = _prep_indicator_df(df)

    shifted = df["c"].shift(window)
    denom = shifted.replace(0, np.nan)
    df["roc"] = ((df["c"] - shifted) / denom) * 100.0

    df = _restore_indicator_df(df, restore)
    return df

def add_donchian_channels(df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    """
    Adds Donchian channel upper/lower/middle bands.
    """
    df, restore = _prep_indicator_df(df)

    upper = df["h"].rolling(window=window, min_periods=window).max()
    lower = df["l"].rolling(window=window, min_periods=window).min()
    df["donchian_upper"] = upper
    df["donchian_lower"] = lower
    df["donchian_middle"] = (upper + lower) / 2.0

    df = _restore_indicator_df(df, restore)
    return df

def add_keltner_channels(
    df: pd.DataFrame,
    window: int = 20,
    atr_window: int = 10,
    atr_multiplier: float = 2.0,
    use_typical_price: bool = True,
    use_ema: bool = True
) -> pd.DataFrame:
    """
    Adds Keltner channel middle/upper/lower bands.
    """
    df, restore = _prep_indicator_df(df)

    price = (df["h"] + df["l"] + df["c"]) / 3.0 if use_typical_price else df["c"]
    if use_ema:
        middle = price.ewm(span=window, adjust=False, min_periods=window).mean()
    else:
        middle = price.rolling(window=window, min_periods=window).mean()

    tr = _true_range(df["h"], df["l"], df["c"])
    atr = _wilder_smooth(tr, atr_window)

    df["keltner_middle"] = middle
    df["keltner_upper"] = middle + (atr_multiplier * atr)
    df["keltner_lower"] = middle - (atr_multiplier * atr)

    df = _restore_indicator_df(df, restore)
    return df

def add_chaikin_money_flow(df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    """
    Adds Chaikin Money Flow (CMF).
    """
    df, restore = _prep_indicator_df(df)

    high = df["h"]
    low = df["l"]
    close = df["c"]
    volume = df["v"]

    price_range = (high - low).replace(0, np.nan)
    mfm = ((close - low) - (high - close)) / price_range
    mfm = mfm.fillna(0.0)
    mfv = mfm * volume

    mfv_sum = mfv.rolling(window=window, min_periods=window).sum()
    vol_sum = volume.rolling(window=window, min_periods=window).sum().replace(0, np.nan)
    df["cmf"] = mfv_sum / vol_sum

    df = _restore_indicator_df(df, restore)
    return df

def add_accumulation_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds Accumulation/Distribution Line (ADL).
    """
    df, restore = _prep_indicator_df(df)

    high = df["h"]
    low = df["l"]
    close = df["c"]
    volume = df["v"]

    price_range = (high - low).replace(0, np.nan)
    mfm = ((close - low) - (high - close)) / price_range
    mfm = mfm.fillna(0.0)
    df["adl"] = (mfm * volume).cumsum()

    df = _restore_indicator_df(df, restore)
    return df

def add_aroon(df: pd.DataFrame, window: int = 25) -> pd.DataFrame:
    """
    Adds Aroon Up/Down and Aroon Oscillator.
    """
    df, restore = _prep_indicator_df(df)

    periods_since_high = df["h"].rolling(window=window, min_periods=window).apply(
        lambda x: len(x) - 1 - np.argmax(x),
        raw=True
    )
    periods_since_low = df["l"].rolling(window=window, min_periods=window).apply(
        lambda x: len(x) - 1 - np.argmin(x),
        raw=True
    )

    df["aroon_up"] = 100.0 * (window - periods_since_high) / window
    df["aroon_down"] = 100.0 * (window - periods_since_low) / window
    df["aroon_osc"] = df["aroon_up"] - df["aroon_down"]

    df = _restore_indicator_df(df, restore)
    return df

def add_ultimate_oscillator(
    df: pd.DataFrame,
    short: int = 7,
    medium: int = 14,
    long: int = 28
) -> pd.DataFrame:
    """
    Adds Ultimate Oscillator.
    """
    df, restore = _prep_indicator_df(df)

    high = df["h"]
    low = df["l"]
    close = df["c"]
    prev_close = close.shift(1)

    min_low_close = pd.concat([low, prev_close], axis=1).min(axis=1)
    max_high_close = pd.concat([high, prev_close], axis=1).max(axis=1)

    bp = close - min_low_close
    tr = max_high_close - min_low_close

    tr_short = tr.rolling(window=short, min_periods=short).sum().replace(0, np.nan)
    tr_medium = tr.rolling(window=medium, min_periods=medium).sum().replace(0, np.nan)
    tr_long = tr.rolling(window=long, min_periods=long).sum().replace(0, np.nan)

    avg_short = bp.rolling(window=short, min_periods=short).sum() / tr_short
    avg_medium = bp.rolling(window=medium, min_periods=medium).sum() / tr_medium
    avg_long = bp.rolling(window=long, min_periods=long).sum() / tr_long

    df["ultimate_osc"] = 100.0 * ((4.0 * avg_short) + (2.0 * avg_medium) + avg_long) / 7.0

    df = _restore_indicator_df(df, restore)
    return df

def add_trix(df: pd.DataFrame, window: int = 15, signal_period: int = 9) -> pd.DataFrame:
    """
    Adds TRIX and optional signal line.
    """
    df, restore = _prep_indicator_df(df)

    close = df["c"]
    ema1 = close.ewm(span=window, adjust=False, min_periods=window).mean()
    ema2 = ema1.ewm(span=window, adjust=False, min_periods=window).mean()
    ema3 = ema2.ewm(span=window, adjust=False, min_periods=window).mean()
    df["trix"] = ema3.pct_change() * 100.0

    if signal_period and signal_period > 0:
        df["trix_signal"] = df["trix"].ewm(
            span=signal_period,
            adjust=False,
            min_periods=signal_period
        ).mean()

    df = _restore_indicator_df(df, restore)
    return df

def add_ppo(
    df: pd.DataFrame,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9
) -> pd.DataFrame:
    """
    Adds Percentage Price Oscillator (PPO), signal, and histogram.
    """
    df, restore = _prep_indicator_df(df)

    close = df["c"]
    ema_fast = close.ewm(span=fast_period, adjust=False, min_periods=fast_period).mean()
    ema_slow = close.ewm(span=slow_period, adjust=False, min_periods=slow_period).mean()
    denom = ema_slow.replace(0, np.nan)
    df["ppo"] = ((ema_fast - ema_slow) / denom) * 100.0

    df["ppo_signal"] = df["ppo"].ewm(
        span=signal_period,
        adjust=False,
        min_periods=signal_period
    ).mean()
    df["ppo_hist"] = df["ppo"] - df["ppo_signal"]

    df = _restore_indicator_df(df, restore)
    return df

def add_awesome_oscillator(df: pd.DataFrame, short: int = 5, long: int = 34) -> pd.DataFrame:
    """
    Adds Awesome Oscillator (AO).
    """
    df, restore = _prep_indicator_df(df)

    median_price = (df["h"] + df["l"]) / 2.0
    short_sma = median_price.rolling(window=short, min_periods=short).mean()
    long_sma = median_price.rolling(window=long, min_periods=long).mean()
    df["ao"] = short_sma - long_sma

    df = _restore_indicator_df(df, restore)
    return df

def add_cmo(df: pd.DataFrame, window: int = 14) -> pd.DataFrame:
    """
    Adds Chande Momentum Oscillator (CMO).
    """
    df, restore = _prep_indicator_df(df)

    diff = df["c"].diff()
    gains = diff.where(diff > 0, 0.0)
    losses = (-diff).where(diff < 0, 0.0)

    sum_gains = gains.rolling(window=window, min_periods=window).sum()
    sum_losses = losses.rolling(window=window, min_periods=window).sum()
    denom = (sum_gains + sum_losses).replace(0, np.nan)
    df["cmo"] = 100.0 * (sum_gains - sum_losses) / denom

    df = _restore_indicator_df(df, restore)
    return df

def add_vortex_indicator(df: pd.DataFrame, window: int = 14) -> pd.DataFrame:
    """
    Adds Vortex Indicator (VI+ and VI-).
    """
    df, restore = _prep_indicator_df(df)

    high = df["h"]
    low = df["l"]
    close = df["c"]

    prev_high = high.shift(1)
    prev_low = low.shift(1)

    vm_plus = (high - prev_low).abs()
    vm_minus = (low - prev_high).abs()
    tr = _true_range(high, low, close)

    tr_sum = tr.rolling(window=window, min_periods=window).sum().replace(0, np.nan)
    df["vortex_plus"] = vm_plus.rolling(window=window, min_periods=window).sum() / tr_sum
    df["vortex_minus"] = vm_minus.rolling(window=window, min_periods=window).sum() / tr_sum

    df = _restore_indicator_df(df, restore)
    return df

def filter_regular_trading_hours(df: pd.DataFrame, tz='US/Eastern') -> pd.DataFrame:
    """
    Ensures 'ts' is a datetime in Eastern time, then filters out rows outside 09:30-16:00 Eastern.
    """

    if df.empty:
        return df

    # 1) Convert ts to a datetime if not already
    if not pd.api.types.is_datetime64_any_dtype(df['ts']):
        df['ts'] = pd.to_datetime(df['ts'], errors='coerce')

    # 2) Drop rows where 'ts' did not parse
    df.dropna(subset=['ts'], inplace=True)
    if df.empty:
        return df

    # 3) If 'ts' is naive, localize to UTC first, or whichever zone your data is in originally.
    #    For example, if your raw timestamps represent seconds since epoch in UTC:
    if df['ts'].dt.tz is None:
        df['ts'] = df['ts'].dt.tz_localize('UTC')  # or 'UTC', or whichever your data truly represents

    # 4) Convert from that zone to Eastern
    df['ts'] = df['ts'].dt.tz_convert(tz)  # tz='US/Eastern'

    # 5) Filter by local time-of-day
    df['time_only'] = df['ts'].dt.time
    mask = (df['time_only'] >= time(9, 30)) & (df['time_only'] < time(16, 0)) #type: ignore
    df = df[mask].copy()
    df.drop(columns=['time_only'], inplace=True)

    # 6) (Optional) remove timezone if your DB is storing naive datetime 
    #    (otherwise, you'll see 'YYYY-MM-DD HH:MM:SS-05:00' in your DB).
    df['ts'] = df['ts'].dt.tz_localize(None)

    return df


def add_obv(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a standard On-Balance Volume (OBV) series to the DataFrame.

    OBV is computed as follows:
        1) Sort candles in ascending order by timestamp.
        2) Set obv[0] = 0 (arbitrary starting point).
        3) For each row i from 1..n-1:
             if close[i] > close[i-1]:  obv[i] = obv[i-1] + volume[i]
             if close[i] < close[i-1]:  obv[i] = obv[i-1] - volume[i]
             otherwise:                 obv[i] = obv[i-1]
        4) (Optional) re-sort back descending by timestamp if that is your project convention.

    Returns:
        DataFrame with a new column 'obv'.
    """

    # ── 1) Make a copy & sort ascending to ensure correct calculation ──────────────────────
    df = df.copy()
    df.sort_values("ts", inplace=True)
    df.reset_index(drop=True, inplace=True)

    # ── 2) Initialize an array or list for OBV ─────────────────────────────────────────────
    obv_values = [0.0]  # Start from zero for the first row

    # ── 3) Loop through each row, compute OBV incrementally ───────────────────────────────
    for i in range(1, len(df)):
        current_close = df.loc[i, "c"]
        previous_close = df.loc[i - 1, "c"]
        current_volume = df.loc[i, "v"]
        last_obv = obv_values[-1]

        if current_close > previous_close: #type: ignore
            obv_values.append(last_obv + current_volume) #type: ignore
        elif current_close < previous_close: #type: ignore
            obv_values.append(last_obv - current_volume) #type: ignore
        else:
            # current_close == previous_close
            obv_values.append(last_obv)

    # ── 4) Assign OBV to new column ────────────────────────────────────────────────────────
    df["obv"] = obv_values

    # ── 5) (Optional) Re-sort descending if your system uses newest-first ─────────────────
    # df.sort_values("ts", ascending=False, inplace=True)
    # df.reset_index(drop=True, inplace=True)

    return df




# ─── ADJUST PROJECT DIRECTORY IMPORTS ─────────────────────────────────────────
project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)

# ─── IMPORT PROJECT MODULES ───────────────────────────────────────────────────
from fudstop4.apis.webull.webull_ta import WebullTA
from fudstop4.apis.polygonio.polygon_options import PolygonOptions
from fudstop4._markets.list_sets.ticker_lists import most_active_tickers

# ─── GLOBAL OBJECTS AND CONSTANTS ─────────────────────────────────────────────
# Lower concurrency can help reduce overhead. Adjust as desired.
SEM = Semaphore(60)
ticker_id_cache: Dict[str, int] = {}
ticker_cache_lock = Lock()

# Initialize database and technical analysis objects.
db = PolygonOptions()
ta = WebullTA()

# HTTP headers for requests.
headers = {
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9",
    "access_token": "dc_us_tech1.195f35f8558-58d056ba4f624bea914efffc80b9ea8c",
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
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "ver": "5.3.1",
    "x-s": "43a074e7dffdc536c2959edb65527a0f0db0cf0ab142f9fd63b9950aa72a2e6e",
    "x-sv": "xodp2vg9"
}

# ─── UTILITY: RETRY AIOHTTP REQUESTS ─────────────────────────────────────────
async def fetch_with_retries(
    session: aiohttp.ClientSession,
    url: str,
    headers: dict,
    retries: int = 3,
    delay: float = 1.0
) -> dict: #type: ignore
    """
    Fetch a URL with retries upon failure.
    """
    for attempt in range(retries):
        try:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            logging.warning(
                "Attempt %d/%d failed for URL %s: %s",
                attempt + 1, retries, url, e
            )
            if attempt < retries - 1:
                await asyncio.sleep(delay)
            else:
                raise

# ─── NUMBA-OPTIMIZED FUNCTIONS ───────────────────────────────────────────────
@njit
def compute_wilders_rsi_numba(closes: np.ndarray, window: int) -> np.ndarray:
    """
    Compute Wilder's RSI using Numba. The first `window` values are set to NaN.
    """
    n = len(closes)
    rsi = np.empty(n, dtype=np.float64)
    for i in range(window):
        rsi[i] = np.nan

    # Calculate price changes.
    changes = np.empty(n, dtype=np.float64)
    changes[0] = 0.0
    for i in range(1, n):
        changes[i] = closes[i] - closes[i - 1]

    # Calculate gains and losses.
    gains = np.empty(n, dtype=np.float64)
    losses = np.empty(n, dtype=np.float64)
    for i in range(n):
        if changes[i] > 0:
            gains[i] = changes[i]
            losses[i] = 0.0
        else:
            gains[i] = 0.0
            losses[i] = -changes[i]

    # First average gain and loss.
    sum_gain = 0.0
    sum_loss = 0.0
    for i in range(window):
        sum_gain += gains[i]
        sum_loss += losses[i]
    avg_gain = sum_gain / window
    avg_loss = sum_loss / window

    if avg_loss == 0:
        rsi[window] = 100.0
    else:
        rs = avg_gain / avg_loss
        rsi[window] = 100.0 - (100.0 / (1.0 + rs))

    # Wilder's smoothing for the rest.
    for i in range(window + 1, n):
        avg_gain = ((avg_gain * (window - 1)) + gains[i]) / window
        avg_loss = ((avg_loss * (window - 1)) + losses[i]) / window
        if avg_loss == 0:
            rsi[i] = 100.0
        else:
            rs = avg_gain / avg_loss
            rsi[i] = 100.0 - (100.0 / (1.0 + rs))
    return rsi

def compute_wilders_rsi(df: pd.DataFrame, window: int = 14) -> pd.DataFrame:
    """
    Computes Wilder's RSI on the 'c' (close) column of df.
    """
    if len(df) < window:
        df['rsi'] = np.nan
        return df
    closes = df['c'].to_numpy(dtype=np.float64)
    rsi_values = compute_wilders_rsi_numba(closes, window)
    df['rsi'] = rsi_values
    return df

@njit
def ema_njit(prices: np.ndarray, period: int) -> np.ndarray:
    """
    Calculate the Exponential Moving Average (EMA) for a given period.
    """
    multiplier = 2.0 / (period + 1)
    ema = np.empty(len(prices), dtype=np.float64)
    ema[0] = prices[0]
    for i in range(1, len(prices)):
        ema[i] = (prices[i] - ema[i - 1]) * multiplier + ema[i - 1]
    return ema

@njit
def compute_macd_histogram(prices: np.ndarray) -> np.ndarray:
    """
    Compute the MACD histogram from closing prices using EMA periods of 12, 26, and 9.
    """
    fast = ema_njit(prices, 12)
    slow = ema_njit(prices, 26)
    macd_line = fast - slow
    signal = ema_njit(macd_line, 9)
    hist = macd_line - signal
    return hist

@njit
def determine_macd_curvature_code(prices: np.ndarray) -> int:
    """
    Determine the MACD histogram curvature using refined momentum logic.
    
    Parameters
    ----------
    prices : np.ndarray
        Array of price data (e.g., daily close prices).
    
    Returns
    -------
    int
        An integer code representing the curvature momentum:
        
        0: insufficient data
        1: diverging bull (histogram > 0, strongly increasing)
        2: diverging bear (histogram < 0, strongly decreasing)
        3: arching bull (histogram > 0, but momentum rolling over)
        4: arching bear (histogram < 0, but momentum rolling up)
        5: converging bull (histogram > 0, moderate slope ~ zero)
        6: converging bear (histogram < 0, moderate slope ~ zero)
        7: imminent bullish cross (hist near zero, small slope, below zero => about to cross up)
        8: imminent bearish cross (hist near zero, small slope, above zero => about to cross down)
    
    Enhanced Logic Explanation
    --------------------------
    1) We need at least 4 points in the histogram to detect momentum (first derivative
       ~ slope, second derivative ~ change in slope).
    2) We compute a dynamic threshold based on recent histogram volatility (avg of absolute diffs).
    3) We check near-zero conditions and near-zero slope for "imminent cross".
    4) We check the sign of the latest histogram, the slope from the last 2-3 bars, and second derivative
       to see if it's diverging or arching.
    """
    hist = compute_macd_histogram(prices)
    n = len(hist)
    
    # Need at least 4 data points to do a basic second derivative approach.
    if n < 4:
        return 0  # insufficient data
    
    # Last four points (older -> newer)
    h1, h2, h3, h4 = hist[n - 4], hist[n - 3], hist[n - 2], hist[n - 1]
    
    # First derivative approximations
    d1 = h2 - h1
    d2 = h3 - h2
    d3 = h4 - h3
    
    # Second derivative approximations (changes in slope)
    sd1 = d2 - d1  # how the slope changed from the first gap to the second
    sd2 = d3 - d2  # how the slope changed from the second gap to the third
    
    # Basic slope measure: average of last few differences
    slope = (d2 + d3) / 2.0
    
    # Compute a dynamic threshold based on recent histogram volatility
    # We'll look at the absolute differences h2-h1, h3-h2, h4-h3, etc.
    # This helps us define "strong" vs. "mild" changes adaptively.
    recent_diffs = np.array([abs(d1), abs(d2), abs(d3)])
    avg_hist_vol = np.mean(recent_diffs) + 1e-9  # add small epsilon to avoid /0
    
    # Let's define a "strong slope" if slope magnitude is above 0.75 * avg_hist_vol
    strong_slope_thresh = 0.75 * avg_hist_vol
    
    # We define "near zero" for the histogram and slope
    # You can tweak these to suit your data scale.
    near_zero_hist = 0.1 * avg_hist_vol   # e.g., 10% of avg volatility
    near_zero_slope = 0.1 * avg_hist_vol  # slope threshold near zero
    
    # Check for near-zero histogram and slope => potential cross
    if abs(h4) < near_zero_hist and abs(d3) < near_zero_slope:
        # We examine the average sign of the last 3 or 4 histogram points
        # to guess if it's crossing up or down.
        avg_recent_hist = (h1 + h2 + h3 + h4) / 4.0
        if avg_recent_hist < 0:
            return 7  # imminent bullish cross
        else:
            return 8  # imminent bearish cross
    
    # Not near-zero => check sign of latest histogram
    if h4 > 0:
        # BULLISH SIDE
        if slope > strong_slope_thresh:
            # strongly positive slope => diverging bull
            return 1
        elif slope < -strong_slope_thresh:
            # slope is strongly negative => arching bull
            return 3
        else:
            # slope is moderate => call it converging bull
            return 5
    else:
        # BEARISH SIDE
        if slope < -strong_slope_thresh:
            # strongly negative slope => diverging bear
            return 2
        elif slope > strong_slope_thresh:
            # slope strongly positive => arching bear
            return 4
        else:
            # slope is moderate => converging bear
            return 6

def macd_curvature_label(prices: np.ndarray) -> str:
    """
    Returns a descriptive label for the MACD curvature.
    """
    code = determine_macd_curvature_code(prices)
    mapping = {
        0: "insufficient data",
        1: "diverging bull",
        2: "diverging bear",
        3: "arching bull",
        4: "arching bear",
        5: "converging bull",
        6: "converging bear",
        7: "imminent bullish cross",
        8: "imminent bearish cross"
    }
    return mapping.get(code, "unknown")

# ─── UPDATED TD SEQUENTIAL LOGIC ─────────────────────────────────────────────
@njit
def compute_td9_counts(closes: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute 'TD setup' counts for buy and sell but allow the counts to run 
    beyond 9 bars as long as the condition remains intact.

    RULES:
      1. Only one setup at a time (buy OR sell). 
         If buy_count > 0, we do not update sell_count (and vice versa).
      2. If buy_count > 0, keep incrementing if c[i] < c[i-4]. 
         If it fails, reset buy_count to 0, 
         then check if c[i] > c[i-4] to start a new sell_count = 1 on the same bar.
      3. If sell_count > 0, keep incrementing if c[i] > c[i-4].
         If it fails, reset sell_count to 0,
         then check if c[i] < c[i-4] to start a new buy_count = 1 on the same bar.
      4. If both buy_count and sell_count are 0, see if we can start one:
         - If c[i] < c[i-4], buy_count = 1
         - Else if c[i] > c[i-4], sell_count = 1
    """
    n = len(closes)
    td_buy = np.zeros(n, dtype=np.int32)
    td_sell = np.zeros(n, dtype=np.int32)

    buy_count = 0
    sell_count = 0

    for i in range(n):
        if i < 4:
            td_buy[i] = buy_count
            td_sell[i] = sell_count
            continue

        if buy_count > 0:
            # Already in a BUY setup
            if closes[i] < closes[i - 4]:
                buy_count += 1
            else:
                # Broke buy condition, reset
                buy_count = 0
                # Attempt to start SELL
                if closes[i] > closes[i - 4]:
                    sell_count = 1
                else:
                    sell_count = 0

        elif sell_count > 0:
            # Already in a SELL setup
            if closes[i] > closes[i - 4]:
                sell_count += 1
            else:
                # Broke sell condition, reset
                sell_count = 0
                # Attempt to start BUY
                if closes[i] < closes[i - 4]:
                    buy_count = 1
                else:
                    buy_count = 0
        else:
            # Not in an active setup
            if closes[i] < closes[i - 4]:
                buy_count = 1
            elif closes[i] > closes[i - 4]:
                sell_count = 1

        td_buy[i] = buy_count
        td_sell[i] = sell_count

    return td_buy, td_sell

def add_td9_counts(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds two columns to df:
      - td_buy_count: increments if c[i] < c[i-4] 
      - td_sell_count: increments if c[i] > c[i-4]
      Allows extended sequences beyond 9 as long as 
      the condition is not broken.
    """
    try:
        df = df.copy()
        # Sort ascending for correct sequential logic
        df.sort_values("ts", inplace=True)
        df.reset_index(drop=True, inplace=True)

        closes = df['c'].to_numpy()
        td_buy, td_sell = compute_td9_counts(closes)

        df['td_buy_count'] = td_buy
        df['td_sell_count'] = td_sell
        return df
    except Exception as e:
        print(e)


# ──────────────────────────────────────────────────────────────────────────────
# BULLISH/BEARISH ENGULFING DETECTION
# ──────────────────────────────────────────────────────────────────────────────
def add_engulfing_patterns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Flags perfect bullish or bearish engulfing patterns.
    """
    df = df.copy()
    df['bullish_engulfing'] = False
    df['bearish_engulfing'] = False

    if len(df) < 2:
        return df

    # Sort ascending by timestamp for consistent logic
    df.sort_values("ts", inplace=True)
    df.reset_index(drop=True, inplace=True)

    for i in range(1, len(df)):
        # Previous candle
        pOpen = df.loc[i-1, 'o']
        pClose = df.loc[i-1, 'c']
        pHigh = df.loc[i-1, 'h']
        pLow = df.loc[i-1, 'l']

        # Current candle
        cOpen = df.loc[i, 'o']
        cClose = df.loc[i, 'c']
        cHigh = df.loc[i, 'h']
        cLow = df.loc[i, 'l']

        # Check for bullish engulfing
        if (pClose < pOpen and cClose > cOpen): #type: ignore
            if (cHigh > pHigh and cLow < pLow): #type: ignore
                if (cOpen < pClose and cClose > pOpen): #type: ignore
                    df.loc[i, 'bullish_engulfing'] = True

        # Check for bearish engulfing
        if (pClose > pOpen and cClose < cOpen): #type: ignore
            if (cHigh > pHigh and cLow < pLow): #type: ignore
                if (cOpen > pClose and cClose < pOpen): #type: ignore
                    df.loc[i, 'bearish_engulfing'] = True

    return df




def add_volume_metrics(df: pd.DataFrame, window: int = 5) -> pd.DataFrame:
    """
    Add various volume-based metrics to the DataFrame.
    
    Columns added:
    - volume_diff: difference in volume from the previous bar
    - volume_pct_change: (current_volume / previous_volume - 1) * 100
    - n_increasing_volume_streak: consecutive bars of increasing volume
    - n_decreasing_volume_streak: consecutive bars of decreasing volume
    - volume_ma_{window}: rolling average of volume over `window` bars
    - volume_zscore_{window}: Z-score of the current volume vs. rolling mean/std
    """

    # Ensure the DataFrame is sorted by ascending timestamp
    df = df.sort_values("ts").reset_index(drop=True)

    # 1) Volume Difference
    df["volume_diff"] = df["v"].diff().fillna(0)

    # 2) Volume % Change
    df["volume_pct_change"] = df["v"].pct_change().fillna(0) * 100

    # 3) Streaks of Increasing/Decreasing Volume
    n_increasing = [0] * len(df)
    n_decreasing = [0] * len(df)

    for i in range(1, len(df)):
        # If this bar's volume is higher than previous, increase the 'n_increasing' streak
        if df.loc[i, "v"] > df.loc[i - 1, "v"]: #type: ignore
            n_increasing[i] = n_increasing[i - 1] + 1
        else:
            n_increasing[i] = 0
        
        # If this bar's volume is lower than previous, increase the 'n_decreasing' streak
        if df.loc[i, "v"] < df.loc[i - 1, "v"]: #type: ignore
            n_decreasing[i] = n_decreasing[i - 1] + 1
        else:
            n_decreasing[i] = 0

    df["volume_increasing_streak"] = n_increasing
    df["volume_decreasing_streak"] = n_decreasing



    return df


import hashlib
import random
import string
import time
def generate_webull_headers():
    """
    Dynamically generates headers for a Webull request.
    Offsets the current system time by 6 hours (in milliseconds) for 't_time'.
    Creates a randomized 'x-s' value each time.
    Adjust these methods of generation if you have more info on Webull's official approach.
    """
    # Offset by 6 hours
    offset_hours = 6
    offset_millis = offset_hours * 3600 * 1000

    # Current system time in ms
    current_millis = int(time.time() * 1000)
    t_time_value = current_millis - offset_millis

    # Generate a random string to feed into a hash
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
    # Create an x-s value (example: SHA256 hash of random_str + t_time_value)
    x_s_value = hashlib.sha256(f"{random_str}{t_time_value}".encode()).hexdigest()

    # Build and return the headers
    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9",
        "access_token": "dc_us_tech1.196b5c4dea9-76aba23cd6c34871aeaa5f50aa012ad2",
        "app": "global",
        "app-group": "broker",
        "appid": "wb_web_app",
        "cache-control": "no-cache",
        "device-type": "Web",
        "did": "3uiar5zgvki16rgnpsfca4kyo4scy00a",
        "dnt": "1",
        "hl": "en",
        "origin": "https://app.webull.com",
        "os": "web",
        "osv": "i9zh",
        "platform": "web",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "referer": "https://app.webull.com/",
        "reqid": "kyiyrlq2kxig1vcwrdhcxvp3h5lc0_45",
        "sec-ch-ua": "\"Not(A:Brand\";v=\"24\", \"Google Chrome\";v=\"134\", \"Chromium\";v=\"134\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "t_time": str(t_time_value),
        "tz": "America/Chicago",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        "ver": "5.4.3",
        "x-s": x_s_value,
        "x-sv": "xodp2vg9"
    }

    return headers

# ──────────────────────────────────────────────────────────────────────────────
# STANDARD DEVIATION CHANNEL (SDC) - 21-BAR LOOKBACK
# ADJUSTED TO CHECK IF PRICE IS ABOVE OR BELOW THE CHANNEL.
# ──────────────────────────────────────────────────────────────────────────────
def add_sdc_indicator(
    df: pd.DataFrame,
    window: int = 50,
    dev_up: float = 1.5,
    dev_dn: float = 1.5
) -> pd.DataFrame:
    """
    Computes a Standard Deviation Channel (SDC) over a rolling window.

    For each rolling segment of 'window' bars:
      1) Fit a straight line (via polyfit) to the close prices (y) over x=[0..window-1].
      2) Compute the residual std dev from that line.
      3) Define channel boundaries (on the *latest* bar in the window) at:
         sdc_upper = (line_value at latest bar) + dev_up * std
         sdc_lower = (line_value at latest bar) - dev_dn * std
      4) Compare the entire candle (its high/low) to the channel:
         - 'above_both' if candle's LOW is above sdc_upper
         - 'below_both' if candle's HIGH is below sdc_lower
         - 'BETWEEN'    otherwise

    Columns added to df (NaN for the first (window-1) rows):
        'linreg_slope', 'linreg_intercept', 'linreg_std'
        'sdc_upper', 'sdc_lower'
        'sdc_signal' -> 'above_both', 'below_both', or 'BETWEEN'

    :param df:      DataFrame in ASCENDING time order with columns:
                        - 'c' (close), 'h' (high), 'l' (low).
    :param window:  Rolling window size for each regression (default 50).
    :param dev_up:  Multiplier for the upper std dev offset (default 1.0).
    :param dev_dn:  Multiplier for the lower std dev offset (default 1.0).
    :return:        The DataFrame with new columns.
    """
    try:
        # Initialize new columns
        df['linreg_slope'] = np.nan
        df['linreg_intercept'] = np.nan
        df['linreg_std'] = np.nan
        df['sdc_upper'] = np.nan
        df['sdc_lower'] = np.nan
        df['sdc_signal'] = pd.Series([None] * len(df), dtype='object')

        # Not enough data to calculate anything
        if len(df) < window:
            return df

        # Rolling regression loop
        for i in range(window - 1, len(df)):
            subdf = df.iloc[i - window + 1 : i + 1]

            # x = 0..window-1
            x = np.arange(window)
            y = subdf['c'].values

            # Fit linear regression (1st-degree polyfit)
            slope, intercept = np.polyfit(x, y, deg=1) #type: ignore

            # Calculate residual std deviation
            predicted = slope * x + intercept
            residuals = y - predicted
            std_val = np.std(residuals, ddof=1)  # sample std

            # For the "last bar" in this window:
            latest_x = window - 1
            base_value = slope * latest_x + intercept

            # Compute channel boundaries
            sdc_up = base_value + (dev_up * std_val)
            sdc_dn = base_value - (dev_dn * std_val)

            # Store regression results & SDC in the final bar of that window
            df.loc[i, 'linreg_slope'] = slope
            df.loc[i, 'linreg_intercept'] = intercept
            df.loc[i, 'linreg_std'] = std_val
            df.loc[i, 'sdc_upper'] = sdc_up
            df.loc[i, 'sdc_lower'] = sdc_dn

            # Determine SDC signal
            c_high = df.at[i, 'h']
            c_low = df.at[i, 'l']

            if c_low > sdc_up:
                signal = 'above_both'
            elif c_high < sdc_dn:
                signal = 'below_both'
            else:
                signal = 'BETWEEN'

            df.at[i, 'sdc_signal'] = signal

        return df
    except Exception as e:
        print(e)

async def process_option_id(ticker, strike, call_put, expiry, option_id):
    url = f"https://quotes-gw.webullfintech.com/api/statistic/option/queryVolumeAnalysis?count=50&tickerId={option_id}"
    try:
        async with aiohttp.ClientSession(headers=generate_webull_headers()) as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    print(f"[!] Failed to fetch for {option_id} - Status: {resp.status}")
                    return
                data = await resp.json()
                total_trades = data.get('totalNum')
                total_vol = data.get('totalVolume')
                avg_price = data.get('avgPrice')
                buy_vol = data.get('buyVolume')
                sell_vol = data.get('sellVolume')
                neut_vol = data.get('neutralVolume')
                ticker_id = data.get('tickerId')
                dict_ = { 
                    'option_id': ticker_id,
                    'ticker': ticker,
                    'strike': strike,
                    'call_put': call_put,
                    'expiry': expiry,
                    'total_trades': total_trades,
                    'total_vol': total_vol,
                    'buy_vol': buy_vol,
                    'sell_vol': sell_vol,
                    'neut_vol': neut_vol,
                    
                }

                return dict_
    except Exception as e:
        print(e)


# ---- Add a jitted MACD core that requires an array ----
@njit(cache=True)
def _macd_core(closes: np.ndarray,
               fast_period: int,
               slow_period: int,
               signal_period: int):
    fast = ema_njit(closes, fast_period)
    slow = ema_njit(closes, slow_period)
    macd_line = fast - slow
    signal_line = ema_njit(macd_line, signal_period)
    hist = macd_line - signal_line
    return macd_line, signal_line, hist
# ---- Replace your existing macd_from_close with this adapter ----
def macd_from_close(closes,
                    fast_period: int = 12,
                    slow_period: int = 26,
                    signal_period: int = 9):
    """
    Python adapter that accepts list/Series/array, converts to ndarray,
    then calls the jitted core. Prevents reflected-list issues in Numba.
    """
    closes_arr = np.asarray(closes, dtype=np.float64)
    return _macd_core(closes_arr, fast_period, slow_period, signal_period)




# ---------- Robust column detection (handles many provider schemas) ----------
OPEN_ALIASES  = ("o", "open", "openprice", "price_open")
HIGH_ALIASES  = ("h", "high", "highprice", "price_high")
LOW_ALIASES   = ("l", "low", "lowprice", "price_low")
CLOSE_ALIASES = ("c", "close", "adjclose", "adj_close", "closeprice", "closing_price", "last", "lastprice", "price", "p")

def _find_col(df: pd.DataFrame, aliases: tuple) -> str | None:
    """Return the first matching column name (case-insensitive), else None."""
    # normalize: map lower -> original
    col_map = {str(c).lower(): c for c in df.columns}
    for a in aliases:
        key = a.lower()
        if key in col_map:
            return col_map[key]
    return None



def add_confluence_score(df: pd.DataFrame, macd_sentiment: str) -> pd.DataFrame:
    """
    Add a multi-factor confluence score using researched, widely used thresholds.

    Signals/points (all ASCII for clarity):
      - TD9: classic 9/13/20/25 thresholds mapped to 1/2/3/4 points (buy minus sell).
      - RSI: <20 +4, 20-30 +2, cross above 50 +1; >80 -4, 70-80 -2, cross below 50 -1.
      - MACD: sentiment +3/-3, fresh line cross +2/-2, histogram z-score >1/-1 adds +1/-1.
      - Bollinger: z <= -2 +3, -2 to -1 +1; z >= 2 -3, 1 to 2 -1.
      - Volume/Confluence (enhanced):
          * RVOL (v / 20-mean) thresholds
          * volume z-score vs rolling mean/std
          * fast/slow volume trend (5-mean / 20-mean)
          * signed volume pressure (rolling net buy/sell volume)
          * impulse coupling (big move + high vol)
        Final score_volume shifts by 1 candle to reduce in-progress candle noise.
      - SDC channel: close above upper band +2, below lower band -2.
    """
    df = df.copy()

    # Keep rolling math honest (chronological order)
    if "ts" in df.columns:
        df = df.sort_values("ts").reset_index(drop=True)

    lower_cols = {c.lower(): c for c in df.columns}

    # Initialize all component scores to 0
    for col in ("score_td9", "score_rsi", "score_macd", "score_bbands", "score_volume", "score_sdc"):
        if col not in df.columns:
            df[col] = 0

    # --- TD9 buy/sell counts (robust column detection) ---
    td_buy_candidates  = ['td9_buy', 'td9_buy_count', 'td_buy', 'td_buy_count',
                          'tdsequential_buy', 'td_buy_setup', 'td9buy', 'td_buycount']
    td_sell_candidates = ['td9_sell', 'td9_sell_count', 'td_sell', 'td_sell_count',
                          'tdsequential_sell', 'td_sell_setup', 'td9sell', 'td_sellcount']

    buy_col  = next((lower_cols[n] for n in td_buy_candidates  if n in lower_cols), None)
    sell_col = next((lower_cols[n] for n in td_sell_candidates if n in lower_cols), None)

    buy_series  = df[buy_col]  if buy_col  else pd.Series(0, index=df.index, dtype=float)
    sell_series = df[sell_col] if sell_col else pd.Series(0, index=df.index, dtype=float)

    df['score_td9'] = buy_series.apply(_td_points) - sell_series.apply(_td_points)

    # --- RSI scoring ---
    rsi_candidates = ['rsi', 'rsi_14', 'rsi_wilders', 'wilders_rsi']
    rsi_col = next((lower_cols[n] for n in rsi_candidates if n in lower_cols), None)
    rsi = df[rsi_col] if rsi_col else pd.Series(np.nan, index=df.index, dtype=float)

    base_rsi_score = np.select(
        [
            rsi < 20,
            (rsi >= 20) & (rsi < 30),
            rsi > 80,
            (rsi > 70) & (rsi <= 80),
        ],
        [4, 2, -4, -2],
        default=0
    )

    rsi_cross = pd.Series(0, index=df.index, dtype=int)
    if rsi_col:
        prev_rsi = rsi.shift(1)
        cross_up = (prev_rsi <= 50) & (rsi > 50)
        cross_dn = (prev_rsi >= 50) & (rsi < 50)
        rsi_cross[cross_up] = 1
        rsi_cross[cross_dn] = -1

    df['score_rsi'] = base_rsi_score + rsi_cross

    # --- MACD scoring ---
    sent = (macd_sentiment or '').strip().lower()
    macd_points = 3 if sent == 'bullish' else (-3 if sent == 'bearish' else 0)

    macd_cross = pd.Series(0, index=df.index, dtype=int)
    hist_score = pd.Series(0, index=df.index, dtype=int)

    macd_val = df.get('macd_value')
    macd_sig = df.get('macd_signal')
    macd_hist = df.get('macd_hist')

    if macd_val is not None and macd_sig is not None:
        cross_up = (macd_val.shift(1) < macd_sig.shift(1)) & (macd_val > macd_sig)
        cross_dn = (macd_val.shift(1) > macd_sig.shift(1)) & (macd_val < macd_sig)
        macd_cross = pd.Series(
            np.where(cross_up, 2, np.where(cross_dn, -2, 0)),
            index=df.index,
            dtype=int
        )

    if macd_hist is not None:
        hist_std = macd_hist.rolling(15, min_periods=5).std()
        hist_z = np.where(hist_std > 0, macd_hist / hist_std, 0)
        hist_score = pd.Series(
            np.select(
                [hist_z >= 1.0, hist_z <= -1.0],
                [1, -1],
                default=0
            ),
            index=df.index,
            dtype=int
        )

    df['score_macd'] = macd_points + macd_cross + hist_score

    # --- Bollinger z-score (mean-reversion style) ---
    if {'middle_band', 'std'}.issubset(df.columns):
        std = df['std'].replace(0, np.nan)
        bb_z = (df['c'] - df['middle_band']) / std
        df['score_bbands'] = np.select(
            [
                bb_z <= -2.0,
                (bb_z > -2.0) & (bb_z <= -1.0),
                bb_z >= 2.0,
                (bb_z < 2.0) & (bb_z >= 1.0)
            ],
            [3, 1, -3, -1],
            default=0
        ).astype(int)

    # --- Enhanced volume / rolling-stat confluence ---
    open_col = _find_col(df, OPEN_ALIASES)

    if open_col:
        price_up = (df['c'] > df[open_col])
        price_down = (df['c'] < df[open_col])
    else:
        prev_c = df['c'].shift(1)
        price_up = (df['c'] > prev_c)
        price_down = (df['c'] < prev_c)

    vol = pd.to_numeric(df.get('v', 0), errors='coerce').fillna(0.0)

    vol_ma20 = vol.rolling(20, min_periods=5).mean()
    vol_std20 = vol.rolling(20, min_periods=5).std()

    vol_ratio = pd.Series(np.where(vol_ma20 > 0, vol / vol_ma20, 0.0), index=df.index)
    vol_z = pd.Series(np.where(vol_std20 > 0, (vol - vol_ma20) / vol_std20, 0.0), index=df.index)

    vol_ma5 = vol.rolling(5, min_periods=3).mean()
    vol_trend_ratio = pd.Series(np.where(vol_ma20 > 0, vol_ma5 / vol_ma20, 1.0), index=df.index)

    # Base RVOL score (stronger penalty for heavy sell volume)
    base_vol_score = pd.Series(
        np.select(
            [
                (vol_ratio >= 1.8) & price_up,
                (vol_ratio >= 1.3) & price_up,
                (vol_ratio >= 1.8) & price_down,
                (vol_ratio >= 1.3) & price_down,
            ],
            [2, 1, -2, -1],
            default=0
        ),
        index=df.index,
        dtype=int
    )

    # Streak score (uses your precomputed `volume_streak`)
    streak_score = pd.Series(0, index=df.index, dtype=int)
    if "volume_streak" in df.columns:
        streak_score = pd.Series(
            np.select(
                [
                    (df["volume_streak"] >= 3) & price_up,
                    (df["volume_streak"] <= -3) & price_down,
                ],
                [1, -1],
                default=0
            ),
            index=df.index,
            dtype=int
        )

    # Fast/slow trend ratio (rising interest vs fading interest)
    trend_score = pd.Series(
        np.select(
            [
                (vol_trend_ratio >= 1.15) & price_up,
                (vol_trend_ratio >= 1.15) & price_down,
                (vol_trend_ratio <= 0.85) & price_up,
                (vol_trend_ratio <= 0.85) & price_down,
            ],
            [1, -1, -1, 1],
            default=0
        ),
        index=df.index,
        dtype=int
    )

    # Volume z-score context (statistical loudness)
    vol_z_score = pd.Series(
        np.select(
            [
                (vol_z >= 2.0) & price_up,
                (vol_z >= 2.0) & price_down,
                (vol_z <= -1.0) & price_up,
                (vol_z <= -1.0) & price_down,
            ],
            [1, -1, -1, 1],
            default=0
        ),
        index=df.index,
        dtype=int
    )

    # Signed volume pressure (net buy/sell volume over last ~10 candles)
    signed_vol = np.where(price_up, vol, np.where(price_down, -vol, 0.0))
    pressure_sum = pd.Series(signed_vol, index=df.index).rolling(10, min_periods=5).sum()
    pressure_ratio = pd.Series(
        np.where(vol_ma20 > 0, pressure_sum / (vol_ma20 * 10.0), 0.0),
        index=df.index
    )
    pressure_score = pd.Series(
        np.select(
            [pressure_ratio >= 0.15, pressure_ratio <= -0.15],
            [1, -1],
            default=0
        ),
        index=df.index,
        dtype=int
    )

    # Impulse coupling: big move + high vol = real; big move without vol = meh
    ret = df["c"].pct_change().fillna(0.0)
    abs_ret = ret.abs()
    abs_ret_ma20 = abs_ret.rolling(20, min_periods=5).mean()
    abs_ret_std20 = abs_ret.rolling(20, min_periods=5).std()
    ret_z = pd.Series(np.where(abs_ret_std20 > 0, (abs_ret - abs_ret_ma20) / abs_ret_std20, 0.0), index=df.index)

    impulse_score = pd.Series(
        np.select(
            [
                (ret_z >= 1.5) & (vol_z >= 1.0) & (ret > 0),
                (ret_z >= 1.5) & (vol_z >= 1.0) & (ret < 0),
            ],
            [1, -1],
            default=0
        ),
        index=df.index,
        dtype=int
    )

    raw_volume_score = (
        base_vol_score
        + streak_score
        + trend_score
        + vol_z_score
        + pressure_score
        + impulse_score
    ).clip(-6, 6)

    # IMPORTANT: shift to last closed candle to avoid in-progress candle volume lies
    df["score_volume"] = raw_volume_score.shift(1).fillna(0).astype(int)

    # Optional tightening: reward/punish BB "completely outside" only when volume confirms (also shifted)
    # This pairs nicely with your "previous candle closure" BB fix.
    vol_confirm = ((vol_ratio >= 1.3) | (vol_z >= 1.0) | (vol_trend_ratio >= 1.15)).shift(1).fillna(False)

    if "candle_completely_below_lower" in df.columns:
        df["score_bbands"] = df["score_bbands"] + np.where(df["candle_completely_below_lower"] & vol_confirm, 1, 0).astype(int)

    if "candle_completely_above_upper" in df.columns:
        df["score_bbands"] = df["score_bbands"] + np.where(df["candle_completely_above_upper"] & vol_confirm, -1, 0).astype(int)

    # --- SDC regression channel breaks ---
    if 'sdc_signal' in df.columns:
        df['score_sdc'] = np.select(
            [
                df['sdc_signal'] == 'above_both',
                df['sdc_signal'] == 'below_both'
            ],
            [2, -2],
            default=0
        )

    # --- Total ---
    components = ['score_td9', 'score_rsi', 'score_macd', 'score_bbands', 'score_volume', 'score_sdc']
    df['confluence_score'] = df[components].sum(axis=1)

    return df


# Indicator API moved to scripts/fudstop_ta.py
from fudstop_ta import FudstopTA  # noqa: E402

OPEN_ALIASES = FudstopTA.OPEN_ALIASES
HIGH_ALIASES = FudstopTA.HIGH_ALIASES
LOW_ALIASES = FudstopTA.LOW_ALIASES
CLOSE_ALIASES = FudstopTA.CLOSE_ALIASES

_find_col = FudstopTA._find_col

add_parabolic_sar_signals = FudstopTA.add_parabolic_sar_signals
compute_volume_profile = FudstopTA.compute_volume_profile
add_td9_counts = FudstopTA.add_td9_counts
compute_bollinger_bands = FudstopTA.compute_bollinger_bands
compute_stochastic_oscillator = FudstopTA.compute_stochastic_oscillator
compute_atr = FudstopTA.compute_atr
compute_supertrend = FudstopTA.compute_supertrend
compute_adx = FudstopTA.compute_adx
compute_trend = FudstopTA.compute_trend
compute_angle = FudstopTA.compute_angle
compute_relative_angle = FudstopTA.compute_relative_angle
add_bollinger_bands = FudstopTA.add_bollinger_bands
_prep_indicator_df = FudstopTA._prep_indicator_df
_restore_indicator_df = FudstopTA._restore_indicator_df
_true_range = FudstopTA._true_range
_wilder_smooth = FudstopTA._wilder_smooth
add_atr = FudstopTA.add_atr
add_stochastic_oscillator = FudstopTA.add_stochastic_oscillator
add_cci = FudstopTA.add_cci
add_williams_r = FudstopTA.add_williams_r
add_mfi = FudstopTA.add_mfi
add_roc = FudstopTA.add_roc
add_donchian_channels = FudstopTA.add_donchian_channels
add_keltner_channels = FudstopTA.add_keltner_channels
add_chaikin_money_flow = FudstopTA.add_chaikin_money_flow
add_accumulation_distribution = FudstopTA.add_accumulation_distribution
add_aroon = FudstopTA.add_aroon
add_ultimate_oscillator = FudstopTA.add_ultimate_oscillator
add_trix = FudstopTA.add_trix
add_ppo = FudstopTA.add_ppo
add_awesome_oscillator = FudstopTA.add_awesome_oscillator
add_cmo = FudstopTA.add_cmo
add_vortex_indicator = FudstopTA.add_vortex_indicator
add_obv = FudstopTA.add_obv
compute_wilders_rsi_numba = FudstopTA.compute_wilders_rsi_numba
compute_wilders_rsi = FudstopTA.compute_wilders_rsi
ema_njit = FudstopTA.ema_njit
compute_macd_histogram = FudstopTA.compute_macd_histogram
determine_macd_curvature_code = FudstopTA.determine_macd_curvature_code
macd_curvature_label = FudstopTA.macd_curvature_label
compute_td9_counts = FudstopTA.compute_td9_counts
add_engulfing_patterns = FudstopTA.add_engulfing_patterns
add_volume_metrics = FudstopTA.add_volume_metrics
add_sdc_indicator = FudstopTA.add_sdc_indicator
macd_from_close = FudstopTA.macd_from_close
add_confluence_score = FudstopTA.add_confluence_score
