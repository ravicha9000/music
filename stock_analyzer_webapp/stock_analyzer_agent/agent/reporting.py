# This file will contain modules for generating reports.
from datetime import datetime
from typing import Dict, Any, Optional # Using Optional for type hints
# import pandas as pd # For pd.DataFrame, pd.Series if we pass them directly

# Placeholder for data structures (as comments)
# current_data: {
#     "current_price": float | None,
#     "daily_high": float | None,
#     "daily_low": float | None,
#     "opening_price": float | None, 
#     "previous_close": float | None, 
#     "percentage_change": float | None, # e.g., 0.02 for +2%
#     "volume": int | None,
#     "avg_volume": int | None, # Or float
#     "data_timestamp_utc": str | None, # e.g., "2023-10-27 14:30:00 UTC"
#     "market_state": str | None, # e.g., "REGULAR", "PRE", "POST", "CLOSED"
#     "currency": str | None,
#     "exchange": str | None,
#     "short_name": str | None,
#     "status_message": str | None
# }
# technical_indicators: {
#     "sma_20": float | None,
#     "sma_50": float | None,
#     "sma_200": float | None,
#     "rsi": float | None,
#     "macd_line": float | None,
#     "macd_signal": float | None,
#     "macd_hist": float | None,
#     "bb_upper": float | None,
#     "bb_middle": float | None,
#     "bb_lower": float | None,
#     "stoch_k": float | None,
#     "stoch_d": float | None,
#     "volatility_info": Dict[str, Any] | None # e.g. {'atr': 1.5, 'atr_percentage': 1.0, 'volatility_signal': 'Moderate'}
# }
# fundamental_data: { 
#     # ... (same as before)
# }
# chart_features: {
#     # ... (same as before)
# }

def format_price(price: Optional[float]) -> str:
    """Formats a price to 2 decimal places, or returns 'N/A'."""
    if price is None or price != price: 
        return "N/A"
    try:
        return f"{price:.2f}"
    except (TypeError, ValueError):
        return "N/A"

def format_percentage(value: Optional[float], multiply: bool = True) -> str:
    """
    Formats a float as a percentage (e.g., 0.15 -> '15.00%'), or 'N/A'.
    If multiply is False, assumes value is already in percent form (e.g. 15.0 for 15%).
    """
    if value is None or value != value or (isinstance(value, str) and value == "N/A"):
        return "N/A"
    try:
        num_value = float(value)
        if multiply:
            return f"{num_value * 100:.2f}%"
        else:
            return f"{num_value:.2f}%"
    except (TypeError, ValueError):
        return "N/A"

def format_volume(volume: Optional[int | float]) -> str:
    """Formats volume with commas (e.g., 1234567 -> '1,234,567'), or 'N/A'."""
    if volume is None or volume != volume: 
        return "N/A"
    try:
        return f"{int(volume):,}"
    except (TypeError, ValueError):
        return "N/A"

def format_timestamp(ts: Optional[int | float | datetime | str]) -> str: # Added str for pre-formatted ts
    """
    Converts a UNIX timestamp, datetime object, or existing string to a readable string ('YYYY-MM-DD HH:MM:SS'), or 'N/A'.
    """
    if ts is None:
        return "N/A"
    if isinstance(ts, str): # If already formatted or "N/A"
        return ts 
    try:
        if isinstance(ts, datetime):
            dt_object = ts
        else:
            dt_object = datetime.fromtimestamp(float(ts))
        return dt_object.strftime('%Y-%m-%d %H:%MM:%SS') # Removed %Z as yfinance usually gives local market time
    except (TypeError, ValueError, OSError): 
        return "N/A"

def format_value(value: Any, precision: int = 2, is_ratio: bool = False) -> str:
    """General formatter for numeric values, can be extended."""
    if value is None or (isinstance(value, float) and value != value): 
        return "N/A"
    try:
        if is_ratio: 
             return f"{float(value):.{precision}f}x" if isinstance(value, (int, float)) else str(value)
        return f"{float(value):.{precision}f}"
    except (TypeError, ValueError):
        return str(value) 

