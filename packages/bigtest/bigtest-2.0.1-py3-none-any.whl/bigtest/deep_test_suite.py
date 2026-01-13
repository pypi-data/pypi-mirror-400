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
        dates = pd.date_range(start=start, periods=10, freq='1h')
        data = {
            'time': dates,
            'open': [100] * 10,
            'high': [110] * 10,
            'low': [90] * 10,
            'close': [100] * 10,
            'volume': [1000] * 10 # Standard volume
        }
        # Low volume candle at index 5
        data['volume'][5] = 1 
        return pd.DataFrame(data)

    def get_ticks(self, symbol, start, end):
        # Dummy ticks
        return pd.DataFrame()

class TestDeepBacktester(unittest.TestCase):
    def setUp(self):
        self.data_engine = MockDataEngine()
        self.trade_manager = TradeManager(max_pyramiding=5)
        self.backtester = Backtester(self.data_engine, self.trade_manager)

    def test_slippage_on_entry(self):
        # Test that low volume causes slippage
        def strategy(df):
            # Buy on candle 5 (Low volume)
            return [{'index': 5, 'type': 'BUY', 'sl': 80, 'tp': 120}]
            
        self.backtester.run("TEST", "1h", "2023-01-01", "2023-01-02", strategy)
        
        trades = self.trade_manager.get_active_trades()
        self.assertEqual(len(trades), 1)
        trade = trades[0]
        
        # Close price is 100.
        # Volume is 1.
        # Slippage formula: 0.0001 * (10000 / (1 + 1)) = 0.5 (capped at 0.01) -> 1%
        # Entry should be 100 * 1.01 = 101
        
        self.assertGreater(trade.entry_price, 100.0)
        self.assertIn("Slip", trade.comment)
        print(f"Entry Price with Slippage: {trade.entry_price}")

    def test_short_selling_pnl(self):
        # Test Short Sell PnL logic
        # Entry at 100, Exit at 90 -> Profit of 10
        
        # We need to manually close or setup a scenario
        # Let's use a manual close via strategy for simplicity? 
        # No, backtester closes on TP/SL.
        
        def strategy(df):
            return [{'index': 0, 'type': 'SELL', 'sl': 120, 'tp': 90}]
            
        # We need price to hit 90.
        # Mock data has Low=90. So TP should be hit.
        
        self.backtester.run("TEST", "1h", "2023-01-01", "2023-01-02", strategy)
        
        closed_trades = self.trade_manager.get_closed_trades()
        self.assertEqual(len(closed_trades), 1)
        trade = closed_trades[0]
        
        # Entry ~100 (minus slippage? Sell -> Price * (1-slip))
        # Exit ~90 (plus slippage? Buy to close -> Price * (1+slip))
        
        self.assertEqual(trade.type, 'SELL')
        self.assertLess(trade.entry_price, 100.0) # Slippage on entry
        self.assertGreater(trade.exit_price, 90.0) # Slippage on exit (TP hit)
        
        # PnL = (Entry - Exit) * Size
        expected_pnl = (trade.entry_price - trade.exit_price) * 1.0
        self.assertAlmostEqual(trade.pnl, expected_pnl)
        self.assertGreater(trade.pnl, 0) # Should be profitable

    def test_pyramiding_limit(self):
        self.trade_manager = TradeManager(max_pyramiding=2)
        self.backtester = Backtester(self.data_engine, self.trade_manager)
        
        def strategy(df):
            return [{'index': i, 'type': 'BUY', 'sl': 50, 'tp': 150} for i in range(5)]
            
        self.backtester.run("TEST", "1h", "2023-01-01", "2023-01-02", strategy)
        
        # Should have 2 active trades
        self.assertEqual(len(self.trade_manager.get_active_trades()), 2)

if __name__ == '__main__':
    unittest.main()
