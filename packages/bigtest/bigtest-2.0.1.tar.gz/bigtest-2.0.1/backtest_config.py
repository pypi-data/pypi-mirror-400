"""
Backtest Configuration - Industry-Grade Settings
Comprehensive user inputs for professional backtesting
"""

from dataclasses import dataclass, field
from typing import List, Optional, Literal
from datetime import time


@dataclass
class BacktestConfig:
    """
    Comprehensive backtesting configuration with all user-customizable settings.
    
    Usage:
        config = BacktestConfig(
            symbol='EUR/USD',
            timeframe='1m',
            start_date='2024-01-01',
            end_date='2024-02-01',
            initial_capital=10000,
            leverage=100
        )
    """
    
    # ==================== DATA SETTINGS ====================
    symbol: str                          # e.g., 'EUR/USD', 'BTC/USDT'
    timeframe: str                       # e.g., '1m', '5m', '1h', '1d'
    start_date: str                      # Format: 'YYYY-MM-DD'
    end_date: str                        # Format: 'YYYY-MM-DD'
    data_source: str = 'finda'           # 'finda', 'dukascopy', 'binance'
    
    # ==================== CAPITAL & POSITION ====================
    initial_capital: float = 10000.0     # Starting capital
    currency: str = 'USD'                # Account currency
    leverage: int = 1                    # Leverage multiplier (1 = no leverage)
    lot_size: float = 100000             # Standard lot size (100k for forex)
    max_position_size: float = 1.0       # Maximum position in lots
    max_pyramiding: int = 1              # Max concurrent trades (same direction)
    
    # ==================== RISK MANAGEMENT ====================
    risk_per_trade: float = 0.01         # Risk per trade (0.01 = 1%)
    max_daily_loss: float = 0.05         # Max daily loss (0.05 = 5%)
    max_drawdown: float = 0.20           # Max drawdown stop (0.20 = 20%)
    use_kelly_criterion: bool = False    # Use Kelly for position sizing
    kelly_fraction: float = 0.5          # Fraction of Kelly to use
    
    # ==================== EXECUTION SETTINGS ====================
    slippage_model: Literal['none', 'fixed', 'random', 'volume', 'atr'] = 'fixed'
    slippage_pips: float = 0.3           # Slippage in pips
    slippage_max_pips: float = 1.0       # Max slippage for random/atr model
    commission_per_lot: float = 7.0      # Commission per round-turn lot (legacy)
    commission_rate: float = 0.00007     # Commission on notional value (0.7 bps)
    maker_commission_rate: float = 0.00002  # Maker commission for limit orders (0.2 bps)
    spread_pips: float = 1.0             # Spread in pips (added to entry)
    use_notional_commission: bool = True # Use notional-based commission
    
    # ==================== TP/SL SETTINGS ====================
    use_tick_resolution: bool = True     # Use ticks for ambiguous exits
    assume_worst_case: bool = True       # If no ticks, assume SL hit first
    pip_value: float = 0.0001            # Pip size (0.0001 for forex, 0.01 for JPY)
    
    # ==================== SESSION FILTER ====================
    trade_sessions: Optional[List[str]] = None  # ['london', 'newyork', 'tokyo', 'sydney']
    trade_days: Optional[List[int]] = None      # [0,1,2,3,4] = Mon-Fri
    session_start: Optional[time] = None        # Custom session start
    session_end: Optional[time] = None          # Custom session end
    
    # ==================== BACKTEST OPTIONS ====================
    process_bar_by_bar: bool = True      # Process each bar (vs vectorized)
    check_margin: bool = True            # Check margin requirements
    close_at_end: bool = True            # Close open trades at backtest end
    
    # ==================== MARGIN & LIQUIDATION (100x Leverage) ====================
    stop_out_enabled: bool = True        # Enable forced liquidation on margin breach
    maintenance_margin_pct: float = 0.5  # Maintenance = 50% of initial margin
    margin_call_warning_pct: float = 0.7 # Warn at 70% margin usage
    
    # ==================== REPORTING ====================
    generate_report: bool = True         # Generate HTML report
    save_trades_csv: bool = True         # Save trades to CSV
    plot_equity: bool = True             # Plot equity curve
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        # Validate timeframe
        valid_timeframes = ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w']
        if self.timeframe not in valid_timeframes:
            raise ValueError(f"Invalid timeframe: {self.timeframe}. Must be one of {valid_timeframes}")
        
        # Validate risk settings
        if not 0 < self.risk_per_trade <= 1:
            raise ValueError("risk_per_trade must be between 0 and 1")
        if not 0 < self.max_daily_loss <= 1:
            raise ValueError("max_daily_loss must be between 0 and 1")
        
        # Set pip value for JPY pairs
        if 'JPY' in self.symbol.upper():
            self.pip_value = 0.01
    
    def get_session_hours(self, session: str) -> tuple:
        """Get trading hours for named session (UTC)"""
        sessions = {
            'tokyo':    (time(0, 0), time(9, 0)),
            'london':   (time(7, 0), time(16, 0)),
            'newyork':  (time(12, 0), time(21, 0)),
            'sydney':   (time(21, 0), time(6, 0)),
        }
        return sessions.get(session.lower(), (time(0, 0), time(23, 59)))
    
    def is_trading_allowed(self, dt) -> bool:
        """Check if trading is allowed at given datetime"""
        # Check day filter
        if self.trade_days is not None:
            if dt.weekday() not in self.trade_days:
                return False
        
        # Check session filter
        if self.trade_sessions is not None:
            in_session = False
            for session in self.trade_sessions:
                start, end = self.get_session_hours(session)
                current = dt.time()
                if start <= end:
                    if start <= current <= end:
                        in_session = True
                        break
                else:  # Session spans midnight
                    if current >= start or current <= end:
                        in_session = True
                        break
            return in_session
        
        # Check custom session
        if self.session_start and self.session_end:
            current = dt.time()
            if self.session_start <= self.session_end:
                return self.session_start <= current <= self.session_end
            else:
                return current >= self.session_start or current <= self.session_end
        
        return True