# --- Day Trader Report ---
def generate_day_trader_report(
    ticker: str, 
    current_data: Dict[str, Any], 
    technical_indicators: Dict[str, Any], 
    analysis_timestamp: datetime, # This is the agent's analysis time
    chart_features: Optional[Dict[str, Any]] = None
) -> str:
    report_lines = []
    
    report_lines.append(f"--- Day Trader Report for {ticker.upper()} ---")
    report_lines.append(f"Agent Analysis Time: {format_timestamp(analysis_timestamp)}")
    report_lines.append(f"Market Data As Of:   {format_timestamp(current_data.get('data_timestamp_utc', 'N/A'))}")
    report_lines.append(f"Market Status:       {current_data.get('market_state', 'N/A')}")
    report_lines.append("-" * 40)

    report_lines.append("Price Action:")
    current_price = current_data.get('current_price')
    report_lines.append(f"  Current Price: {format_price(current_price)}")
    report_lines.append(f"  Day High:      {format_price(current_data.get('daily_high'))}")
    report_lines.append(f"  Day Low:       {format_price(current_data.get('daily_low'))}")
    report_lines.append(f"  Open:          {format_price(current_data.get('opening_price'))}")
    
    percentage_change = current_data.get('percentage_change')
    if percentage_change is None and current_price is not None and current_data.get('previous_close') is not None:
        prev_close = current_data.get('previous_close')
        if prev_close and prev_close != 0: 
            percentage_change = (current_price - prev_close) / prev_close
    report_lines.append(f"  Change:        {format_percentage(percentage_change)}")
    report_lines.append("-" * 40)

    report_lines.append("Volume & Volatility:")
    current_volume = current_data.get('volume')
    avg_volume = current_data.get('avg_volume')
    report_lines.append(f"  Current Volume: {format_volume(current_volume)}")
    report_lines.append(f"  Avg Volume:     {format_volume(avg_volume)}")
    
    volume_pct_change = None
    if current_volume is not None and avg_volume is not None and avg_volume != 0:
        volume_pct_change = (current_volume - avg_volume) / avg_volume
    volume_vs_avg_str = format_percentage(volume_pct_change)
    if volume_pct_change is not None:
        if volume_pct_change > 0.2: volume_vs_avg_str += " (Strong)"
        elif volume_pct_change < -0.2: volume_vs_avg_str += " (Weak)"
    report_lines.append(f"  Volume vs Avg:  {volume_vs_avg_str}")

    volatility_info = technical_indicators.get('volatility_info')
    if volatility_info and isinstance(volatility_info, dict):
        atr_val = format_price(volatility_info.get('atr'))
        vol_signal = volatility_info.get('volatility_signal', 'N/A')
        report_lines.append(f"  Volatility:     {vol_signal} (ATR: {atr_val})")
    else:
        report_lines.append("  Volatility:     N/A")
    report_lines.append("-" * 40)


    report_lines.append("Key Technical Signals & Chart Observations:")
    if chart_features:
        has_chart_features = False
        if chart_features.get('support') is not None:
            report_lines.append(f"  Potential Support:    {format_price(chart_features.get('support'))}"); has_chart_features = True
        if chart_features.get('resistance') is not None:
            report_lines.append(f"  Potential Resistance: {format_price(chart_features.get('resistance'))}"); has_chart_features = True
        price_gap_info = chart_features.get('price_gap_info')
        if price_gap_info:
            report_lines.append(f"  Price Gap Detected:   {price_gap_info.get('type','N/A').capitalize()} gap of {format_percentage(price_gap_info.get('gap_percentage'), multiply=False)} "
                                f"at open ({format_price(price_gap_info.get('open_price'))} vs prev close {format_price(price_gap_info.get('previous_close'))})."); has_chart_features = True
        unusual_volume_info = chart_features.get('unusual_volume_info') # This is also in Volume section now
        if unusual_volume_info and volume_vs_avg_str == "N/A": # Only if not covered by general volume line
            report_lines.append(f"  Unusual Volume Note:  Current volume ({format_volume(unusual_volume_info.get('current_volume'))}) "
                                f"is significantly higher than average ({format_volume(unusual_volume_info.get('average_volume'))})."); has_chart_features = True
        if has_chart_features: report_lines.append("-" * 40)

    rsi = technical_indicators.get('rsi')
    rsi_str = format_price(rsi)
    if rsi is not None and rsi_str != "N/A":
        if rsi > 70: rsi_str += " (Overbought >70)"
        elif rsi < 30: rsi_str += " (Oversold <30)"
        else: rsi_str += " (Neutral)"
    report_lines.append(f"  RSI (14):      {rsi_str}")

    sma_20 = technical_indicators.get('sma_20'); sma_50 = technical_indicators.get('sma_50')
    if current_price is not None and format_price(current_price) != "N/A":
        if sma_20 is not None and format_price(sma_20) != "N/A":
            pos_20 = "Above" if current_price > sma_20 else "Below" if current_price < sma_20 else "At"
            report_lines.append(f"  Price vs SMA20 ({format_price(sma_20)}): {pos_20}")
        if sma_50 is not None and format_price(sma_50) != "N/A":
            pos_50 = "Above" if current_price > sma_50 else "Below" if current_price < sma_50 else "At"
            report_lines.append(f"  Price vs SMA50 ({format_price(sma_50)}): {pos_50}")
    
    macd_line = technical_indicators.get('macd_line'); macd_signal_line = technical_indicators.get('macd_signal'); macd_hist = technical_indicators.get('macd_hist')
    macd_interpretation = "N/A"
    if macd_hist is not None and format_price(macd_hist) != "N/A":
        if macd_hist > 0: macd_interpretation = "Bullish Momentum"
        elif macd_hist < 0: macd_interpretation = "Bearish Momentum"
        else: macd_interpretation = "Neutral"
    report_lines.append(f"  MACD ({format_price(macd_line)}), Signal ({format_price(macd_signal_line)}), Hist ({format_price(macd_hist)})")
    if macd_interpretation != "N/A": report_lines.append(f"    Interpretation: {macd_interpretation}")

    bb_upper = technical_indicators.get('bb_upper'); bb_middle = technical_indicators.get('bb_middle'); bb_lower = technical_indicators.get('bb_lower')
    bb_pos = "N/A"
    if current_price is not None and format_price(current_price) != "N/A" and all(val is not None and format_price(val) != "N/A" for val in [bb_upper, bb_middle, bb_lower]):
        if current_price > bb_upper: bb_pos = f"Above Upper Band ({format_price(bb_upper)}) - Potential Overbought/Breakout"
        elif current_price < bb_lower: bb_pos = f"Below Lower Band ({format_price(bb_lower)}) - Potential Oversold/Breakdown"
        elif abs(current_price - bb_middle) < (bb_upper - bb_lower) * 0.1 : bb_pos = f"Near Middle Band ({format_price(bb_middle)})"
        elif current_price > bb_middle: bb_pos = f"Between Middle ({format_price(bb_middle)}) and Upper ({format_price(bb_upper)})"
        else: bb_pos = f"Between Middle ({format_price(bb_middle)}) and Lower ({format_price(bb_lower)})"
    report_lines.append(f"  Bollinger Bands: Price is {bb_pos}")

    stoch_k = technical_indicators.get('stoch_k'); stoch_d = technical_indicators.get('stoch_d')
    stoch_str = f"%K={format_price(stoch_k)}, %D={format_price(stoch_d)}"
    if stoch_k is not None and format_price(stoch_k) != "N/A":
        if stoch_k > 80: stoch_str += " (Overbought >80)"
        elif stoch_k < 20: stoch_str += " (Oversold <20)"
        else: stoch_str += " (Neutral)"
    report_lines.append(f"  Stochastic:    {stoch_str}")
    report_lines.append("-" * 40)
    # ... (rest of Day Trader report considerations)
    report_lines.append("Disclaimer: This report is for informational purposes only and not financial advice.")
    return "\n".join(report_lines)

