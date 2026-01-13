import pandas as pd
from backtester import Backtester
from data_engine import DataEngine
from trade_manager import TradeManager
from reporter import Reporter
import os

# --- Helper: RSI Calculation (Pandas) ---
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    # Wilder's Smoothing (alpha = 1/n)
    avg_gain = gain.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# --- Strategy: RSI Scalp ---
def rsi_scalp_strategy(df):
    """
    RSI Scalping Strategy
    - Buy when RSI < 30
    - Sell when RSI > 70
    - TP: 10 pips (0.0010)
    - SL: 5 pips (0.0005)
    """
    print("Calculating Indicators...")
    df['rsi'] = calculate_rsi(df['close'], 14)
    
    signals = []
    
    # Iterate to generate signals
    # Note: We start from index 14 to have RSI values
    for i in range(14, len(df)):
        rsi = df.iloc[i]['rsi']
        # prev_rsi = df.iloc[i-1]['rsi'] # Optional: Check for crossover
        
        # Simple Threshold Logic
        # To avoid spamming signals, we could check if we just crossed
        # But the Backtester handles one trade per direction or we can rely on TradeManager to manage limits.
        # Here we'll just emit signals and let Backtester decide (it usually takes the first one if we don't handle state here).
        # Better: Only signal if we crossed the threshold in this candle
        
        prev_rsi = df.iloc[i-1]['rsi']
        
        # Cross Under 30 -> Buy
        if rsi < 30 and prev_rsi >= 30:
            signals.append({
                'index': i,
                'time': df.iloc[i]['time'],
                'type': 'BUY',
                'sl': df.iloc[i]['close'] - 0.0005, # 5 pips SL
                'tp': df.iloc[i]['close'] + 0.0010, # 10 pips TP
                'risk': 0.01, # 1% Risk
                'comment': f'RSI Buy ({rsi:.2f})'
            })
            
        # Cross Over 70 -> Sell
        elif rsi > 70 and prev_rsi <= 70:
            signals.append({
                'index': i,
                'time': df.iloc[i]['time'],
                'type': 'SELL',
                'sl': df.iloc[i]['close'] + 0.0005, # 5 pips SL
                'tp': df.iloc[i]['close'] - 0.0010, # 10 pips TP
                'risk': 0.01, # 1% Risk
                'comment': f'RSI Sell ({rsi:.2f})'
            })
            
    print(f"Generated {len(signals)} signals.")
    return signals

def run_scalp_test():
    # 1. Setup Components
    data_engine = DataEngine() # Assumes env vars or no auth needed for local/cached data
    trade_manager = TradeManager()
    backtester = Backtester(data_engine, trade_manager)
    
    # 2. Configure Test
    symbol = "EUR/USD"
    timeframe = "1m"
    start_date = "2023-06-01"
    end_date = "2023-06-04"
    
    # 3. Run Backtest
    backtester.run(
        symbol=symbol,
        timeframe=timeframe,
        start_str=start_date,
        end_str=end_date,
        strategy_func=rsi_scalp_strategy,
        initial_capital=10000,
        commission_rate=0.0 # Zero commission for test
    )
    
    # 4. Generate Report
    reporter = Reporter(trade_manager)
    report_file = "scalp_report_EUR_USD_1M.html"
    reporter.generate_html_report(report_file, start_date, end_date)
    
    # Verification
    if os.path.exists(report_file):
        print(f"SUCCESS: Report generated at {report_file}")
    else:
        print("FAILURE: Report not found.")

if __name__ == "__main__":
    run_scalp_test()
