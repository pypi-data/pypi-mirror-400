import unittest
import pandas as pd
import numpy as np
import pythonpine as pp
from datetime import datetime, timedelta
from trade_manager import TradeManager
from backtester import Backtester
from data_engine import DataEngine
from reporter import Reporter

# --- Synthetic Data Generator ---
class SyntheticDataEngine(DataEngine):
    def __init__(self):
        pass
        
    def generate_data(self, pattern, length=500, start_price=100):
        dates = pd.date_range(start="2023-01-01", periods=length, freq='1h')
        prices = [start_price]
        
        for i in range(1, length):
            prev = prices[-1]
            change = 0
            
            if pattern == "UP_TREND":
                change = np.random.normal(0.5, 1.0) # Bias up
            elif pattern == "DOWN_TREND":
                change = np.random.normal(-0.5, 1.0) # Bias down
            elif pattern == "RANGING":
                # Mean reversion to start_price
                diff = start_price - prev
                change = np.random.normal(diff * 0.1, 1.0)
            elif pattern == "VOLATILE":
                change = np.random.normal(0, 3.0) # High variance
                
            prices.append(prev + change)
            
        # Create OHLC from close prices (simplified)
        data = {
            'time': dates,
            'open': [p - np.random.random() for p in prices],
            'high': [p + np.random.random() * 2 for p in prices],
            'low': [p - np.random.random() * 2 for p in prices],
            'close': prices,
            'volume': [int(np.random.normal(1000, 200)) for _ in range(length)]
        }
        return pd.DataFrame(data)

    def get_candles(self, symbol, timeframe, start, end):
        # Parse symbol to determine pattern: "SYNTH-UP", "SYNTH-RANGE", etc.
        if "UP" in symbol: return self.generate_data("UP_TREND")
        if "DOWN" in symbol: return self.generate_data("DOWN_TREND")
        if "RANGE" in symbol: return self.generate_data("RANGING")
        if "VOLATILE" in symbol: return self.generate_data("VOLATILE")
        return self.generate_data("RANGING") # Default

    def get_ticks(self, symbol, start, end):
        return pd.DataFrame() # No ticks for this high-level strategy test

# --- Strategies ---

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

# --- Test Runner ---

def run_strategy_tests():
    data_engine = SyntheticDataEngine()
    results = []
    
    scenarios = [
        {"name": "Trend Following on Up Trend", "symbol": "SYNTH-UP", "strategy": strategy_sma_crossover},
        {"name": "Trend Following on Range", "symbol": "SYNTH-RANGE", "strategy": strategy_sma_crossover},
        {"name": "RSI Reversion on Range", "symbol": "SYNTH-RANGE", "strategy": strategy_rsi_reversion},
        {"name": "RSI Reversion on Up Trend", "symbol": "SYNTH-UP", "strategy": strategy_rsi_reversion},
        {"name": "Bollinger Breakout on Volatile", "symbol": "SYNTH-VOLATILE", "strategy": strategy_bollinger_breakout},
    ]
    
    print("Running Comprehensive Strategy Tests...\n")
    
    for sc in scenarios:
        tm = TradeManager(max_pyramiding=1)
        bt = Backtester(data_engine, tm)
        
        # Run Backtest
        bt.run(sc['symbol'], "1h", "2023-01-01", "2023-01-20", sc['strategy'])
        
        # Generate Professional Report
        reporter = Reporter(tm)
        filename = f"report_{sc['name'].replace(' ', '_')}.html"
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

    # Generate Report
    with open("strategy_performance_report.md", "w") as f:
        f.write("# Strategy Performance Report\n\n")
        f.write("| Scenario | PnL | Trades | Win Rate |\n")
        f.write("| :--- | :--- | :--- | :--- |\n")
        for r in results:
            f.write(f"| {r['Scenario']} | {r['PnL']:.2f} | {r['Trades']} | {r['Win Rate']:.1f}% |\n")
            
    print("Report generated: strategy_performance_report.md")

if __name__ == "__main__":
    run_strategy_tests()