# --- Portfolio Manager Report ---
def generate_portfolio_manager_report(
    ticker: str, 
    current_data: Dict[str, Any], 
    technical_indicators: Dict[str, Any], 
    fundamental_data: Dict[str, Any], 
    analysis_timestamp: datetime, # Agent's analysis time
    chart_features: Optional[Dict[str, Any]] = None
) -> str:
    report_lines = []
    company_name = fundamental_data.get('company_name', ticker.upper())

    report_lines.append(f"--- Portfolio Manager Brief for {company_name} ({ticker.upper()}) ---")
    report_lines.append(f"Agent Analysis Time: {format_timestamp(analysis_timestamp)}")
    report_lines.append(f"Market Data As Of:   {format_timestamp(current_data.get('data_timestamp_utc', 'N/A'))}")
    report_lines.append(f"Market Status:       {current_data.get('market_state', 'N/A')}")
    report_lines.append("=" * 60)
    
    # ... (Executive Summary, Current Performance - ensure they handle N/A gracefully)
    report_lines.append("Executive Summary:") # Simplified for brevity
    current_price = current_data.get('current_price')
    sma_200 = technical_indicators.get('sma_200')
    pe = fundamental_data.get('pe_ratio')
    summary_parts = []
    if format_price(current_price) != "N/A": summary_parts.append(f"Price: {format_price(current_price)}.")
    if format_price(sma_200) != "N/A" and format_price(current_price) != "N/A":
        summary_parts.append(f"Trend: {'Above' if current_price > sma_200 else 'Below'} 200DMA.")
    if format_value(pe, is_ratio=True) != "N/A": summary_parts.append(f"P/E: {format_value(pe, is_ratio=True)}.")
    report_lines.append("  " + " ".join(summary_parts))
    report_lines.append("-" * 60)


    report_lines.append("Technical Analysis & Chart Context:")
    # ... (MA, RSI, MACD lines - ensure N/A checks for interpretations)
    rsi = technical_indicators.get('rsi')
    rsi_str = format_price(rsi)
    if rsi is not None and rsi_str != "N/A":
        if rsi > 70: rsi_str += " (Overbought)"
        elif rsi < 30: rsi_str += " (Oversold)"
    report_lines.append(f"  RSI (14):         {rsi_str}")
    
    # Volatility for PM
    volatility_info = technical_indicators.get('volatility_info')
    if volatility_info and isinstance(volatility_info, dict):
        atr_val = format_price(volatility_info.get('atr'))
        atr_pct = format_percentage(volatility_info.get('atr_percentage'), multiply=False)
        vol_signal = volatility_info.get('volatility_signal', 'N/A')
        report_lines.append(f"  Volatility:       Recent volatility is {vol_signal.lower()}, with ATR at {atr_val} ({atr_pct} of current price).")
    else:
        report_lines.append("  Volatility:       N/A")

    if chart_features: # Already handled N/A for individual items in Day Trader, can be similar here
        s = chart_features.get('support'); r = chart_features.get('resistance')
        if format_price(s) != "N/A" or format_price(r) != "N/A":
            report_lines.append(f"  Key Levels:       Support at {format_price(s)}, Resistance at {format_price(r)}.")
    report_lines.append("-" * 60)
    # ... (Fundamental Analysis, Risk Considerations - ensure they handle N/A)
    report_lines.append("Fundamental Analysis Summary: (Selected)")
    report_lines.append(f"  P/E Ratio:        {format_value(fundamental_data.get('pe_ratio'), is_ratio=True)}")
    report_lines.append(f"  EPS Growth (TTM): {format_percentage(fundamental_data.get('eps_growth_ttm'))}")
    report_lines.append("-" * 60)
    report_lines.append("Disclaimer: This brief is for informational purposes and not a specific recommendation.")
    return "\n".join(report_lines)

