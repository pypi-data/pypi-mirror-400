import unittest
import pandas as pd
from datetime import datetime, timedelta
from trade_manager import TradeManager
from backtester import Backtester
from data_engine import DataEngine

class MockDataEngine(DataEngine):
    def __init__(self):
        pass
        
    def get_candles(self, symbol, timeframe, start, end):
        # Create dummy candles
        dates = pd.date_range(start=start, periods=5, freq='1h')
        data = {
            'time': dates,
            'open': [100, 102, 105, 103, 101],
            'high': [103, 106, 108, 104, 102],
            'low': [99, 101, 102, 100, 98],
            'close': [102, 105, 103, 101, 99],
            'volume': [1000] * 5
        }
        return pd.DataFrame(data)

    def get_ticks(self, symbol, start, end):
        # Create dummy ticks for a specific candle
        # Let's say we want to test tick resolution for the 3rd candle (index 2)
        # Candle: O=105, H=108, L=102, C=103. Time: dates[2]
        
        # Ticks: 105 -> 107 -> 102 (SL hit?) -> 108 (TP hit?) -> 103
        
        # We need to parse start string to match
        start_dt = datetime.strptime(start, "%Y-%m-%d-%H-%M-%S")
        
        ticks_data = {
            'time': [start_dt + timedelta(minutes=i) for i in range(5)],
            'price': [105, 107, 102, 108, 103],
            'volume': [100] * 5
        }
        return pd.DataFrame(ticks_data)

class TestBacktester(unittest.TestCase):
    def setUp(self):
        self.data_engine = MockDataEngine()
        self.trade_manager = TradeManager()
        self.backtester = Backtester(self.data_engine, self.trade_manager)

    def test_tick_resolution_sl(self):
        # Strategy: Buy at index 1 (Close=105). SL=102.5, TP=110.
        # Next candle (index 2): Low=102. SL should be hit.
        # Ticks: 105 -> 107 -> 102. SL (102.5) should be hit at 102 tick.
        
        def mock_strategy(df):
            return [{
                'index': 1,
                'type': 'BUY',
                'sl': 102.5,
                'tp': 110.0,
                'comment': 'Test Trade'
            }]
            
        self.backtester.run("TEST", "1h", "2023-01-01-00-00-00", "2023-01-01-10-00-00", mock_strategy)
        
        closed_trades = self.trade_manager.get_closed_trades()
        self.assertEqual(len(closed_trades), 1)
        trade = closed_trades[0]
        self.assertEqual(trade.status, 'CLOSED')
        self.assertEqual(trade.exit_price, 102.5) # SL price
        self.assertIn("Tick", trade.comment) # Should be tick resolution 
        # Wait, my backtester logic sets exit price to SL price if hit.
        
    def test_pyramiding(self):
        # Strategy: Buy at every candle. Max pyramiding = 1.
        def mock_strategy(df):
            return [{'index': i, 'type': 'BUY', 'sl': 90, 'tp': 120} for i in range(5)]
            
        self.backtester.run("TEST", "1h", "2023-01-01-00-00-00", "2023-01-01-10-00-00", mock_strategy)
        
        # Should only have 1 active trade (or closed and opened new one)
        # Since SL/TP not hit for most, we should see if multiple opened.
        # Candle 1: Open trade.
        # Candle 2: Signal. Pyramiding check -> Deny.
        # ...
        self.assertEqual(len(self.trade_manager.trades), 1)

if __name__ == '__main__':
    unittest.main()
