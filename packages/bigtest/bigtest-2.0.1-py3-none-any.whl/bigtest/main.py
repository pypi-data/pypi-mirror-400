import os
from dotenv import load_dotenv
from data_engine import DataEngine
from strategy_engine import StrategyEngine
from trade_manager import TradeManager
from backtester import Backtester
import pythonpine as pp

# Load environment variables
load_dotenv()
API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")

def simple_strategy(df):
    """
    Example Strategy: SMA Crossover
    Buy when SMA(10) crosses over SMA(20).
    Sell when SMA(10) crosses under SMA(20).
    """
    signals = []
    
    # Calculate Indicators using PythonPine
    # Note: pythonpine expects lists
    closes = df['close'].tolist()
    sma10 = pp.sma(closes, 10)
    sma20 = pp.sma(closes, 20)
    
    # Generate Signals
    for i in range(20, len(df)):
        # Crossover: SMA10 > SMA20 now AND SMA10 <= SMA20 before
        if sma10[i] > sma20[i] and sma10[i-1] <= sma20[i-1]:
            signals.append({
                'index': i,
                'type': 'BUY',
                'sl': df['close'].iloc[i] * 0.99, # 1% SL
                'tp': df['close'].iloc[i] * 1.02, # 2% TP
                'comment': 'SMA Crossover Buy'
            })
        
        # Crossunder: SMA10 < SMA20 now AND SMA10 >= SMA20 before
        elif sma10[i] < sma20[i] and sma10[i-1] >= sma20[i-1]:
             signals.append({
                'index': i,
                'type': 'SELL',
                'sl': df['close'].iloc[i] * 1.01, # 1% SL
                'tp': df['close'].iloc[i] * 0.98, # 2% TP
                'comment': 'SMA Crossover Sell'
            })
            
    return signals

def main():
    # 1. Initialize Components
    data_engine = DataEngine(api_key=API_KEY, secret_key=SECRET_KEY)
    strategy_engine = StrategyEngine() # Not strictly needed if we pass func, but good for structure
    trade_manager = TradeManager(max_pyramiding=1)
    
    backtester = Backtester(data_engine, trade_manager)
    
    # 2. Run Backtest
    # Using a crypto symbol for easy testing with Alpaca/Binance
    symbol = "BTC/USD" 
    timeframe = "1h"
    start_str = "2023-01-01-00-00-00"
    end_str = "2023-01-05-00-00-00"
    
    backtester.run(
        symbol=symbol,
        timeframe=timeframe,
        start_str=start_str,
        end_str=end_str,
        strategy_func=simple_strategy
    )

if __name__ == "__main__":
    main()
