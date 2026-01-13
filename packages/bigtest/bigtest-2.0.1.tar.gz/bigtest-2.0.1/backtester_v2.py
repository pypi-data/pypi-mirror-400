"""
Backtester V2 - Industry-Grade Backtesting Engine
Main engine with correct TP/SL logic and deep analytics
"""

from typing import Callable, List, Dict, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from .backtest_config import BacktestConfig, TradeSignal
from .trade_simulator import TradeSimulator, Position
from .analytics import AnalyticsEngine, PerformanceMetrics
from .report_generator import ReportGenerator


class BacktestEngine:
    """
    Industry-grade backtesting engine with:
    - Correct TP/SL detection logic
    - Optimized tick fetching (only when needed)
    - Comprehensive analytics
    - Professional reporting
    
    Usage:
        config = BacktestConfig(symbol='EUR/USD', ...)
        engine = BacktestEngine(config)
        results = engine.run(my_strategy)
    """
    
    def __init__(self, config: BacktestConfig):
        """
        Initialize backtesting engine.
        
        Args:
            config: BacktestConfig with all settings
        """
        self.config = config
        self.simulator = TradeSimulator(config)
        self.analytics = AnalyticsEngine()
        
        # Data
        self.candles: pd.DataFrame = None
        self.tick_cache: Dict[str, pd.DataFrame] = {}
        self.tick_batch_loaded: bool = False
        
        # Equity tracking
        self.equity_curve: List[Dict] = []
        
        # Results
        self.metrics: PerformanceMetrics = None
    
    def run(self, strategy_func: Callable[[pd.DataFrame], List[Dict]], 
            data: pd.DataFrame = None) -> PerformanceMetrics:
        """
        Run backtest with given strategy.
        
        Args:
            strategy_func: Strategy function that takes DataFrame and returns signals
            data: Optional pre-loaded candle data
        
        Returns:
            PerformanceMetrics with full results
        """
        print(f"--- Starting Backtest for {self.config.symbol} ---")
        print(f"Period: {self.config.start_date} to {self.config.end_date}")
        print(f"Timeframe: {self.config.timeframe}")
        print(f"Capital: ${self.config.initial_capital:,.0f} | Leverage: {self.config.leverage}:1")
        print()
        
        # Reset state
        self.simulator.reset()
        self.equity_curve = []
        self.tick_cache = {}
        
        # Load data
        if data is not None:
            self.candles = data
        else:
            self.candles = self._load_candles()
        
        if self.candles is None or self.candles.empty:
            print("ERROR: No data loaded!")
            return PerformanceMetrics()
        
        print(f"Loaded {len(self.candles)} candles")
        
        # Generate signals from strategy
        print("Running strategy...")
        signals = strategy_func(self.candles)
        signals_by_index = {s['index']: s for s in signals}
        print(f"Strategy generated {len(signals)} signals")
        print()
        
        # Initialize equity curve
        self.equity_curve.append({
            'time': self.candles.iloc[0]['time'],
            'equity': self.config.initial_capital
        })
        
        # Main backtest loop
        print("Processing candles...")
        for i in range(len(self.candles)):
            candle = self.candles.iloc[i].to_dict()
            current_time = candle['time']
            
            # Update daily tracking
            self.simulator.update_daily_tracking(current_time)
            
            # Check session filter
            if not self.config.is_trading_allowed(current_time):
                continue
            
            # ========== A. CHECK EXITS FOR OPEN POSITIONS ==========
            positions_to_close = []
            
            for position in self.simulator.positions:
                # Check if TP/SL hit
                exit_reason, exit_price = self.simulator.check_exit(position, candle)
                
                if exit_reason:
                    # Check if tick resolution needed (ambiguous case)
                    if self.simulator.is_tick_fetch_needed(position, candle):
                        ticks = self._get_ticks_for_candle(current_time)
                        if ticks is not None and not ticks.empty:
                            exit_reason, exit_price = self.simulator.resolve_with_ticks(position, ticks)
                    
                    if exit_reason:
                        positions_to_close.append((position, exit_price, exit_reason))
            
            # Close positions (after iteration to avoid modification during loop)
            for position, exit_price, reason in positions_to_close:
                self.simulator.close_position(position, exit_price, current_time, reason)
            
                # ========== B. CHECK FOR LIQUIDATION (100x Leverage) ==========
            if self.config.stop_out_enabled:
                liquidated = self.simulator.check_liquidation(candle)
                for position, liq_price in liquidated:
                    self.simulator.close_position(position, liq_price, current_time, 'LIQUIDATION')
            
            # ========== C. PROCESS PENDING LIMIT ORDERS ==========
            if hasattr(self.simulator, 'process_pending_orders'):
                self.simulator.process_pending_orders(candle)
            
            # ========== D. CHECK FOR NEW SIGNALS (i+1 EXECUTION) ==========
            # CRITICAL: Signals generated at bar i-1 execute on OPEN of bar i
            # This eliminates look-ahead bias - strategy has NO knowledge of current candle
            if (i - 1) in signals_by_index:
                signal_dict = signals_by_index[i - 1]
                
                # Convert to TradeSignal
                signal = TradeSignal(
                    index=signal_dict['index'],
                    time=signal_dict.get('time', current_time),
                    type=signal_dict['type'],
                    entry_price=candle['open'],  # FORCE entry at current bar's OPEN
                    sl=signal_dict.get('sl'),
                    tp=signal_dict.get('tp'),
                    size=signal_dict.get('size'),
                    risk=signal_dict.get('risk'),
                    comment=signal_dict.get('comment', '')
                )
                
                # Open position
                self.simulator.open_position(signal, candle)
            
            # ========== E. UPDATE EQUITY CURVE ==========
            equity = self.simulator.get_equity(candle['close'])
            self.equity_curve.append({
                'time': current_time,
                'equity': equity,
                'margin_used': self.simulator.calculate_margin_used() if hasattr(self.simulator, 'calculate_margin_used') else 0
            })
        
        # ========== F. CLOSE REMAINING POSITIONS ==========
        if self.config.close_at_end and self.simulator.positions:
            final_candle = self.candles.iloc[-1].to_dict()
            final_price = final_candle['close']
            final_time = final_candle['time']
            
            print(f"Closing {len(self.simulator.positions)} open positions at end of backtest")
            for position in list(self.simulator.positions):
                self.simulator.close_position(position, final_price, final_time, 'End of Backtest')
        
        # ========== E. CALCULATE ANALYTICS ==========
        print()
        print("Calculating performance metrics...")
        self.metrics = self.analytics.calculate_metrics(
            trades=self.simulator.closed_trades,
            equity_curve=self.equity_curve,
            initial_capital=self.config.initial_capital,
            final_capital=self.simulator.current_capital,
            total_commission=self.simulator.total_commission,
            total_slippage=self.simulator.total_slippage
        )
        
        # Print summary
        self._print_summary()
        
        return self.metrics
    
    def _load_candles(self) -> pd.DataFrame:
        """Load candle data using finda or fallback"""
        try:
            # Try finda first
            from finda import Finda
            finder = Finda()
            df = finder.get_candles(
                self.config.symbol,
                self.config.timeframe,
                self.config.start_date,
                self.config.end_date
            )
            print(f"[finda] Data loaded successfully")
            return df
        except ImportError:
            print("[finda] Not available, trying DataEngine...")
        except Exception as e:
            print(f"[finda] Error: {e}, trying DataEngine...")
        
        try:
            # Fallback to existing DataEngine
            from data_engine import DataEngine
            engine = DataEngine()
            df = engine.get_candles(
                self.config.symbol,
                self.config.timeframe,
                self.config.start_date,
                self.config.end_date
            )
            return df
        except Exception as e:
            print(f"[DataEngine] Error: {e}")
            return pd.DataFrame()
    
    def _get_ticks_for_candle(self, candle_time) -> Optional[pd.DataFrame]:
        """Get tick data for specific candle (with caching)"""
        cache_key = str(candle_time)
        
        if cache_key in self.tick_cache:
            return self.tick_cache[cache_key]
        
        try:
            from data_engine import DataEngine
            engine = DataEngine()
            
            start = candle_time
            end = candle_time + timedelta(minutes=1)
            
            ticks = engine.get_ticks(
                self.config.symbol,
                start.strftime("%Y-%m-%d-%H-%M-%S"),
                end.strftime("%Y-%m-%d-%H-%M-%S")
            )
            
            self.tick_cache[cache_key] = ticks
            return ticks
        except Exception as e:
            return None
    
    def _print_summary(self):
        """Print backtest summary"""
        m = self.metrics
        
        print()
        print("=" * 60)
        print("BACKTEST RESULTS")
        print("=" * 60)
        print(f"Symbol: {self.config.symbol} | Timeframe: {self.config.timeframe}")
        print(f"Period: {self.config.start_date} to {self.config.end_date}")
        print("-" * 60)
        print(f"Total Trades: {m.total_trades}")
        print(f"Win Rate: {m.win_rate*100:.1f}% ({m.winning_trades}W / {m.losing_trades}L)")
        print(f"Profit Factor: {m.profit_factor:.2f}")
        print("-" * 60)
        print(f"Net Profit: ${m.net_profit:,.2f}")
        print(f"Total Return: {m.total_return_pct:.2f}%")
        print(f"Max Drawdown: {m.max_drawdown_pct*100:.2f}%")
        print("-" * 60)
        print(f"Sharpe Ratio: {m.sharpe_ratio:.2f}")
        print(f"Sortino Ratio: {m.sortino_ratio:.2f}")
        print(f"Recovery Factor: {m.recovery_factor:.2f}")
        print("=" * 60)
    
    def get_trades_df(self) -> pd.DataFrame:
        """Get all trades as DataFrame"""
        return pd.DataFrame(self.simulator.closed_trades)
    
    def get_equity_df(self) -> pd.DataFrame:
        """Get equity curve as DataFrame"""
        return pd.DataFrame(self.equity_curve)
    
    def generate_report(self, filename: str = None) -> str:
        """Generate text report"""
        if self.metrics is None:
            return "No backtest results available"
        
        report = self.analytics.format_metrics_report(self.metrics)
        
        if filename:
            with open(filename, 'w') as f:
                f.write(report)
            print(f"Report saved to {filename}")
        
        return report
    
    def generate_html_report(self, filename: str = 'backtest_report.html') -> str:
        """
        Generate comprehensive HTML report with charts.
        
        Args:
            filename: Output filename
        
        Returns:
            Path to generated report
        """
        if self.metrics is None:
            print("No backtest results available. Run backtest first.")
            return ""
        
        report_gen = ReportGenerator()
        return report_gen.generate_html_report(
            trades=self.simulator.closed_trades,
            equity_curve=self.equity_curve,
            metrics=self.metrics,
            config=self.config,
            filename=filename
        )


# Convenience function
def run_backtest(symbol: str, timeframe: str, start: str, end: str,
                 strategy_func: Callable, **kwargs) -> PerformanceMetrics:
    """
    Quick backtest runner.
    
    Args:
        symbol: Trading symbol
        timeframe: Candle timeframe
        start: Start date
        end: End date
        strategy_func: Strategy function
        **kwargs: Additional BacktestConfig options
    
    Returns:
        PerformanceMetrics
    """
    config = BacktestConfig(
        symbol=symbol,
        timeframe=timeframe,
        start_date=start,
        end_date=end,
        **kwargs
    )
    
    engine = BacktestEngine(config)
    return engine.run(strategy_func)


if __name__ == "__main__":
    print("Backtester V2 - Industry-Grade Engine")
    print("Usage: from backtester_v2 import BacktestEngine, BacktestConfig")
