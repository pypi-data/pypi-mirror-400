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

def strategy_rsi_scalp(df):
    """
    RSI Scalping Strategy (15m):
    - Trend Filter: EMA 50
    - Entry: RSI Reversion (Oversold in Uptrend, Overbought in Downtrend)
    - Risk: 1% per trade
    - RR: 1:1.5
    """
    signals = []
    closes = df['close'].tolist()
    highs = df['high'].tolist()
    lows = df['low'].tolist()
    
    # Indicators
    ema50 = pp.ema(closes, 50)
    rsi = pp.rsi(closes, 14)
    atr = pp.atr(highs, lows, closes, 14)
    
    print(f"DEBUG: Data Length: {len(df)}")
    print(f"DEBUG: EMA50[-1]: {ema50[-1] if len(ema50)>0 else 'None'}")
    print(f"DEBUG: RSI[-1]: {rsi[-1] if len(rsi)>0 else 'None'}")

    for i in range(50, len(df)):
        # Long Setup: Oversold (Mean Reversion)
        if rsi[i] < 30:
            sl_dist = 1.5 * atr[i] 
            entry_price = closes[i]
            sl = entry_price - sl_dist
            tp = entry_price + (sl_dist * 1.5) 
            signals.append({
                'index': i, 'type': 'BUY', 
                'sl': sl, 'tp': tp, 
                'risk': 0.01, 
                'comment': f'RSI Buy ({rsi[i]:.1f})'
            })

        # Short Setup: Overbought (Mean Reversion)
        elif rsi[i] > 70:
            sl_dist = 1.5 * atr[i]
            entry_price = closes[i]
            sl = entry_price + sl_dist
            tp = entry_price - (sl_dist * 1.5) 
            signals.append({
                'index': i, 'type': 'SELL', 
                'sl': sl, 'tp': tp, 
                'risk': 0.01, 
                'comment': f'RSI Sell ({rsi[i]:.1f})'
            })
                    
    return signals

def run_day_trading_test():
    print("Initializing Data Engine...")
    data_engine = DataEngine(api_key=API_KEY, secret_key=SECRET_KEY)
    
    # 1 Week Test Period (Reduced from 1 Month for speed)
    start_date = "2023-01-01-00-00-00"
    end_date = "2023-01-08-00-00-00"
    
    scenarios = [
        {"name": "BTC_USD_15m_Scalp_1Week", "symbol": "BTC/USD", "strategy": strategy_rsi_scalp},
    ]
    
    print(f"Running Day Trading Test ({start_date} to {end_date})...\n")
    
    for sc in scenarios:
        print(f"--- Running {sc['name']} ---")
        # Professional Settings:
        # - Max Pyramiding: 5 (Allow more concurrent trades for scalping)
        # - Commission: 0.1% (0.001)
        tm = TradeManager(max_pyramiding=5, commission_rate=0.001)
        bt = Backtester(data_engine, tm)
        
        try:
            # 15m Timeframe
            bt.run(sc['symbol'], "15m", start_date, end_date, sc['strategy'], commission_rate=0.001)
            
            # Generate Report
            reporter = Reporter(tm)
            filename = f"day_trade_report_{sc['name']}.html"
            reporter.generate_html_report(filename, start_date, end_date)
            
            pnl = tm.get_total_pnl()
            trades = len(tm.get_closed_trades())
            print(f"Result: PnL={pnl:.2f}, Trades={trades}, Report={filename}\n")
            
        except Exception as e:
            print(f"Failed to run {sc['name']}: {e}\n")

if __name__ == "__main__":
    run_day_trading_test()
