# This file will contain modules for fetching and analyzing fundamental data.
import yfinance as yf
import pandas as pd
from datetime import datetime

def get_company_info(ticker_symbol: str) -> dict | None:
    """
    Fetches the company information dictionary from yfinance.

    Args:
        ticker_symbol: The stock ticker symbol (e.g., "AAPL").

    Returns:
        A dictionary containing company information, or None if an error occurs or info is empty.
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        if not info: # Check if info dictionary is empty
            print(f"Warning: No company information found for {ticker_symbol}. It might be an invalid ticker or delisted.")
            return None
        # Further check if essential keys are missing, yfinance sometimes returns a dict with just "regularMarketPrice" for invalid tickers
        if info.get("regularMarketPrice") is not None and len(info) <= 5: # Heuristic for minimal info
             # Check if other common keys are missing, suggesting it's not full info
            if not any(k in info for k in ["shortName", "symbol", "sector", "industry"]):
                print(f"Warning: Limited or potentially invalid company information received for {ticker_symbol}.")
                # Depending on strictness, could return None here too
        return info
    except Exception as e:
        print(f"Error fetching company info for {ticker_symbol}: {e}")
        return None

def get_pe_ratio(company_info: dict) -> float | None:
    """
    Extracts the Price to Earnings (P/E) ratio from company information.
    Prioritizes 'trailingPE', then 'forwardPE'.

    Args:
        company_info: The company information dictionary from get_company_info.

    Returns:
        The P/E ratio as a float, or None if not available or company_info is None.
    """
    if not company_info:
        return None
    
    pe_ratio = company_info.get('trailingPE')
    if pe_ratio is None:
        pe_ratio = company_info.get('forwardPE')
    
    if isinstance(pe_ratio, (int, float)):
        return float(pe_ratio)
    return None

def get_earnings_data(ticker_symbol: str, company_info: dict) -> dict:
    """
    Retrieves latest EPS, EPS growth, and upcoming earnings date.

    Args:
        ticker_symbol: The stock ticker symbol.
        company_info: The company information dictionary.

    Returns:
        A dictionary with 'latest_eps', 'eps_growth_qoq', 'upcoming_earnings_date'.
        Values can be None if data is unavailable.
    """
    data = {
        'latest_eps': None,
        'eps_growth_ttm': None, # Trailing Twelve Months
        'eps_growth_qoq': None, # Quarter over Quarter
        'upcoming_earnings_date': None
    }

    if not company_info:
        return data

    # Latest EPS
    data['latest_eps'] = company_info.get('trailingEps') 
    if data['latest_eps'] is None:
        pass

    # Upcoming earnings date
    earnings_timestamp = company_info.get('earningsTimestamp')
    if earnings_timestamp:
        try:
            data['upcoming_earnings_date'] = datetime.fromtimestamp(earnings_timestamp).strftime('%Y-%m-%d')
        except Exception as e:
            print(f"Error converting earnings timestamp for {ticker_symbol}: {e}")
    
    data['eps_growth_ttm'] = company_info.get('earningsQuarterlyGrowth') 
    
    try:
        ticker = yf.Ticker(ticker_symbol)
        q_earnings = ticker.quarterly_earnings
        if q_earnings is not None and not q_earnings.empty and len(q_earnings) >= 2:
            q_earnings = q_earnings.sort_index(ascending=False) 
            eps_col = 'EPS' if 'EPS' in q_earnings.columns else 'actual' if 'actual' in q_earnings.columns else None
            if eps_col and eps_col in q_earnings.columns and q_earnings[eps_col].iloc[0] is not None and q_earnings[eps_col].iloc[1] is not None:
                if q_earnings[eps_col].iloc[1] != 0: 
                    eps_qoq_growth = (q_earnings[eps_col].iloc[0] - q_earnings[eps_col].iloc[1]) / abs(q_earnings[eps_col].iloc[1])
                    data['eps_growth_qoq'] = round(eps_qoq_growth, 4)
                else:
                    data['eps_growth_qoq'] = float('inf') if q_earnings[eps_col].iloc[0] > 0 else 0

    except Exception as e:
        print(f"Error fetching or calculating detailed EPS growth for {ticker_symbol}: {e}")

    return data

def get_revenue_growth(ticker_symbol: str, company_info: dict) -> dict:
    """
    Retrieves Year-over-Year (YoY) and Quarter-over-Quarter (QoQ) revenue growth.

    Args:
        ticker_symbol: The stock ticker symbol.
        company_info: The company information dictionary.

    Returns:
        A dictionary with 'revenue_growth_yoy', 'revenue_growth_qoq'.
        Values can be None if data is unavailable.
    """
    data = {
        'revenue_growth_yoy': None,
        'revenue_growth_qoq': None
    }

    if company_info and company_info.get('revenueGrowth') is not None:
        data['revenue_growth_yoy'] = company_info.get('revenueGrowth')

    try:
        ticker = yf.Ticker(ticker_symbol)
        
        q_financials = ticker.quarterly_financials
        if q_financials is not None and not q_financials.empty:
            q_financials = q_financials.T 
            q_financials.sort_index(ascending=False, inplace=True) 
            if 'Total Revenue' in q_financials.columns and len(q_financials) >= 2:
                current_revenue = q_financials['Total Revenue'].iloc[0]
                previous_revenue = q_financials['Total Revenue'].iloc[1]
                if previous_revenue is not None and current_revenue is not None and previous_revenue != 0:
                    qoq_growth = (current_revenue - previous_revenue) / abs(previous_revenue)
                    data['revenue_growth_qoq'] = round(qoq_growth, 4)
                elif previous_revenue == 0 and current_revenue > 0 :
                     data['revenue_growth_qoq'] = float('inf') 

        if data['revenue_growth_yoy'] is None: 
            financials = ticker.financials
            if financials is not None and not financials.empty:
                financials = financials.T 
                financials.sort_index(ascending=False, inplace=True)
                if 'Total Revenue' in financials.columns and len(financials) >= 2:
                    current_year_revenue = financials['Total Revenue'].iloc[0]
                    previous_year_revenue = financials['Total Revenue'].iloc[1]
                    if previous_year_revenue is not None and current_year_revenue is not None and previous_year_revenue != 0:
                        yoy_growth = (current_year_revenue - previous_year_revenue) / abs(previous_year_revenue)
                        data['revenue_growth_yoy'] = round(yoy_growth, 4)
                    elif previous_year_revenue == 0 and current_year_revenue > 0 :
                        data['revenue_growth_yoy'] = float('inf')
    except Exception as e:
        print(f"Error fetching or calculating revenue growth for {ticker_symbol}: {e}")

    return data

def get_profit_margins(company_info: dict) -> dict:
    """
    Extracts key profit margins from company information.

    Args:
        company_info: The company information dictionary.

    Returns:
        A dictionary like: {'net_profit_margin': 0.25, 'gross_margin': 0.60, 'operating_margin': 0.30}.
        Values can be None.
    """
    margins = {
        'net_profit_margin': None,
        'gross_margin': None,
        'operating_margin': None
    }
    if not company_info:
        return margins

    margins['net_profit_margin'] = company_info.get('profitMargins')
    margins['gross_margin'] = company_info.get('grossMargins')
    margins['operating_margin'] = company_info.get('operatingMargins')
    
    return margins

def get_debt_to_equity(company_info: dict, ticker_symbol: str) -> float | None:
    """
    Calculates the debt-to-equity ratio.
    Tries to get it from company_info first, then calculates from balance sheet.

    Args:
        company_info: The company information dictionary.
        ticker_symbol: The stock ticker symbol.

    Returns:
        The debt-to-equity ratio as a float, or None.
    """
    if not company_info:
        return None

    # Try to get directly from info
    d2e_ratio = company_info.get('debtToEquity')
    if d2e_ratio is not None:
        try:
            return float(d2e_ratio)
        except (ValueError, TypeError):
            print(f"Warning: Could not convert debtToEquity '{d2e_ratio}' to float for {ticker_symbol}.")
            # Proceed to calculation if conversion fails
    
    total_debt = company_info.get('totalDebt') # Sometimes available in info

    try:
        ticker = yf.Ticker(ticker_symbol)
        # Fetch latest balance sheet (annual first, then quarterly as fallback)
        bs = ticker.balance_sheet
        if bs.empty:
            bs = ticker.quarterly_balance_sheet
        
        if not bs.empty:
            # Balance sheet columns are timestamps, so take the latest (first column)
            latest_bs = bs.iloc[:, 0] 
            
            if total_debt is None and 'Total Debt' in latest_bs.index:
                total_debt = latest_bs['Total Debt']
            
            total_stockholder_equity = None
            if 'Total Stockholder Equity' in latest_bs.index:
                total_stockholder_equity = latest_bs['Total Stockholder Equity']
            elif 'Stockholders Equity' in latest_bs.index: # Alternative name
                 total_stockholder_equity = latest_bs['Stockholders Equity']


            if total_debt is not None and total_stockholder_equity is not None:
                if total_stockholder_equity != 0:
                    return round(float(total_debt) / float(total_stockholder_equity), 4)
                else:
                    # If equity is 0, D/E is infinite if debt > 0, or 0 if debt is also 0.
                    # Or could be undefined (None). Returning None for simplicity.
                    print(f"Warning: Total stockholder equity is zero for {ticker_symbol}, D/E cannot be calculated.")
                    return None 
            else:
                missing_items = []
                if total_debt is None: missing_items.append("Total Debt")
                if total_stockholder_equity is None: missing_items.append("Total Stockholder Equity")
                print(f"Warning: Could not find {', '.join(missing_items)} in balance sheet for {ticker_symbol} to calculate D/E.")
        else:
            print(f"Warning: Balance sheet data not available for {ticker_symbol} to calculate D/E.")

    except Exception as e:
        print(f"Error calculating debt to equity for {ticker_symbol}: {e}")
    
    return None


def get_return_on_equity(company_info: dict) -> float | None:
    """
    Extracts the Return on Equity (ROE) from company information.

    Args:
        company_info: The company information dictionary.

    Returns:
        The ROE as a float, or None.
    """
    if not company_info:
        return None
    
    roe = company_info.get('returnOnEquity')
    if roe is not None:
        try:
            return float(roe)
        except (ValueError, TypeError):
            print(f"Warning: Could not convert returnOnEquity '{roe}' to float.")
            return None
    return None


# Example Usage (for testing, would be removed or in a test file)
if __name__ == '__main__':
    import os
    # Ensure the dummy directory structure exists if run directly
    if not os.path.exists("stock_analyzer_agent/agent"):
        os.makedirs("stock_analyzer_agent/agent", exist_ok=True)

    sample_tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "BRK-A", "JPM", "V", "JNJ", "WMT", "PG", "UNH", "HD", "BAC", "DIS", "PFE", "NFLX", "ADBE", "CRM"]
    # sample_tickers = ["AAPL", "MSFT", "TM", "NONEXISTENTTICKER"] # Test with a non-US stock and a non-existent one

    for sample_ticker in sample_tickers:
        print(f"\n--- Fundamental Analysis for {sample_ticker} ---")
        
        info = get_company_info(sample_ticker)
        if info:
            print(f"Sector: {info.get('sector', 'N/A')}, Industry: {info.get('industry', 'N/A')}")

            pe = get_pe_ratio(info)
            print(f"P/E Ratio: {pe}")

            earnings = get_earnings_data(sample_ticker, info)
            print("Earnings Data:")
            for key, value in earnings.items():
                print(f"  {key}: {value}")

            revenue = get_revenue_growth(sample_ticker, info)
            print("Revenue Growth:")
            for key, value in revenue.items():
                print(f"  {key}: {value}")
            
            margins = get_profit_margins(info)
            print("Profit Margins:")
            for key, value in margins.items():
                print(f"  {key}: {value}")

            d2e = get_debt_to_equity(info, sample_ticker)
            print(f"Debt to Equity Ratio: {d2e}")

            roe = get_return_on_equity(info)
            print(f"Return on Equity (ROE): {roe}")
            
        else:
            print(f"Could not retrieve company info for {sample_ticker}.")
        print("--------------------------------------")

    # Test with a known problematic or specific case if needed
    # print(f"\n--- Fundamental Analysis for Specific Case ---")
    # specific_ticker = "BHGE" # Example of a company that might have changed ticker or merged
    # info_specific = get_company_info(specific_ticker)
    # if info_specific:
    #     d2e_specific = get_debt_to_equity(info_specific, specific_ticker)
    #     print(f"Debt to Equity Ratio ({specific_ticker}): {d2e_specific}")
    # else:
    #     print(f"Could not retrieve company info for {specific_ticker}.")