# --- Beginner Investor Report ---
def generate_beginner_investor_report(
    ticker: str, 
    current_data: Dict[str, Any], 
    technical_indicators: Dict[str, Any], 
    fundamental_data: Dict[str, Any], 
    analysis_timestamp: datetime, # Agent's analysis time
    chart_features: Optional[Dict[str, Any]] = None
) -> str:
    report_lines = []
    company_name = fundamental_data.get('company_name', ticker.upper())

    report_lines.append(f"--- Learning About {company_name} ({ticker.upper()}) ---")
    report_lines.append(f"Agent Analysis Time: {format_timestamp(analysis_timestamp)}")
    report_lines.append(f"Market Data As Of:   {format_timestamp(current_data.get('data_timestamp_utc', 'N/A'))}")
    report_lines.append(f"Market Status:       {current_data.get('market_state', 'N/A')}")
    report_lines.append("Hello! This report helps you understand some key things about this stock.")
    report_lines.append("=" * 60)
    
    # ... (Price, Volume - ensure N/A checks)

    report_lines.append("Learning About Technical Indicators & What the Chart Might Be Showing:")
    # Volatility for Beginner
    volatility_info = technical_indicators.get('volatility_info')
    if volatility_info and isinstance(volatility_info, dict):
        vol_signal = volatility_info.get('volatility_signal', 'N/A').lower()
        if vol_signal != "n/a":
            report_lines.append(f"\n  Volatility Check: Volatility tells us how much the price might swing. It's currently {vol_signal}. "
                                f"A '{vol_signal}' volatility stock can have {'bigger' if vol_signal == 'high' else 'smaller' if vol_signal == 'low' else 'moderate'} price changes quickly.")
        else:
            report_lines.append("\n  Volatility Check: Information not available.")
    
    rsi = technical_indicators.get('rsi')
    rsi_expl = format_price(rsi)
    if rsi is not None and rsi_expl != "N/A":
        rsi_expl += ". "
        if rsi > 70: rsi_expl += "This is generally considered 'overbought' (might drop)"
        elif rsi < 30: rsi_expl += "This is generally considered 'oversold' (might rise)"
        else: rsi_expl += "This is in the neutral range."
    else: rsi_expl = "N/A"
    report_lines.append(f"\n  RSI (Relative Strength Index): {rsi_expl}")
    report_lines.append("    (RSI measures how quickly the stock price has been going up or down.)")
    # ... (Rest of beginner report, ensuring N/A checks for interpretations)
    report_lines.append("-" * 60)
    report_lines.append("Disclaimer: This report is for educational purposes. Consult a financial advisor.")
    return "\n".join(report_lines)


