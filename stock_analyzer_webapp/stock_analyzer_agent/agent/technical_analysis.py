# This file will contain modules for calculating technical indicators.
import pandas as pd
import numpy as np # Added for handling potential inf values if needed, and for NaN
from typing import Dict, Optional, Tuple, Any # For type hinting, added Any

# Assuming historical_data is passed as an argument for now.
# from .data_collection import get_historical_stock_data

def calculate_moving_average(historical_data: pd.DataFrame, window: int) -> pd.Series:
    """
    Calculates the simple moving average (SMA) for the 'Close' price.

    Args:
        historical_data: Pandas DataFrame with historical stock data (must include a 'Close' column).
        window: The window period for the moving average (integer).

    Returns:
        A pandas Series with the SMA values, or an empty Series if an error occurs.
    """
    if not isinstance(historical_data, pd.DataFrame):
        print("Error: historical_data must be a pandas DataFrame.")
        return pd.Series(dtype=float)
    if 'Close' not in historical_data.columns:
        print("Error: 'Close' column not found in historical_data.")
        return pd.Series(dtype=float)
    if not isinstance(window, int) or window <= 0:
        print("Error: window must be a positive integer.")
        return pd.Series(dtype=float)
    if len(historical_data) < window:
        print(f"Error: Not enough data ({len(historical_data)} points) for window size {window}.")
        return pd.Series(dtype=float)

    try:
        sma = historical_data['Close'].rolling(window=window, min_periods=window).mean()
        return sma
    except Exception as e:
        print(f"Error calculating moving average: {e}")
        return pd.Series(dtype=float)

def calculate_rsi(historical_data: pd.DataFrame, window: int = 14) -> pd.Series:
    """
    Calculates the Relative Strength Index (RSI).

    Args:
        historical_data: Pandas DataFrame with historical stock data (must include a 'Close' column).
        window: The window period for RSI calculation (default 14).

    Returns:
        A pandas Series with the RSI values, or an empty Series if an error occurs.
    """
    if not isinstance(historical_data, pd.DataFrame):
        print("Error: historical_data must be a pandas DataFrame.")
        return pd.Series(dtype=float)
    if 'Close' not in historical_data.columns:
        print("Error: 'Close' column not found in historical_data.")
        return pd.Series(dtype=float)
    if not isinstance(window, int) or window <= 0:
        print("Error: window must be a positive integer.")
        return pd.Series(dtype=float)
    if len(historical_data) < window + 1: 
        print(f"Error: Not enough data ({len(historical_data)} points) for RSI window size {window}.")
        return pd.Series(dtype=float)

    try:
        delta = historical_data['Close'].diff()
        
        gain = pd.Series(index=delta.index, dtype=float)
        loss = pd.Series(index=delta.index, dtype=float)
        
        gain[delta > 0] = delta[delta > 0]
        gain[delta <= 0] = 0 
        
        loss[delta < 0] = -delta[delta < 0]
        loss[delta >= 0] = 0 

        avg_gain = gain.ewm(com=window - 1, min_periods=window).mean()
        avg_loss = loss.ewm(com=window - 1, min_periods=window).mean()
        
        rs = avg_gain / avg_loss
        
        rsi = 100 - (100 / (1 + rs))
        
        rsi.loc[(avg_loss == 0) & (avg_gain == 0)] = 50 
        rsi.loc[(avg_loss == 0) & (avg_gain > 0)] = 100 
        rsi.loc[avg_loss.isna() & avg_gain.isna()] = np.nan

        return rsi

    except Exception as e:
        print(f"Error calculating RSI: {e}")
        return pd.Series(dtype=float)