@dataclass
class TradeSignal:
    """Signal generated by a strategy"""
    index: int                           # Bar index
    time: any                            # Signal time
    type: Literal['BUY', 'SELL']         # Direction
    entry_price: Optional[float] = None  # Limit entry (None = market)
    sl: Optional[float] = None           # Stop loss price
    tp: Optional[float] = None           # Take profit price
    size: Optional[float] = None         # Position size
    risk: Optional[float] = None         # Risk fraction for sizing
    comment: str = ''                    # Trade comment
    
    def __post_init__(self):
        if self.type not in ['BUY', 'SELL']:
            raise ValueError(f"Invalid signal type: {self.type}")


@dataclass 
class TradeResult:
    """Completed trade with full details"""
    id: int
    symbol: str
    type: str
    entry_time: any
    entry_price: float
    exit_time: any
    exit_price: float
    size: float
    sl: Optional[float]
    tp: Optional[float]
    pnl: float
    pnl_pct: float
    commission: float
    slippage: float
    duration: any
    exit_reason: str
    comment: str
    
    # Risk metrics
    max_favorable_excursion: float = 0.0   # Best unrealized profit
    max_adverse_excursion: float = 0.0     # Worst unrealized loss
    r_multiple: float = 0.0                 # Profit in R units


if __name__ == "__main__":
    # Example usage
    config = BacktestConfig(
        symbol='EUR/USD',
        timeframe='1m',
        start_date='2024-01-01',
        end_date='2024-02-01',
        initial_capital=10000,
        leverage=100,
        risk_per_trade=0.02,
        slippage_pips=0.5,
        commission_per_lot=7.0,
        trade_sessions=['london', 'newyork']
    )
    print(f"Config: {config.symbol} {config.timeframe}")
    print(f"Capital: ${config.initial_capital} with {config.leverage}:1 leverage")
    print(f"Risk: {config.risk_per_trade*100}% per trade")
