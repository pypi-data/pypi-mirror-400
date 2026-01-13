import os
from dotenv import load_dotenv
from trade_manager import TradeManager
from backtester import Backtester
from data_engine import DataEngine
from reporter import Reporter
import pythonpine as pp
import pandas as pd

# Load environment variables
load_dotenv("../finda/.env")
API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")

def strategy_macd_swing(df):
    """
    MACD Swing Strategy:
    - Trend Filter: EMA 200
    - Entry: MACD Cross
    - Exit: SL (2*ATR) or TP (1:2 RR)
    """
    signals = []
    closes = df['close'].tolist()
    highs = df['high'].tolist()
    lows = df['low'].tolist()
    
    # Indicators
    ema200 = pp.ema(closes, 200)
    macd_line, signal_line, hist = pp.macd(closes, 12, 26, 9)
    atr = pp.atr(highs, lows, closes, 14)
    
    for i in range(200, len(df)):
        # Buy Setup: Uptrend + MACD Cross Up
        if closes[i] > ema200[i]:
            if macd_line[i] > signal_line[i] and macd_line[i-1] <= signal_line[i-1]:
                # Removed strict 'macd < 0' filter to get more trades
                sl_dist = 2 * atr[i]
                entry_price = closes[i]
                sl = entry_price - sl_dist
                tp = entry_price + (sl_dist * 2)
                signals.append({
                    'index': i, 'type': 'BUY', 
                    'sl': sl, 'tp': tp, 
                    'comment': 'MACD Bullish Swing'
                })

        # Sell Setup: Downtrend + MACD Cross Down
        elif closes[i] < ema200[i]:
            if macd_line[i] < signal_line[i] and macd_line[i-1] >= signal_line[i-1]:
                # Removed strict 'macd > 0' filter to get more trades
                sl_dist = 2 * atr[i]
                entry_price = closes[i]
                sl = entry_price + sl_dist
                tp = entry_price - (sl_dist * 2)
                signals.append({
                    'index': i, 'type': 'SELL', 
                    'sl': sl, 'tp': tp, 
                    'comment': 'MACD Bearish Swing'
                })
                    
    return signals

def run_swing_tests():
    print("Initializing Data Engine...")
    data_engine = DataEngine(api_key=API_KEY, secret_key=SECRET_KEY)
    
    # 1 Month Test Period
    start_date = "2023-10-01-00-00-00"
    end_date = "2023-11-01-00-00-00"
    
    scenarios = [
        {"name": "EUR_USD_Swing_1M", "symbol": "EUR/USD", "strategy": strategy_macd_swing},
        {"name": "BTC_USD_Swing_1M", "symbol": "BTC/USD", "strategy": strategy_macd_swing},
    ]
    
    print(f"Running 1-Month Swing Tests ({start_date} to {end_date})...\n")
    
    for sc in scenarios:
        print(f"--- Running {sc['name']} ---")
        # Increased Pyramiding to 3 to allow overlapping trades
        tm = TradeManager(max_pyramiding=3)
        bt = Backtester(data_engine, tm)
        
        try:
            bt.run(sc['symbol'], "1h", start_date, end_date, sc['strategy'])
            
            # Generate Professional Report
            reporter = Reporter(tm)
            filename = f"swing_report_{sc['name']}.html"
            reporter.generate_html_report(filename, start_date, end_date)
            
            pnl = tm.get_total_pnl()
            trades = len(tm.get_closed_trades())
            print(f"Result: PnL={pnl:.2f}, Trades={trades}, Report={filename}\n")
            
        except Exception as e:
            print(f"Failed to run {sc['name']}: {e}\n")

if __name__ == "__main__":
    run_swing_tests()
