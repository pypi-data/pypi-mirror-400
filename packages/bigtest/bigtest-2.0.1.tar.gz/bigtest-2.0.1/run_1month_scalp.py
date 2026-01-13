import pandas as pd
from backtester import Backtester
from data_engine import DataEngine
from trade_manager import TradeManager
from reporter import Reporter
import os

# --- Helper: RSI Calculation ---
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

# --- Generic RSI Scalp Strategy ---
def rsi_scalp_strategy(df, symbol):
    print(f"Calculating Indicators for {symbol}...")
    df['rsi'] = calculate_rsi(df['close'], 14)
    signals = []
    
    # Dynamic Parameters based on asset class
    if "USD" in symbol and "/" in symbol and "BTC" not in symbol and "ETH" not in symbol: # Forex (EUR/USD)
        sl_pips = 0.0005 # 5 pips
        tp_pips = 0.0010 # 10 pips
        is_forex = True
    elif "BTC" in symbol or "ETH" in symbol: # Crypto
        sl_amt = 100 # $100
        tp_amt = 200 # $200
        is_crypto = True
        is_forex = False
    else: # Stocks (TSLA, AAPL)
        sl_pct = 0.005 # 0.5%
        tp_pct = 0.01 # 1.0%
        is_stock = True
        is_forex = False
        is_crypto = False

    for i in range(14, len(df)):
        rsi = df.iloc[i]['rsi']
        prev_rsi = df.iloc[i-1]['rsi']
        close = df.iloc[i]['close']
        time = df.iloc[i]['time']
        
        # Cross Under 30 -> Buy
        if rsi < 30 and prev_rsi >= 30:
            if is_forex:
                sl = close - sl_pips
                tp = close + tp_pips
            elif is_crypto:
                sl = close - sl_amt
                tp = close + tp_amt
            else:
                sl = close * (1 - sl_pct)
                tp = close * (1 + tp_pct)
                
            signals.append({
                'index': i,
                'time': time,
                'type': 'BUY',
                'sl': sl,
                'tp': tp,
                'risk': 0.01,
                'comment': f'RSI Buy ({rsi:.2f})'
            })
            
        # Cross Over 70 -> Sell
        elif rsi > 70 and prev_rsi <= 70:
            if is_forex:
                sl = close + sl_pips
                tp = close - tp_pips
            elif is_crypto:
                sl = close + sl_amt
                tp = close - tp_amt
            else:
                sl = close * (1 + sl_pct)
                tp = close * (1 - tp_pct)
                
            signals.append({
                'index': i,
                'time': time,
                'type': 'SELL',
                'sl': sl,
                'tp': tp,
                'risk': 0.01,
                'comment': f'RSI Sell ({rsi:.2f})'
            })
            
    print(f"Generated {len(signals)} signals for {symbol}.")
    return signals

def run_test(symbol, start_date, end_date):
    print(f"\n=== Running Backtest for {symbol} ===")
    print(f"Period: {start_date} to {end_date}")
    
    data_engine = DataEngine()
    trade_manager = TradeManager()
    backtester = Backtester(data_engine, trade_manager)
    
    # Wrap strategy to pass symbol
    def strategy_wrapper(df):
        return rsi_scalp_strategy(df, symbol)
    
    try:
        backtester.run(
            symbol=symbol,
            timeframe="1m",
            start_str=start_date,
            end_str=end_date,
            strategy_func=strategy_wrapper,
            initial_capital=10000,
            commission_rate=0.0
        )
        
        reporter = Reporter(trade_manager)
        safe_symbol = symbol.replace("/", "_")
        report_file = f"report_{safe_symbol}_1M.html"
        reporter.generate_html_report(report_file, start_date, end_date)
        
        if os.path.exists(report_file):
            print(f"SUCCESS: Report generated at {report_file}")
        else:
            print("FAILURE: Report not found.")
            
    except Exception as e:
        print(f"ERROR running test for {symbol}: {e}")

if __name__ == "__main__":
    tests = [
        ("EUR/USD", "2023-06-01", "2023-07-01"),
        ("BTC/USD", "2023-06-01", "2023-07-01"),
        ("TSLA", "2023-06-01", "2023-07-01")
    ]
    
    for symbol, start, end in tests:
        run_test(symbol, start, end)