# --- Main Report Orchestrator ---
def generate_stock_report(
    ticker: str, 
    user_type: str, 
    current_data: Dict[str, Any], 
    technical_indicators: Dict[str, Any], # Now includes volatility_info
    fundamental_data: Optional[Dict[str, Any]] = None, 
    chart_features: Optional[Dict[str, Any]] = None, 
    analysis_timestamp: Optional[datetime] = None # Agent's analysis time
) -> str:
    if analysis_timestamp is None:
        analysis_timestamp = datetime.now()

    user_type_lower = user_type.lower()

    # Basic check for essential current_data fields beyond just existence
    if not current_data or current_data.get('current_price') is None and current_data.get('market_state') is None :
         return f"Error: Essential current data (price, market state) is missing for {ticker}."

    if user_type_lower == 'day_trader':
        if not technical_indicators: # technical_indicators is now expected to have volatility_info
            return "Error: Technical indicators (including volatility) are required for Day Trader report."
        return generate_day_trader_report(ticker, current_data, technical_indicators, analysis_timestamp, chart_features)
    
    elif user_type_lower == 'portfolio_manager':
        if not technical_indicators or not fundamental_data:
            return "Error: Technical indicators (incl. volatility) and fundamental data are required for Portfolio Manager report."
        return generate_portfolio_manager_report(ticker, current_data, technical_indicators, fundamental_data, analysis_timestamp, chart_features)
        
    elif user_type_lower == 'beginner_investor':
        if not technical_indicators or not fundamental_data:
            return "Error: Technical indicators (incl. volatility) and fundamental data are required for Beginner Investor report."
        return generate_beginner_investor_report(ticker, current_data, technical_indicators, fundamental_data, analysis_timestamp, chart_features)
        
    else:
        return f"Error: Report type '{user_type}' is not supported yet."

