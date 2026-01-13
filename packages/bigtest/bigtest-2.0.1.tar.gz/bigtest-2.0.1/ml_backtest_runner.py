"""
ML Backtest Runner
Runs the ML Scalping Strategy backtest on EUR/USD and generates reports.
"""

import sys
import os
from datetime import datetime, timedelta

# Add paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backtester import Backtester
from data_engine import DataEngine
from trade_manager import TradeManager
from reporter import Reporter
from ml_scalping_strategy import ml_scalping_strategy, ML_AVAILABLE


def run_ml_backtest(symbol="EUR/USD", timeframe="15m", days=30, initial_capital=10000):
    """
    Run ML Scalping Strategy backtest.
    
    Args:
        symbol: Trading pair
        timeframe: Candle timeframe
        days: Number of days to backtest
        initial_capital: Starting capital
    """
    print("\n" + "=" * 70)
    print("ML SCALPING STRATEGY BACKTEST")
    print("=" * 70)
    
    if not ML_AVAILABLE:
        print("ERROR: scikit-learn is required. Install with: pip install scikit-learn")
        return None
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")
    
    print(f"Symbol: {symbol}")
    print(f"Timeframe: {timeframe}")
    print(f"Period: {start_str} to {end_str} ({days} days)")
    print(f"Initial Capital: ${initial_capital:,.2f}")
    print("=" * 70)
    
    # Initialize components
    data_engine = DataEngine()
    trade_manager = TradeManager(initial_capital=initial_capital, max_pyramiding=1)
    backtester = Backtester(data_engine, trade_manager)
    
    # Create strategy wrapper
    def strategy_wrapper(df):
        return ml_scalping_strategy(df, symbol)
    
    try:
        # Run backtest
        print("\n[Runner] Starting backtest...")
        backtester.run(
            symbol=symbol,
            timeframe=timeframe,
            start_str=start_str,
            end_str=end_str,
            strategy_func=strategy_wrapper,
            initial_capital=initial_capital,
            commission_rate=0.00002  # 0.002% commission (forex)
        )
        
        # Generate report
        reporter = Reporter(trade_manager)
        safe_symbol = symbol.replace("/", "_")
        report_file = f"report_ML_SCALP_{safe_symbol}_{timeframe}.html"
        reporter.generate_html_report(report_file, start_str, end_str)
        
        # Calculate statistics
        closed_trades = trade_manager.get_closed_trades()
        total_pnl = trade_manager.get_total_pnl()
        
        wins = [t for t in closed_trades if t.pnl > 0]
        losses = [t for t in closed_trades if t.pnl <= 0]
        
        # Print results
        print("\n" + "=" * 70)
        print("BACKTEST RESULTS")
        print("=" * 70)
        print(f"Total Trades: {len(closed_trades)}")
        print(f"Winning Trades: {len(wins)}")
        print(f"Losing Trades: {len(losses)}")
        
        if closed_trades:
            win_rate = len(wins) / len(closed_trades) * 100
            print(f"Win Rate: {win_rate:.1f}%")
            
            # Profit Factor
            gross_profit = sum(t.pnl for t in wins) if wins else 0
            gross_loss = abs(sum(t.pnl for t in losses)) if losses else 1
            profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
            print(f"Profit Factor: {profit_factor:.2f}")
            
            # Average trade
            avg_win = gross_profit / len(wins) if wins else 0
            avg_loss = gross_loss / len(losses) if losses else 0
            print(f"Average Win: ${avg_win:.2f}")
            print(f"Average Loss: ${avg_loss:.2f}")
        
        print(f"\nTotal PnL: ${total_pnl:.2f}")
        print(f"Final Capital: ${trade_manager.current_capital:.2f}")
        print(f"Return: {(total_pnl / initial_capital) * 100:.2f}%")
        
        # Max Drawdown
        if trade_manager.drawdown_curve:
            max_dd = max(d['drawdown'] for d in trade_manager.drawdown_curve)
            print(f"Max Drawdown: {max_dd:.2f}%")
        
        print(f"\nReport saved: {report_file}")
        print("=" * 70)
        
        return {
            'symbol': symbol,
            'timeframe': timeframe,
            'trades': len(closed_trades),
            'wins': len(wins),
            'losses': len(losses),
            'pnl': total_pnl,
            'return_pct': (total_pnl / initial_capital) * 100,
            'report': report_file
        }
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None


def run_multi_timeframe_test():
    """Run tests on multiple timeframes for comparison"""
    print("\n" + "=" * 70)
    print("ML SCALPING STRATEGY - MULTI-TIMEFRAME TEST")
    print("=" * 70)
    
    results = []
    
    # Test on 15m (primary scalping timeframe)
    result = run_ml_backtest("EUR/USD", "15m", days=30)
    if result:
        results.append(result)
    
    # Print comparison
    if results:
        print("\n" + "=" * 70)
        print("COMPARISON SUMMARY")
        print("=" * 70)
        print(f"{'Timeframe':<12} {'Trades':<10} {'Win %':<10} {'PnL':<12} {'Return':<10}")
        print("-" * 54)
        for r in results:
            win_pct = (r['wins'] / r['trades'] * 100) if r['trades'] > 0 else 0
            print(f"{r['timeframe']:<12} {r['trades']:<10} {win_pct:<10.1f} ${r['pnl']:<11.2f} {r['return_pct']:<10.2f}%")
        print("=" * 70)
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="ML Scalping Strategy Backtest")
    parser.add_argument("--symbol", default="EUR/USD", help="Trading symbol")
    parser.add_argument("--timeframe", default="15m", help="Timeframe")
    parser.add_argument("--days", type=int, default=30, help="Days to backtest")
    parser.add_argument("--capital", type=int, default=10000, help="Initial capital")
    parser.add_argument("--multi", action="store_true", help="Run multi-timeframe test")
    
    args = parser.parse_args()
    
    if args.multi:
        run_multi_timeframe_test()
    else:
        run_ml_backtest(args.symbol, args.timeframe, args.days, args.capital)