def calculate_macd(historical_data: pd.DataFrame, short_window: int = 12, long_window: int = 26, signal_window: int = 9) -> tuple[pd.Series, pd.Series, pd.Series]:
    """
    Calculates the MACD line, Signal line, and MACD Histogram.
    """
    empty_series_tuple = (pd.Series(dtype=float), pd.Series(dtype=float), pd.Series(dtype=float))
    if not isinstance(historical_data, pd.DataFrame):
        print("Error: historical_data must be a pandas DataFrame.")
        return empty_series_tuple
    if 'Close' not in historical_data.columns:
        print("Error: 'Close' column not found in historical_data.")
        return empty_series_tuple
    if not all(isinstance(w, int) and w > 0 for w in [short_window, long_window, signal_window]):
        print("Error: All window periods must be positive integers.")
        return empty_series_tuple
    if long_window <= short_window:
        print("Error: long_window must be greater than short_window.")
        return empty_series_tuple
    if len(historical_data) < long_window + signal_window -1 : 
        print(f"Error: Not enough data ({len(historical_data)} points) for MACD calculation (long_window={long_window}, signal_window={signal_window}).")
        return empty_series_tuple

    try:
        short_ema = historical_data['Close'].ewm(span=short_window, adjust=False, min_periods=short_window).mean()
        long_ema = historical_data['Close'].ewm(span=long_window, adjust=False, min_periods=long_window).mean()
        
        macd_line = short_ema - long_ema
        signal_line = macd_line.ewm(span=signal_window, adjust=False, min_periods=signal_window).mean()
        macd_histogram = macd_line - signal_line
        
        return macd_line, signal_line, macd_histogram
    except Exception as e:
        print(f"Error calculating MACD: {e}")
        return empty_series_tuple

def calculate_bollinger_bands(historical_data: pd.DataFrame, window: int = 20, num_std_dev: float = 2.0) -> tuple[pd.Series, pd.Series, pd.Series]:
    """
    Calculates the Upper Band, Middle Band (SMA), and Lower Band for Bollinger Bands.
    """
    empty_series_tuple = (pd.Series(dtype=float), pd.Series(dtype=float), pd.Series(dtype=float))
    if not isinstance(historical_data, pd.DataFrame):
        print("Error: historical_data must be a pandas DataFrame.")
        return empty_series_tuple
    if 'Close' not in historical_data.columns:
        print("Error: 'Close' column not found in historical_data.")
        return empty_series_tuple
    if not (isinstance(window, int) and window > 0):
        print("Error: window must be a positive integer.")
        return empty_series_tuple
    if not (isinstance(num_std_dev, (int, float)) and num_std_dev > 0):
        print("Error: num_std_dev must be a positive number.")
        return empty_series_tuple
    if len(historical_data) < window:
        print(f"Error: Not enough data ({len(historical_data)} points) for Bollinger Bands window {window}.")
        return empty_series_tuple

    try:
        middle_band = historical_data['Close'].rolling(window=window, min_periods=window).mean()
        std_dev = historical_data['Close'].rolling(window=window, min_periods=window).std()
        
        upper_band = middle_band + (std_dev * num_std_dev)
        lower_band = middle_band - (std_dev * num_std_dev)
        
        return upper_band, middle_band, lower_band
    except Exception as e:
        print(f"Error calculating Bollinger Bands: {e}")
        return empty_series_tuple

def calculate_stochastic_oscillator(historical_data: pd.DataFrame, k_window: int = 14, d_window: int = 3) -> tuple[pd.Series, pd.Series]:
    """
    Calculates the %K and %D for the Stochastic Oscillator.
    """
    empty_series_tuple = (pd.Series(dtype=float), pd.Series(dtype=float))
    if not isinstance(historical_data, pd.DataFrame):
        print("Error: historical_data must be a pandas DataFrame.")
        return empty_series_tuple
    required_columns = ['Close', 'High', 'Low']
    if not all(col in historical_data.columns for col in required_columns):
        print(f"Error: historical_data must contain {', '.join(required_columns)} columns.")
        return empty_series_tuple
    if not (isinstance(k_window, int) and k_window > 0):
        print("Error: k_window must be a positive integer.")
        return empty_series_tuple
    if not (isinstance(d_window, int) and d_window > 0):
        print("Error: d_window must be a positive integer.")
        return empty_series_tuple
    if len(historical_data) < k_window + d_window - 1:
         print(f"Error: Not enough data ({len(historical_data)} points) for Stochastic Oscillator (k_window={k_window}, d_window={d_window}).")
         return empty_series_tuple

    try:
        lowest_low = historical_data['Low'].rolling(window=k_window, min_periods=k_window).min()
        highest_high = historical_data['High'].rolling(window=k_window, min_periods=k_window).max()
        
        percent_k = ((historical_data['Close'] - lowest_low) / (highest_high - lowest_low)) * 100
        
        percent_k.replace([np.inf, -np.inf], np.nan, inplace=True) 
        condition_zero_range = (highest_high - lowest_low) == 0
        percent_k[condition_zero_range & (historical_data['Close'] == lowest_low)] = 50.0

        percent_d = percent_k.rolling(window=d_window, min_periods=d_window).mean()
        
        return percent_k, percent_d
    except Exception as e:
        print(f"Error calculating Stochastic Oscillator: {e}")
        return empty_series_tuple

