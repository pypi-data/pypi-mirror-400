import os
from dotenv import load_dotenv
from trade_manager import TradeManager
from backtester import Backtester
from data_engine import DataEngine
from reporter import Reporter
import pythonpine as pp
import pandas as pd

# Load environment variables
load_dotenv("../finda/.env") # Load from finda directory
API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")

# --- Strategies (Reused) ---

def strategy_sma_crossover(df):
    """Trend Following: Buy Golden Cross, Sell Death Cross"""
    signals = []
    closes = df['close'].tolist()
    sma_fast = pp.sma(closes, 10)
    sma_slow = pp.sma(closes, 30)
    
    for i in range(30, len(df)):
        if sma_fast[i] > sma_slow[i] and sma_fast[i-1] <= sma_slow[i-1]:
            signals.append({'index': i, 'type': 'BUY', 'sl': df['close'].iloc[i]*0.95, 'tp': df['close'].iloc[i]*1.10, 'comment': 'Golden Cross'})
        elif sma_fast[i] < sma_slow[i] and sma_fast[i-1] >= sma_slow[i-1]:
            signals.append({'index': i, 'type': 'SELL', 'sl': df['close'].iloc[i]*1.05, 'tp': df['close'].iloc[i]*0.90, 'comment': 'Death Cross'})
    return signals

def strategy_rsi_reversion(df):
    """Mean Reversion: Buy Oversold (<30), Sell Overbought (>70)"""
    signals = []
    closes = df['close'].tolist()
    rsi = pp.rsi(closes, 14)
    
    for i in range(15, len(df)):
        if rsi[i] < 30 and rsi[i-1] >= 30:
            signals.append({'index': i, 'type': 'BUY', 'sl': df['close'].iloc[i]*0.98, 'tp': df['close'].iloc[i]*1.05, 'comment': 'RSI Oversold'})
        elif rsi[i] > 70 and rsi[i-1] <= 70:
            signals.append({'index': i, 'type': 'SELL', 'sl': df['close'].iloc[i]*1.02, 'tp': df['close'].iloc[i]*0.95, 'comment': 'RSI Overbought'})
    return signals

def strategy_bollinger_breakout(df):
    """Volatility Breakout: Buy if close > Upper Band"""
    signals = []
    closes = df['close'].tolist()
    upper, lower, mid = pp.bollinger_bands(closes, 20, 2)
    
    for i in range(20, len(df)):
        if closes[i] > upper[i] and closes[i-1] <= upper[i-1]:
             signals.append({'index': i, 'type': 'BUY', 'sl': mid[i], 'tp': closes[i]*1.05, 'comment': 'BB Breakout Buy'})
        elif closes[i] < lower[i] and closes[i-1] >= lower[i-1]:
             signals.append({'index': i, 'type': 'SELL', 'sl': mid[i], 'tp': closes[i]*0.95, 'comment': 'BB Breakout Sell'})
    return signals

def run_real_world_tests():
    print("Initializing Data Engine with Real Data...")
    data_engine = DataEngine(api_key=API_KEY, secret_key=SECRET_KEY)
    
    # Define 6 Scenarios
    # Note: Ensure symbols are supported by your finda providers (Alpaca, Binance, Dukascopy)
    # Timeframe: 1h. Duration: ~1 week to ensure we get data but not too huge for tick download.
    
    start_date = "2023-11-01-00-00-00"
    end_date = "2023-11-07-00-00-00"
    
    scenarios = [
        # Crypto (Binance/Alpaca)
        {"name": "BTC_USD_Trend", "symbol": "BTC/USD", "strategy": strategy_sma_crossover},
        {"name": "ETH_USD_RSI", "symbol": "ETH/USD", "strategy": strategy_rsi_reversion},
        
        # Forex (Dukascopy/Alpaca)
        {"name": "EUR_USD_Bollinger", "symbol": "EUR/USD", "strategy": strategy_bollinger_breakout},
        {"name": "GBP_USD_Trend", "symbol": "GBP/USD", "strategy": strategy_sma_crossover},
        
        # Stocks (Alpaca)
        {"name": "AAPL_RSI", "symbol": "AAPL", "strategy": strategy_rsi_reversion},
        {"name": "TSLA_Bollinger", "symbol": "TSLA", "strategy": strategy_bollinger_breakout},
    ]
    
    results = []
    
    print(f"Running 6 Real-World Tests ({start_date} to {end_date})...\n")
    
    for sc in scenarios:
        print(f"--- Running {sc['name']} ---")
        tm = TradeManager(max_pyramiding=1)
        bt = Backtester(data_engine, tm)
        
        try:
            bt.run(sc['symbol'], "1h", start_date, end_date, sc['strategy'])
            
            # Generate Report
            reporter = Reporter(tm)
            filename = f"real_report_{sc['name']}.html"
            reporter.generate_html_report(filename)
            
            pnl = tm.get_total_pnl()
            trades = len(tm.get_closed_trades())
            win_rate = 0
            if trades > 0:
                wins = len([t for t in tm.get_closed_trades() if t.pnl > 0])
                win_rate = (wins / trades) * 100
                
            results.append({
                "Scenario": sc['name'],
                "PnL": pnl,
                "Trades": trades,
                "Win Rate": win_rate,
                "Report": filename
            })
            print(f"Result: PnL={pnl:.2f}, Trades={trades}, WinRate={win_rate:.1f}%, Report={filename}\n")
            
        except Exception as e:
            print(f"Failed to run {sc['name']}: {e}\n")

    # Generate Summary Report
    with open("real_world_performance_report.md", "w") as f:
        f.write("# Real-World Strategy Performance Report\n\n")
        f.write(f"**Period:** {start_date} to {end_date}\n\n")
        f.write("| Scenario | PnL | Trades | Win Rate | Report |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- |\n")
        for r in results:
            f.write(f"| {r['Scenario']} | {r['PnL']:.2f} | {r['Trades']} | {r['Win Rate']:.1f}% | [View]({r['Report']}) |\n")
            
    print("Summary report generated: real_world_performance_report.md")

if __name__ == "__main__":
    run_real_world_tests()
