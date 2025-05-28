# This file will contain modules for fetching real-time and historical stock data.
import yfinance as yf
import pandas as pd
from datetime import datetime, timezone # Added timezone

def get_current_stock_data(ticker_symbol: str) -> dict:
    """
    Fetches current market data for the given ticker_symbol.

    Args:
        ticker_symbol: The stock ticker symbol (e.g., "AAPL").

    Returns:
        A dictionary containing current stock data, or an empty dictionary if an error occurs
        or critical data is missing.
        Includes 'data_timestamp_utc', 'market_state'.
    """
    data = {
        "current_price": None,
        "daily_high": None,
        "daily_low": None,
        "opening_price": None,
        "previous_close": None,
        "volume": None,
        "market_cap": None,
        "data_timestamp_utc": None,
        "market_state": None,
        "currency": None, # Added for context
        "exchange": None, # Added for context
        "short_name": None, # Added for context
        "status_message": None # To indicate data availability issues
    }
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        
        if not info or len(info) < 10: # Heuristic: if info is very sparse, it might be a bad ticker or delisted
            data["status_message"] = f"Limited or no information found for {ticker_symbol}. It might be delisted or an invalid ticker."
            print(f"Warning: {data['status_message']}")
            # Return mostly None values if info is too limited
            return data

        # Extracting data with fallbacks
        data["current_price"] = info.get("currentPrice", info.get("regularMarketPrice", info.get("ask"))) # ask as last resort
        data["daily_high"] = info.get("dayHigh")
        data["daily_low"] = info.get("dayLow")
        data["opening_price"] = info.get("open", info.get("regularMarketOpen"))
        data["previous_close"] = info.get("previousClose", info.get("regularMarketPreviousClose"))
        data["volume"] = info.get("volume", info.get("regularMarketVolume"))
        data["market_cap"] = info.get("marketCap")
        data["currency"] = info.get("currency")
        data["exchange"] = info.get("exchangeName", info.get("exchange"))
        data["short_name"] = info.get("shortName", info.get("longName"))

        # Timestamp handling
        timestamp_sources = ["regularMarketTime", "postMarketTime", "preMarketTime"]
        data_timestamp = None
        for source_key in timestamp_sources:
            if info.get(source_key) is not None:
                data_timestamp = info.get(source_key)
                break
        
        if data_timestamp:
            try:
                # Assuming timestamp is UNIX epoch time
                dt_object_utc = datetime.fromtimestamp(int(data_timestamp), timezone.utc)
                data["data_timestamp_utc"] = dt_object_utc.strftime('%Y-%m-%d %H:%M:%S %Z')
            except (TypeError, ValueError) as e:
                print(f"Warning: Could not parse data timestamp '{data_timestamp}' for {ticker_symbol}: {e}")
                data["data_timestamp_utc"] = "N/A (parse error)"
        else:
            data["data_timestamp_utc"] = "N/A (no source)"

        # Market state
        data["market_state"] = info.get("marketState", "N/A")
        if data["market_state"] == "N/A" and info.get("regularMarketPrice") is not None: # Infer if possible
             data["market_state"] = "REGULAR (inferred)"


        # Check for critical missing data
        if data["current_price"] is None and data["opening_price"] is None :
            data["status_message"] = f"Critical price data (current/open) is missing for {ticker_symbol}. Data may be stale or unavailable."
            print(f"Warning: {data['status_message']}")
            # Optionally, could return a dictionary with fewer fields or set more to None
            # For now, we return what we have with the status message

        return data
        
    except Exception as e:
        print(f"Error fetching current data for {ticker_symbol}: {e}")
        data["status_message"] = f"Exception during data fetching: {str(e)}"
        # Return mostly None values on major exception
        for key in ["current_price", "daily_high", "daily_low", "opening_price", "previous_close", "volume", "market_cap"]:
            data[key] = None
        data["market_state"] = "Error"
        return data

def get_historical_stock_data(ticker_symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """
    Fetches historical stock data (OHLCV) for the given ticker_symbol.

    Args:
        ticker_symbol: The stock ticker symbol (e.g., "AAPL").
        period: The period for which to fetch data (e.g., "1d", "5d", "1mo", "1y", "max").
        interval: The interval of data points (e.g., "1m", "5m", "15m", "1h", "1d", "1wk").

    Returns:
        A pandas DataFrame containing historical OHLCV data, or an empty DataFrame if an error occurs.
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        history = ticker.history(period=period, interval=interval)
        if history.empty:
            print(f"Warning: No historical data found for {ticker_symbol} with period={period} and interval={interval}.")
        return history
    except Exception as e:
        print(f"Error fetching historical data for {ticker_symbol}: {e}")
        return pd.DataFrame()

if __name__ == '__main__':
    print("--- Testing Data Collection ---")
    
    # Test with a valid ticker
    sample_ticker_valid = "AAPL"
    print(f"\nFetching current data for {sample_ticker_valid}...")
    current_data_valid = get_current_stock_data(sample_ticker_valid)
    print(f"Current Data ({sample_ticker_valid}):")
    for key, value in current_data_valid.items():
        print(f"  {key}: {value}")

    print(f"\nFetching historical data for {sample_ticker_valid} (last 5 days)...")
    historical_data_valid = get_historical_stock_data(sample_ticker_valid, period="5d", interval="1d")
    print(f"Historical Data ({sample_ticker_valid}):")
    print(historical_data_valid.head())

    # Test with a potentially problematic ticker (e.g., one that might be delisted or have limited info)
    sample_ticker_problem = "FTRCQ" # Example of a delisted/problematic stock
    print(f"\nFetching current data for {sample_ticker_problem}...")
    current_data_problem = get_current_stock_data(sample_ticker_problem)
    print(f"Current Data ({sample_ticker_problem}):")
    for key, value in current_data_problem.items():
        print(f"  {key}: {value}")
    
    # Test with an invalid ticker
    sample_ticker_invalid = "INVALIDTICKERXYZ123"
    print(f"\nFetching current data for {sample_ticker_invalid}...")
    current_data_invalid = get_current_stock_data(sample_ticker_invalid)
    print(f"Current Data ({sample_ticker_invalid}):")
    for key, value in current_data_invalid.items():
        print(f"  {key}: {value}")

    print(f"\nFetching historical data for {sample_ticker_invalid}...")
    historical_data_invalid = get_historical_stock_data(sample_ticker_invalid)
    print(f"Historical Data ({sample_ticker_invalid}):")
    print(historical_data_invalid)

    # Example of a stock that might be in PRE or POST market state if tested during those times
    # For consistent testing, the market state will usually be CLOSED or REGULAR depending on when this is run.
    # sample_ticker_market_state = "MSFT" 
    # print(f"\nFetching current data for {sample_ticker_market_state} to check market state...")
    # current_data_ms = get_current_stock_data(sample_ticker_market_state)
    # print(f"Market State for {sample_ticker_market_state}: {current_data_ms.get('market_state')}")
    # print(f"Data Timestamp for {sample_ticker_market_state}: {current_data_ms.get('data_timestamp_utc')}")

    # Test a non-US stock to see how timestamp/market state behaves
    # sample_ticker_non_us = "BARC.L" # Barclays PLC on LSE
    # print(f"\nFetching current data for {sample_ticker_non_us} (Non-US)...")
    # current_data_non_us = get_current_stock_data(sample_ticker_non_us)
    # print(f"Current Data ({sample_ticker_non_us}):")
    # for key, value in current_data_non_us.items():
    #     print(f"  {key}: {value}")

    print("\n--- Data Collection Testing Complete ---")