# --- Chart Feature Identification ---

def identify_support_resistance(historical_data: pd.DataFrame, window: int = 20) -> Dict[str, Optional[float]]:
    """
    Identifies potential support and resistance levels based on recent lows and highs.
    """
    results: Dict[str, Optional[float]] = {'support': None, 'resistance': None}
    if not isinstance(historical_data, pd.DataFrame):
        print("Error: historical_data must be a pandas DataFrame for S/R identification.")
        return results
    if not all(col in historical_data.columns for col in ['Low', 'High']):
        print("Error: 'Low' and 'High' columns are required in historical_data for S/R.")
        return results
    if not isinstance(window, int) or window <= 0:
        print("Error: window must be a positive integer for S/R.")
        return results
    if len(historical_data) < window:
        print(f"Error: Not enough data ({len(historical_data)} points) for S/R window {window}.")
        return results

    try:
        support = historical_data['Low'].rolling(window=window, min_periods=max(1, window//2)).min().iloc[-1]
        resistance = historical_data['High'].rolling(window=window, min_periods=max(1, window//2)).max().iloc[-1]
        
        results['support'] = float(support) if pd.notna(support) else None
        results['resistance'] = float(resistance) if pd.notna(resistance) else None
        
        return results
    except IndexError: 
        print(f"Error: Not enough data points after rolling for S/R window {window}.")
        return {'support': None, 'resistance': None}
    except Exception as e:
        print(f"Error identifying support/resistance: {e}")
        return {'support': None, 'resistance': None}

def detect_price_gap(current_data: Dict[str, Any], historical_data: pd.DataFrame, gap_threshold_percentage: float = 1.0) -> Optional[Dict[str, Any]]:
    """
    Detects significant price gaps between previous close and current open.
    """
    if not isinstance(current_data, dict):
        print("Error: current_data must be a dictionary for gap detection.")
        return None
    if not isinstance(historical_data, pd.DataFrame):
        print("Error: historical_data must be a pandas DataFrame for gap detection.")
        return None

    current_open = current_data.get('opening_price', current_data.get('open'))

    if current_open is None:
        print("Error: 'opening_price' (or 'open') not found in current_data for gap detection.")
        return None
        
    if 'Close' not in historical_data.columns:
        print("Error: 'Close' column not found in historical_data for gap detection.")
        return None
    if historical_data.empty or len(historical_data['Close'].dropna()) == 0:
        print("Error: Historical data is empty or has no 'Close' prices for gap detection.")
        return None

    try:
        previous_close = historical_data['Close'].dropna().iloc[-1]
        
        if not isinstance(current_open, (int, float)) or not isinstance(previous_close, (int, float)):
            print("Error: current_open or previous_close is not a valid number for gap calculation.")
            return None

        if previous_close == 0: 
            print("Warning: Previous close was 0, cannot calculate gap percentage.")
            return None

        gap = current_open - previous_close
        gap_percentage = (gap / previous_close) * 100

        if abs(gap_percentage) >= gap_threshold_percentage:
            gap_type = 'up' if gap > 0 else 'down'
            return {
                'type': gap_type,
                'gap_percentage': round(gap_percentage, 2),
                'open_price': float(current_open),
                'previous_close': float(previous_close)
            }
        return None
    except IndexError:
        print("Error: Could not retrieve previous_close from historical_data (empty or all NaN after dropna).")
        return None
    except Exception as e:
        print(f"Error detecting price gap: {e}")
        return None

def detect_unusual_volume(current_data: Dict[str, Any], historical_data: pd.DataFrame, lookback_period: int = 20, threshold_multiplier: float = 2.0) -> Optional[Dict[str, Any]]:
    """
    Detects significantly unusual current volume compared to average historical volume.
    """
    if not isinstance(current_data, dict):
        print("Error: current_data must be a dictionary for unusual volume detection.")
        return None
    
    current_volume = current_data.get('volume')
    if current_volume is None:
        print("Error: 'volume' not found in current_data for unusual volume detection.")
        return None
    if not isinstance(current_volume, (int, float)):
        print("Error: current_volume is not a valid number.")
        return None

    average_volume = None
    if 'avg_volume' in current_data and current_data['avg_volume'] is not None: 
        average_volume = current_data['avg_volume']
    elif 'averageDailyVolume10Day' in current_data and current_data['averageDailyVolume10Day'] is not None: 
        average_volume = current_data['averageDailyVolume10Day']
    elif 'averageVolume' in current_data and current_data['averageVolume'] is not None: 
        average_volume = current_data['averageVolume']
    
    if average_volume is None: 
        if not isinstance(historical_data, pd.DataFrame):
            print("Warning: historical_data is not a DataFrame, cannot calculate average volume.")
        elif 'Volume' not in historical_data.columns:
            print("Warning: 'Volume' column not found in historical_data, cannot calculate average volume.")
        elif len(historical_data) < 1: 
             print(f"Warning: Not enough historical data ({len(historical_data)} points) to calculate average volume.")
        else:
            try:
                valid_volumes = historical_data['Volume'].dropna()
                if len(valid_volumes) >= 1 : 
                    actual_lookback = min(lookback_period, len(valid_volumes))
                    if actual_lookback > 0:
                        average_volume = valid_volumes.tail(actual_lookback).mean()
                    else:
                        print("Warning: No valid volume data points for averaging.")
                else:
                    print("Warning: No valid volume data in historical_data for averaging.")
            except Exception as e:
                print(f"Error calculating average volume from historical_data: {e}")
    
    if average_volume is None or not isinstance(average_volume, (int, float)) or average_volume == 0:
        print("Warning: Average volume is not available or is zero, cannot detect unusual volume.")
        return None

    try:
        if float(current_volume) > float(average_volume) * threshold_multiplier:
            return {
                'current_volume': int(current_volume),
                'average_volume': round(float(average_volume), 2),
                'threshold_multiplier': threshold_multiplier,
                'signal': 'High Volume Spike'
            }
        return None
    except Exception as e:
        print(f"Error comparing volumes: {e}")
        return None

# --- Volatility Analysis ---

def calculate_average_true_range(historical_data: pd.DataFrame, window: int = 14) -> pd.Series:
    """
    Calculates the Average True Range (ATR).

    Args:
        historical_data: Pandas DataFrame with 'High', 'Low', 'Close' columns.
        window: The window period for ATR (typically 14).

    Returns:
        A pandas Series with ATR values, or an empty Series if an error occurs.
    """
    required_cols = ['High', 'Low', 'Close']
    if not isinstance(historical_data, pd.DataFrame):
        print("Error: historical_data must be a pandas DataFrame for ATR.")
        return pd.Series(dtype=float)
    if not all(col in historical_data.columns for col in required_cols):
        print(f"Error: historical_data must contain {', '.join(required_cols)} columns for ATR.")
        return pd.Series(dtype=float)
    if not isinstance(window, int) or window <= 0:
        print("Error: window must be a positive integer for ATR.")
        return pd.Series(dtype=float)
    # Need at least `window` periods for the SMA of TR, and 1 prior period for Close.shift().
    if len(historical_data) < window + 1:
        print(f"Error: Not enough data ({len(historical_data)} points) for ATR window {window}.")
        return pd.Series(dtype=float)

    try:
        high_low = historical_data['High'] - historical_data['Low']
        high_prev_close = np.abs(historical_data['High'] - historical_data['Close'].shift(1))
        low_prev_close = np.abs(historical_data['Low'] - historical_data['Close'].shift(1))
        
        # Create a DataFrame for TR components to handle NaNs correctly during max calculation
        tr_df = pd.DataFrame({
            'hl': high_low, 
            'hpc': high_prev_close, 
            'lpc': low_prev_close
        })
        
        true_range = tr_df.max(axis=1, skipna=False) # skipna=False to propagate NaN if all components are NaN for a row
        
        # The first TR value will be NaN due to Close.shift(1).
        # Calculate SMA of TR. min_periods=window ensures that the first ATR value is based on a full window of TRs.
        atr = true_range.rolling(window=window, min_periods=window).mean()
        
        return atr
    except Exception as e:
        print(f"Error calculating ATR: {e}")
        return pd.Series(dtype=float)

def check_volatility(historical_data: pd.DataFrame, current_data: dict, atr_period: int = 14) -> Optional[Dict[str, Any]]:
    """
    Checks current price volatility based on ATR.

    Args:
        historical_data: Pandas DataFrame for ATR calculation.
        current_data: Dictionary containing 'current_price'.
        atr_period: The window period for ATR calculation.

    Returns:
        A dictionary {'atr': float, 'atr_percentage': float, 'volatility_signal': str} or None.
    """
    if not isinstance(current_data, dict) or 'current_price' not in current_data or current_data['current_price'] is None:
        print("Error: current_data must be a dict with a valid 'current_price' for volatility check.")
        return None
    
    current_price = current_data['current_price']
    if not isinstance(current_price, (int, float)) or current_price <= 0:
        print("Error: Invalid current_price for volatility check.")
        return None

    atr_series = calculate_average_true_range(historical_data, window=atr_period)
    if atr_series.empty or atr_series.isna().all():
        print("Warning: ATR could not be calculated or is all NaN.")
        return None

    try:
        latest_atr = atr_series.dropna().iloc[-1]
        if not isinstance(latest_atr, (int, float)) or latest_atr < 0: # ATR shouldn't be negative
            print("Warning: Invalid latest ATR value.")
            return None
            
        atr_percentage = (latest_atr / current_price) * 100
        
        volatility_signal = "Moderate" # Default
        if atr_percentage > 5.0:
            volatility_signal = "High"
        elif atr_percentage < 2.0:
            volatility_signal = "Low"
            
        return {
            'atr': round(float(latest_atr), 4), 
            'atr_percentage': round(float(atr_percentage), 2), 
            'volatility_signal': volatility_signal
        }
    except IndexError: # If dropna().iloc[-1] fails
        print("Warning: Not enough valid ATR values to determine latest ATR.")
        return None
    except Exception as e:
        print(f"Error in check_volatility: {e}")
        return None

# Example usage in __main__
if __name__ == '__main__':
    # Create sample historical data (ensure enough rows for ATR calculation)
    data = {
        'High': [10, 12, 11, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30],
        'Low':  [9,  10, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28],
        'Close':[10, 11, 10.5,12.5,13, 14.5,15, 16.5,17, 18.5,19, 20.5,21, 22.5,23, 24.5,25, 26.5,27, 28.5, 29],
        'Volume':[1000,1200,1100,1300,1400,1500,1600,1700,1800,1900,2000,2100,2200,2300,2400,2500,2600,2700,2800,2900,3000]
    }
    # Ensure index is DatetimeIndex for time series operations if any part of yfinance expects it
    # For these functions, it's not strictly necessary but good practice.
    sample_dates = pd.date_range(start='2023-01-01', periods=len(data['High']))
    sample_historical_data = pd.DataFrame(data, index=sample_dates)

    print("--- Testing Technical Analysis Functions ---")

    # Test ATR
    print("\nTesting ATR Calculation (window=14):")
    atr_values = calculate_average_true_range(sample_historical_data, window=14)
    print("ATR Series (last 5):")
    print(atr_values.tail())
    if not atr_values.empty and atr_values.notna().any():
        print(f"Latest ATR: {atr_values.dropna().iloc[-1]:.2f}")

    # Test Volatility Check
    print("\nTesting Volatility Check:")
    sample_current_data_vol = {'current_price': 29.50} # Price slightly above last close
    volatility_info = check_volatility(sample_historical_data, sample_current_data_vol, atr_period=14)
    if volatility_info:
        print(f"Volatility Info: {volatility_info}")
    else:
        print("Volatility Info: Could not be determined.")

    sample_current_data_high_vol = {'current_price': 15.0} # Lower price, ATR will be higher percentage
    volatility_info_high = check_volatility(sample_historical_data.head(15), sample_current_data_high_vol, atr_period=10) # Shorter data and period
    if volatility_info_high:
        print(f"Volatility Info (High Case): {volatility_info_high}")
    else:
        print("Volatility Info (High Case): Could not be determined.")
    
    print("\n--- Testing with insufficient data for ATR ---")
    short_historical_data = sample_historical_data.head(10) # Only 10 data points
    atr_short = calculate_average_true_range(short_historical_data, window=14)
    print(f"ATR with insufficient data (10 points, 14 window): {atr_short}") # Should be empty or all NaN and print error
    
    vol_check_short = check_volatility(short_historical_data, sample_current_data_vol, atr_period=14)
    print(f"Volatility check with insufficient data for ATR: {vol_check_short}") # Should be None

    print("\n--- Technical Analysis Testing Complete ---")

[end of stock_analyzer_agent/agent/technical_analysis.py]
