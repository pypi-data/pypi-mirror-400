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

def strategy_macd_swing_risk(df):
    """
    MACD Swing Strategy with Dynamic Risk Management.
    - Risk 1% of equity per trade.
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
        # Buy Setup
        if closes[i] > ema200[i]:
            if macd_line[i] > signal_line[i] and macd_line[i-1] <= signal_line[i-1]:
                sl_dist = 2 * atr[i]
                entry_price = closes[i]
                sl = entry_price - sl_dist
                tp = entry_price + (sl_dist * 2)
                signals.append({
                    'index': i, 'type': 'BUY', 
                    'sl': sl, 'tp': tp, 
                    'risk': 0.01, # Risk 1% of capital
                    'comment': 'MACD Bullish'
                })

        # Sell Setup
        elif closes[i] < ema200[i]:
            if macd_line[i] < signal_line[i] and macd_line[i-1] >= signal_line[i-1]:
                sl_dist = 2 * atr[i]
                entry_price = closes[i]
                sl = entry_price + sl_dist
                tp = entry_price - (sl_dist * 2)
                signals.append({
                    'index': i, 'type': 'SELL', 
                    'sl': sl, 'tp': tp, 
                    'risk': 0.01, # Risk 1% of capital
                    'comment': 'MACD Bearish'
                })
                    
    return signals

def run_stress_test():
    print("Initializing Data Engine...")
    data_engine = DataEngine(api_key=API_KEY, secret_key=SECRET_KEY)
    
    # 1 Month Test Period for Verification
    start_date = "2023-01-01-00-00-00"
    end_date = "2023-02-01-00-00-00"
    
    scenarios = [
        {"name": "BTC_USD_1Month_Stress", "symbol": "BTC/USD", "strategy": strategy_macd_swing_risk},
    ]
    
    print(f"Running 1-Year Stress Test ({start_date} to {end_date})...\n")
    
    for sc in scenarios:
        print(f"--- Running {sc['name']} ---")
        # Professional Settings:
        # - Max Pyramiding: 3
        # - Commission: 0.1% (0.001)
        tm = TradeManager(max_pyramiding=3, commission_rate=0.001)
        bt = Backtester(data_engine, tm)
        
        try:
            # Pass commission_rate to run()
            bt.run(sc['symbol'], "1h", start_date, end_date, sc['strategy'], commission_rate=0.001)
            
            # Generate Annual Report
            reporter = Reporter(tm)
            filename = f"stress_report_{sc['name']}.html"
            reporter.generate_html_report(filename, start_date, end_date)
            
            pnl = tm.get_total_pnl()
            trades = len(tm.get_closed_trades())
            print(f"Result: PnL={pnl:.2f}, Trades={trades}, Report={filename}\n")
            
        except Exception as e:
            print(f"Failed to run {sc['name']}: {e}\n")

if __name__ == "__main__":
    run_stress_test()
