from flask import Flask, escape, render_template, request, redirect, url_for
from stock_analyzer_webapp.stock_analyzer_agent.agent import data_collection
from stock_analyzer_webapp.stock_analyzer_agent.agent import technical_analysis
from stock_analyzer_webapp.stock_analyzer_agent.agent import reporting
from stock_analyzer_webapp.stock_analyzer_agent.agent import fundamental_analysis # Added for fundamental data
from datetime import datetime
import pandas as pd

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        ticker = request.form.get('ticker')
        user_type = request.form.get('user_type')
        if ticker and user_type:
            # Sanitize ticker here before passing to url_for for safety if needed,
            # though analyze_stock also escapes.
            return redirect(url_for('analyze_stock', user_type=user_type, ticker_symbol=ticker))
    return render_template('index.html')

@app.route('/analyze/<user_type>/<ticker_symbol>', methods=['GET'])
def analyze_stock(user_type, ticker_symbol):
    analysis_timestamp = datetime.now()
    
    # Sanitize inputs (basic example)
    # user_type = str(escape(user_type)) # Already a path parameter, Flask handles basic validation
    # ticker_symbol = str(escape(ticker_symbol)) # Already a path parameter

    current_data = data_collection.get_current_stock_data(ticker_symbol)
    # Use a slightly longer period for more robust indicator calculation
    historical_data = data_collection.get_historical_stock_data(ticker_symbol, period="6mo", interval="1d")

    # Error Handling for data fetching
    if not current_data or \
       (current_data.get('current_price') is None and current_data.get('status_message')) or \
       (isinstance(historical_data, pd.DataFrame) and historical_data.empty):
        
        error_message = f"Could not retrieve sufficient data for ticker: {ticker_symbol}."
        if current_data and current_data.get('status_message'):
            error_message += f" Status: {current_data.get('status_message')}"
        elif isinstance(historical_data, pd.DataFrame) and historical_data.empty:
            error_message += " Reason: Historical data is empty or could not be fetched."
        else:
            error_message += " An unknown data fetching error occurred."
        return render_template('error.html', error_message=error_message, ticker_symbol=ticker_symbol), 404

    technical_indicators = {}
    
    sma_20_series = technical_analysis.calculate_moving_average(historical_data, window=20)
    technical_indicators['sma_20'] = sma_20_series.iloc[-1] if not sma_20_series.empty and pd.notna(sma_20_series.iloc[-1]) else None
    
    sma_50_series = technical_analysis.calculate_moving_average(historical_data, window=50)
    technical_indicators['sma_50'] = sma_50_series.iloc[-1] if not sma_50_series.empty and pd.notna(sma_50_series.iloc[-1]) else None
    
    sma_200_series = technical_analysis.calculate_moving_average(historical_data, window=200)
    technical_indicators['sma_200'] = sma_200_series.iloc[-1] if not sma_200_series.empty and pd.notna(sma_200_series.iloc[-1]) else None
    
    rsi_series = technical_analysis.calculate_rsi(historical_data)
    technical_indicators['rsi'] = rsi_series.iloc[-1] if not rsi_series.empty and pd.notna(rsi_series.iloc[-1]) else None
    
    macd_line, signal_line, macd_hist = technical_analysis.calculate_macd(historical_data)
    technical_indicators['macd_line'] = macd_line.iloc[-1] if not macd_line.empty and pd.notna(macd_line.iloc[-1]) else None
    technical_indicators['macd_signal'] = signal_line.iloc[-1] if not signal_line.empty and pd.notna(signal_line.iloc[-1]) else None
    technical_indicators['macd_hist'] = macd_hist.iloc[-1] if not macd_hist.empty and pd.notna(macd_hist.iloc[-1]) else None
    
    bb_upper, bb_middle, bb_lower = technical_analysis.calculate_bollinger_bands(historical_data)
    technical_indicators['bb_upper'] = bb_upper.iloc[-1] if not bb_upper.empty and pd.notna(bb_upper.iloc[-1]) else None
    technical_indicators['bb_middle'] = bb_middle.iloc[-1] if not bb_middle.empty and pd.notna(bb_middle.iloc[-1]) else None
    technical_indicators['bb_lower'] = bb_lower.iloc[-1] if not bb_lower.empty and pd.notna(bb_lower.iloc[-1]) else None
    
    stoch_k, stoch_d = technical_analysis.calculate_stochastic_oscillator(historical_data)
    technical_indicators['stoch_k'] = stoch_k.iloc[-1] if not stoch_k.empty and pd.notna(stoch_k.iloc[-1]) else None
    technical_indicators['stoch_d'] = stoch_d.iloc[-1] if not stoch_d.empty and pd.notna(stoch_d.iloc[-1]) else None
    
    technical_indicators['volatility_info'] = technical_analysis.check_volatility(historical_data, current_data)

    chart_features = {}
    chart_features.update(technical_analysis.identify_support_resistance(historical_data))
    chart_features['price_gap_info'] = technical_analysis.detect_price_gap(current_data, historical_data)
    chart_features['unusual_volume_info'] = technical_analysis.detect_unusual_volume(current_data, historical_data)

    fundamental_data_for_report = None
    if user_type.lower() in ['portfolio_manager', 'beginner_investor']:
        company_info = fundamental_analysis.get_company_info(ticker_symbol)
        if company_info:
            earnings_data = fundamental_analysis.get_earnings_data(ticker_symbol, company_info) # Fetch once
            fundamental_data_for_report = {
                'company_name': company_info.get('shortName', ticker_symbol),
                'sector': company_info.get('sector'),
                'industry': company_info.get('industry'),
                'pe_ratio': fundamental_analysis.get_pe_ratio(company_info),
                'latest_eps': earnings_data.get('latest_eps'),
                'eps_growth_ttm': earnings_data.get('eps_growth_ttm'), # Using TTM from get_earnings_data
                'revenue_growth_yoy': fundamental_analysis.get_revenue_growth(ticker_symbol, company_info).get('revenue_growth_yoy'),
                'net_profit_margin': fundamental_analysis.get_profit_margins(company_info).get('net_profit_margin'),
                'debt_to_equity': fundamental_analysis.get_debt_to_equity(company_info, ticker_symbol),
                'return_on_equity': fundamental_analysis.get_return_on_equity(company_info),
                # Add other relevant fields as per reporting module's needs
            }
        else: 
            fundamental_data_for_report = {
                'company_name': ticker_symbol,
                'status_message': f"Could not retrieve detailed fundamental company info for {ticker_symbol}."
            }


    report = reporting.generate_stock_report(
        ticker=ticker_symbol,
        user_type=user_type,
        current_data=current_data,
        technical_indicators=technical_indicators,
        fundamental_data=fundamental_data_for_report, 
        chart_features=chart_features,
        analysis_timestamp=analysis_timestamp
    )
    
    return render_template('report.html', ticker_symbol=ticker_symbol, user_type=user_type, report_content=report)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
