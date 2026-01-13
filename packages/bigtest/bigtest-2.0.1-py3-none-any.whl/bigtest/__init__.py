"""
BigTest - Holy Grail Backtester v2.0
Institutional-grade backtesting engine for quantitative trading research.
"""

from .backtester_v2 import BacktestEngine, run_backtest
from .backtest_config import BacktestConfig, TradeSignal, TradeResult
from .trade_simulator import TradeSimulator, Position, LimitOrder
from .analytics import AnalyticsEngine, PerformanceMetrics
from .data_engine import DataEngine
from .report_generator import ReportGenerator

__version__ = "2.0.1"
__author__ = "Kushal Garg"

__all__ = [
    "BacktestEngine",
    "BacktestConfig", 
    "TradeSignal",
    "TradeResult",
    "TradeSimulator",
    "Position",
    "LimitOrder",
    "AnalyticsEngine",
    "PerformanceMetrics",
    "DataEngine",
    "ReportGenerator",
    "run_backtest",
]
