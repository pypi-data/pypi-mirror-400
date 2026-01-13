"""
Analytics Engine - Deep Performance Metrics
Professional-grade backtesting analytics like Pine Script / MT4
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import math


@dataclass
class PerformanceMetrics:
    """Comprehensive performance metrics"""
    # Basic
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    breakeven_trades: int = 0
    
    # Returns
    net_profit: float = 0.0
    gross_profit: float = 0.0
    gross_loss: float = 0.0
    profit_factor: float = 0.0
    expected_payoff: float = 0.0
    
    # Rates
    win_rate: float = 0.0
    loss_rate: float = 0.0
    
    # Average Trade
    avg_profit: float = 0.0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    avg_win_loss_ratio: float = 0.0
    
    # Extremes
    largest_win: float = 0.0
    largest_loss: float = 0.0
    
    # Streaks
    max_consecutive_wins: int = 0
    max_consecutive_losses: int = 0
    current_streak: int = 0
    current_streak_type: str = ''
    
    # Drawdown
    max_drawdown: float = 0.0
    max_drawdown_pct: float = 0.0
    max_drawdown_duration: int = 0  # In bars/days
    avg_drawdown: float = 0.0
    
    # Risk-Adjusted
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    calmar_ratio: float = 0.0
    recovery_factor: float = 0.0
    
    # R-Multiple Stats
    avg_r_multiple: float = 0.0
    total_r: float = 0.0
    expectancy_r: float = 0.0
    
    # Duration
    avg_trade_duration: Any = None
    avg_winning_duration: Any = None
    avg_losing_duration: Any = None
    
    # Capital
    initial_capital: float = 0.0
    final_capital: float = 0.0
    total_return_pct: float = 0.0
    cagr: float = 0.0
    
    # Costs
    total_commission: float = 0.0
    total_slippage: float = 0.0


class AnalyticsEngine:
    """
    Professional analytics engine for backtesting results.
    Calculates comprehensive performance metrics.
    """
    
    def __init__(self):
        self.trades: List[Dict] = []
        self.equity_curve: List[Dict] = []
        self.initial_capital: float = 0.0
        self.final_capital: float = 0.0
    
    def calculate_metrics(self, trades: List[Dict], equity_curve: List[Dict], 
                          initial_capital: float, final_capital: float,
                          total_commission: float = 0.0, 
                          total_slippage: float = 0.0) -> PerformanceMetrics:
        """
        Calculate all performance metrics from trade history.
        
        Args:
            trades: List of completed trades
            equity_curve: Equity curve data
            initial_capital: Starting capital
            final_capital: Ending capital
        
        Returns:
            PerformanceMetrics object
        """
        self.trades = trades
        self.equity_curve = equity_curve
        self.initial_capital = initial_capital
        self.final_capital = final_capital
        
        metrics = PerformanceMetrics()
        metrics.initial_capital = initial_capital
        metrics.final_capital = final_capital
        metrics.total_commission = total_commission
        metrics.total_slippage = total_slippage
        
        if not trades:
            return metrics
        
        # Basic counts
        metrics.total_trades = len(trades)
        wins = [t for t in trades if t['pnl'] > 0]
        losses = [t for t in trades if t['pnl'] < 0]
        breakeven = [t for t in trades if t['pnl'] == 0]
        
        metrics.winning_trades = len(wins)
        metrics.losing_trades = len(losses)
        metrics.breakeven_trades = len(breakeven)
        
        # Returns
        metrics.gross_profit = sum(t['pnl'] for t in wins)
        metrics.gross_loss = abs(sum(t['pnl'] for t in losses))
        metrics.net_profit = metrics.gross_profit - metrics.gross_loss
        
        # Rates
        if metrics.total_trades > 0:
            metrics.win_rate = metrics.winning_trades / metrics.total_trades
            metrics.loss_rate = metrics.losing_trades / metrics.total_trades
        
        # Profit Factor
        if metrics.gross_loss > 0:
            metrics.profit_factor = metrics.gross_profit / metrics.gross_loss
        else:
            metrics.profit_factor = float('inf') if metrics.gross_profit > 0 else 0
        
        # Average Trade
        if metrics.total_trades > 0:
            metrics.avg_profit = metrics.net_profit / metrics.total_trades
            metrics.expected_payoff = metrics.avg_profit
        
        if wins:
            metrics.avg_win = metrics.gross_profit / len(wins)
        if losses:
            metrics.avg_loss = metrics.gross_loss / len(losses)
        
        if metrics.avg_loss > 0:
            metrics.avg_win_loss_ratio = metrics.avg_win / metrics.avg_loss
        
        # Extremes
        if wins:
            metrics.largest_win = max(t['pnl'] for t in wins)
        if losses:
            metrics.largest_loss = min(t['pnl'] for t in losses)
        
        # Streaks
        metrics.max_consecutive_wins, metrics.max_consecutive_losses = self._calculate_streaks(trades)
        
        # Drawdown
        dd_stats = self._calculate_drawdown(equity_curve, initial_capital)
        metrics.max_drawdown = dd_stats['max_dd']
        metrics.max_drawdown_pct = dd_stats['max_dd_pct']
        metrics.max_drawdown_duration = dd_stats['max_dd_duration']
        metrics.avg_drawdown = dd_stats['avg_dd']
        
        # Risk-Adjusted Returns
        metrics.sharpe_ratio = self._calculate_sharpe(trades)
        metrics.sortino_ratio = self._calculate_sortino(trades)
        
        if metrics.max_drawdown_pct > 0:
            metrics.recovery_factor = metrics.net_profit / metrics.max_drawdown
            # Annualized return for Calmar
            if len(equity_curve) > 1:
                days = (equity_curve[-1].get('time', datetime.now()) - 
                       equity_curve[0].get('time', datetime.now())).days
                if days > 0:
                    annual_return = (metrics.net_profit / initial_capital) * (365 / days)
                    metrics.calmar_ratio = annual_return / metrics.max_drawdown_pct
        
        # R-Multiple Stats
        r_values = [t.get('r_multiple', 0) for t in trades if 'r_multiple' in t]
        if r_values:
            metrics.avg_r_multiple = np.mean(r_values)
            metrics.total_r = sum(r_values)
            metrics.expectancy_r = np.mean(r_values)
        
        # Duration
        durations = [t['duration'] for t in trades if t.get('duration')]
        if durations:
            total_seconds = sum(d.total_seconds() for d in durations if hasattr(d, 'total_seconds'))
            if total_seconds > 0:
                metrics.avg_trade_duration = timedelta(seconds=total_seconds/len(durations))
        
        win_durations = [t['duration'] for t in wins if t.get('duration')]
        if win_durations:
            total_seconds = sum(d.total_seconds() for d in win_durations if hasattr(d, 'total_seconds'))
            if total_seconds > 0:
                metrics.avg_winning_duration = timedelta(seconds=total_seconds/len(win_durations))
        
        loss_durations = [t['duration'] for t in losses if t.get('duration')]
        if loss_durations:
            total_seconds = sum(d.total_seconds() for d in loss_durations if hasattr(d, 'total_seconds'))
            if total_seconds > 0:
                metrics.avg_losing_duration = timedelta(seconds=total_seconds/len(loss_durations))
        
        # Capital Returns
        metrics.total_return_pct = (final_capital - initial_capital) / initial_capital * 100
        
        # CAGR
        if len(equity_curve) > 1:
            start_time = equity_curve[0].get('time')
            end_time = equity_curve[-1].get('time')
            if start_time and end_time:
                years = (end_time - start_time).days / 365.25
                if years > 0 and initial_capital > 0:
                    metrics.cagr = ((final_capital / initial_capital) ** (1/years) - 1) * 100
        
        return metrics
    
    def _calculate_streaks(self, trades: List[Dict]) -> tuple:
        """Calculate max consecutive wins and losses"""
        max_wins = 0
        max_losses = 0
        current_wins = 0
        current_losses = 0
        
        for t in trades:
            if t['pnl'] > 0:
                current_wins += 1
                current_losses = 0
                max_wins = max(max_wins, current_wins)
            elif t['pnl'] < 0:
                current_losses += 1
                current_wins = 0
                max_losses = max(max_losses, current_losses)
            else:
                current_wins = 0
                current_losses = 0
        
        return max_wins, max_losses
    
    def _calculate_drawdown(self, equity_curve: List[Dict], initial_capital: float) -> Dict:
        """Calculate drawdown statistics"""
        if not equity_curve:
            return {'max_dd': 0, 'max_dd_pct': 0, 'max_dd_duration': 0, 'avg_dd': 0}
        
        equities = [e.get('equity', initial_capital) for e in equity_curve]
        
        peak = equities[0]
        max_dd = 0
        max_dd_pct = 0
        drawdowns = []
        dd_duration = 0
        max_dd_duration = 0
        
        for eq in equities:
            if eq > peak:
                peak = eq
                dd_duration = 0
            
            dd = peak - eq
            dd_pct = dd / peak if peak > 0 else 0
            
            if dd > max_dd:
                max_dd = dd
                max_dd_pct = dd_pct
            
            if dd > 0:
                dd_duration += 1
                max_dd_duration = max(max_dd_duration, dd_duration)
            
            drawdowns.append(dd_pct)
        
        avg_dd = np.mean(drawdowns) if drawdowns else 0
        
        return {
            'max_dd': max_dd,
            'max_dd_pct': max_dd_pct,
            'max_dd_duration': max_dd_duration,
            'avg_dd': avg_dd
        }
    
    def _calculate_sharpe(self, trades: List[Dict], risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe Ratio"""
        if len(trades) < 2:
            return 0.0
        
        returns = [t['pnl_pct'] for t in trades if 'pnl_pct' in t]
        if not returns:
            returns = [t['pnl'] / self.initial_capital for t in trades]
        
        if not returns or np.std(returns) == 0:
            return 0.0
        
        # Annualize
        avg_return = np.mean(returns)
        std_return = np.std(returns)
        
        # Assuming ~252 trading days
        trades_per_year = 252 * len(trades) / max(1, len(self.equity_curve))
        
        annualized_return = avg_return * trades_per_year
        annualized_std = std_return * np.sqrt(trades_per_year)
        
        if annualized_std == 0:
            return 0.0
        
        sharpe = (annualized_return - risk_free_rate) / annualized_std
        return sharpe
    
    def _calculate_sortino(self, trades: List[Dict], risk_free_rate: float = 0.02) -> float:
        """Calculate Sortino Ratio (only downside volatility)"""
        if len(trades) < 2:
            return 0.0
        
        returns = [t['pnl_pct'] for t in trades if 'pnl_pct' in t]
        if not returns:
            returns = [t['pnl'] / self.initial_capital for t in trades]
        
        # Only negative returns
        negative_returns = [r for r in returns if r < 0]
        
        if not negative_returns:
            return float('inf') if np.mean(returns) > 0 else 0.0
        
        avg_return = np.mean(returns)
        downside_std = np.std(negative_returns)
        
        if downside_std == 0:
            return 0.0
        
        # Annualize
        trades_per_year = 252 * len(trades) / max(1, len(self.equity_curve))
        annualized_return = avg_return * trades_per_year
        annualized_downside = downside_std * np.sqrt(trades_per_year)
        
        sortino = (annualized_return - risk_free_rate) / annualized_downside
        return sortino
    
    def get_monthly_breakdown(self, trades: List[Dict]) -> pd.DataFrame:
        """Get PnL breakdown by month"""
        if not trades:
            return pd.DataFrame()
        
        monthly = {}
        for t in trades:
            if 'exit_time' in t and t['exit_time']:
                key = t['exit_time'].strftime('%Y-%m')
                if key not in monthly:
                    monthly[key] = {'pnl': 0, 'trades': 0, 'wins': 0}
                monthly[key]['pnl'] += t['pnl']
                monthly[key]['trades'] += 1
                if t['pnl'] > 0:
                    monthly[key]['wins'] += 1
        
        return pd.DataFrame.from_dict(monthly, orient='index')
    
    def get_daily_breakdown(self, trades: List[Dict]) -> pd.DataFrame:
        """Get PnL breakdown by day of week"""
        if not trades:
            return pd.DataFrame()
        
        days = {i: {'pnl': 0, 'trades': 0, 'wins': 0} for i in range(7)}
        day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        
        for t in trades:
            if 'exit_time' in t and t['exit_time']:
                dow = t['exit_time'].weekday()
                days[dow]['pnl'] += t['pnl']
                days[dow]['trades'] += 1
                if t['pnl'] > 0:
                    days[dow]['wins'] += 1
        
        df = pd.DataFrame.from_dict(days, orient='index')
        df.index = [day_names[i] for i in df.index]
        return df
    
    def format_metrics_report(self, metrics: PerformanceMetrics) -> str:
        """Format metrics as readable text report"""
        lines = [
            "=" * 60,
            "PERFORMANCE REPORT",
            "=" * 60,
            "",
            "--- OVERVIEW ---",
            f"Total Trades: {metrics.total_trades}",
            f"Net Profit: ${metrics.net_profit:,.2f}",
            f"Total Return: {metrics.total_return_pct:.2f}%",
            "",
            "--- WIN/LOSS ---",
            f"Winning Trades: {metrics.winning_trades} ({metrics.win_rate*100:.1f}%)",
            f"Losing Trades: {metrics.losing_trades} ({metrics.loss_rate*100:.1f}%)",
            f"Profit Factor: {metrics.profit_factor:.2f}",
            "",
            "--- AVERAGES ---",
            f"Avg Trade: ${metrics.avg_profit:,.2f}",
            f"Avg Win: ${metrics.avg_win:,.2f}",
            f"Avg Loss: ${metrics.avg_loss:,.2f}",
            f"Win/Loss Ratio: {metrics.avg_win_loss_ratio:.2f}",
            "",
            "--- EXTREMES ---",
            f"Largest Win: ${metrics.largest_win:,.2f}",
            f"Largest Loss: ${metrics.largest_loss:,.2f}",
            f"Max Consecutive Wins: {metrics.max_consecutive_wins}",
            f"Max Consecutive Losses: {metrics.max_consecutive_losses}",
            "",
            "--- DRAWDOWN ---",
            f"Max Drawdown: ${metrics.max_drawdown:,.2f} ({metrics.max_drawdown_pct*100:.2f}%)",
            f"Max DD Duration: {metrics.max_drawdown_duration} bars",
            "",
            "--- RISK-ADJUSTED ---",
            f"Sharpe Ratio: {metrics.sharpe_ratio:.2f}",
            f"Sortino Ratio: {metrics.sortino_ratio:.2f}",
            f"Calmar Ratio: {metrics.calmar_ratio:.2f}",
            f"Recovery Factor: {metrics.recovery_factor:.2f}",
            "",
            "--- R-MULTIPLES ---",
            f"Avg R: {metrics.avg_r_multiple:.2f}",
            f"Total R: {metrics.total_r:.2f}",
            f"Expectancy: {metrics.expectancy_r:.2f}R",
            "",
            "=" * 60
        ]
        return "\n".join(lines)


if __name__ == "__main__":
    print("Analytics Engine - Deep performance metrics")