# Example Usage
if __name__ == '__main__':
    agent_analysis_time = datetime.now()
    
    sample_current_data_updated = {
        "current_price": 150.25, "daily_high": 152.50, "daily_low": 149.75,
        "opening_price": 155.00, "previous_close": 148.00, 
        "volume": 2_500_000, "avg_volume": 1_000_000,
        "data_timestamp_utc": "2023-10-27 16:00:00 UTC", # Example
        "market_state": "CLOSED", # Example
        "currency": "USD", "exchange": "NASDAQ", "short_name": "StockCo Inc."
    }
    sample_technical_indicators_updated = {
        "sma_20": 148.50, "sma_50": 145.00, "sma_200": 130.00,
        "rsi": 65.0, "macd_line": 1.25, "macd_signal": 1.10, "macd_hist": 0.15,
        "bb_upper": 155.00, "bb_middle": 150.00, "bb_lower": 145.00,
        "stoch_k": 70.0, "stoch_d": 65.0,
        "volatility_info": {'atr': 3.52, 'atr_percentage': 2.34, 'volatility_signal': 'Moderate'}
    }
    sample_technical_indicators_na = { # For testing N/A handling
        "sma_20": None, "sma_50": 145.00, "sma_200": None,
        "rsi": None, "macd_line": None, "macd_signal": None, "macd_hist": None,
        "bb_upper": None, "bb_middle": None, "bb_lower": None,
        "stoch_k": None, "stoch_d": None,
        "volatility_info": {'atr': 0.75, 'atr_percentage': 0.5, 'volatility_signal': 'Low'} # Low vol example
    }
    # (fundamental_data and chart_features remain same as previous example)
    sample_fundamental_data = {
        "company_name": "Global Consolidated Corp", "sector": "Technology", "industry": "Software",
        "pe_ratio": 25.5, "latest_eps": 5.90, "eps_growth_ttm": 0.15, "revenue_growth_yoy": 0.12, 
        "net_profit_margin": 0.22, "debt_to_equity": 0.5, "return_on_equity": 0.18
    }
    sample_chart_features = {
        "support": 140.00, "resistance": 160.00,
        "price_gap_info": { 'type': 'up', 'gap_percentage': 4.73, 'open_price': 155.00, 'previous_close': 148.00 },
        "unusual_volume_info": { 'current_volume': 2_500_000, 'average_volume': 1_000_000, 'signal': 'High Volume Spike'}
    }

    print("--- Generating Day Trader Report (Updated Example) ---")
    dt_report = generate_stock_report(
        "XYZ", 'day_trader', sample_current_data_updated, 
        sample_technical_indicators_updated, chart_features=sample_chart_features, 
        analysis_timestamp=agent_analysis_time
    )
    print(dt_report)

    print("\n\n--- Generating Portfolio Manager Report (Updated Example) ---")
    pm_report = generate_stock_report(
        "XYZ", 'portfolio_manager', sample_current_data_updated, 
        sample_technical_indicators_updated, fundamental_data=sample_fundamental_data, 
        chart_features=sample_chart_features, analysis_timestamp=agent_analysis_time
    )
    print(pm_report)

    print("\n\n--- Generating Beginner Investor Report (Updated Example) ---")
    bi_report = generate_stock_report(
        "XYZ", 'beginner_investor', sample_current_data_updated, 
        sample_technical_indicators_updated, fundamental_data=sample_fundamental_data,
        chart_features=sample_chart_features, analysis_timestamp=agent_analysis_time
    )
    print(bi_report)
    
    print("\n\n--- Generating Day Trader Report (N/A Technicals Example) ---")
    dt_report_na = generate_stock_report(
        "NA_TEST", 'day_trader', sample_current_data_updated, 
        sample_technical_indicators_na, chart_features=None, 
        analysis_timestamp=agent_analysis_time
    )
    print(dt_report_na)

[end of stock_analyzer_agent/agent/reporting.py]
