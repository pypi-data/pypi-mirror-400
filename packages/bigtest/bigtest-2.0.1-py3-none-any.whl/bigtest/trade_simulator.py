"""
Trade Simulator - Core Backtesting Logic
Correct TP/SL detection with optimized tick fetching
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple, Any
from datetime import datetime, timedelta
import numpy as np
import pandas as pd


@dataclass
class Position:
    """Represents an open position with full tracking."""
    id: int
    symbol: str
    type: str  # 'BUY' or 'SELL'
    entry_price: float
    entry_time: Any
    size: float
    sl: Optional[float]
    tp: Optional[float]
    comment: str = ''
    
    # MFE/MAE Tracking
    max_price: float = 0.0  # Highest price seen (for trailing)
    min_price: float = 0.0  # Lowest price seen
    mfe: float = 0.0  # Maximum Favorable Excursion (pips)
    mae: float = 0.0  # Maximum Adverse Excursion (pips)
    
    # Context
    overlapping_trades: int = 0  # Count of other trades open at entry
    capital_before: float = 0.0
    
    # Margin
    initial_margin: float = 0.0
    unrealized_pnl: float = 0.0


@dataclass
class LimitOrder:
    """Pending limit order awaiting fill."""
    id: int
    symbol: str
    type: str  # 'BUY_LIMIT' or 'SELL_LIMIT'
    limit_price: float
    size: float
    sl: Optional[float]
    tp: Optional[float]
    created_time: Any
    expiry_bars: int = 100  # Expire after N bars
    bars_active: int = 0
    comment: str = ''


class TradeSimulator:
    """
    Core trade simulation engine with correct TP/SL detection.
    
    Key Features:
    - Correct TP/SL hit detection based on trade direction
    - Optimized tick fetching (only when needed)
    - Slippage and commission modeling
    - Position tracking with MFE/MAE
    """
    
    def __init__(self, config):
        """
        Initialize simulator with config.
        
        Args:
            config: BacktestConfig instance
        """
        self.config = config
        self.pip = config.pip_value
        
        # State
        self.positions: List[Position] = []
        self.pending_orders: List[LimitOrder] = []  # Pending limit orders
        self.closed_trades: List[Dict] = []
        self.trade_counter = 0
        self.order_counter = 0
        
        # Capital tracking
        self.initial_capital = config.initial_capital
        self.current_capital = config.initial_capital
        self.peak_capital = config.initial_capital
        self.daily_pnl = 0.0
        self.current_date = None
        
        # ATR for variable slippage
        self.current_atr: float = 0.0
        
        # Statistics
        self.total_commission = 0.0
        self.total_slippage = 0.0
        self.liquidation_count = 0
    
    def reset(self):
        """Reset simulator state for new backtest"""
        self.positions = []
        self.pending_orders = []
        self.closed_trades = []
        self.trade_counter = 0
        self.order_counter = 0
        self.current_capital = self.initial_capital
        self.peak_capital = self.initial_capital
        self.daily_pnl = 0.0
        self.current_date = None
        self.current_atr = 0.0
        self.total_commission = 0.0
        self.total_slippage = 0.0
        self.liquidation_count = 0
    
    # ==================== POSITION MANAGEMENT ====================
    
    def can_open_position(self, direction: str) -> bool:
        """Check if new position can be opened"""
        # Check pyramiding limit
        same_dir_positions = [p for p in self.positions if p.type == direction]
        if len(same_dir_positions) >= self.config.max_pyramiding:
            return False
        
        # Check daily loss limit
        if self.daily_pnl <= -self.config.max_daily_loss * self.initial_capital:
            return False
        
        # Check drawdown limit
        drawdown = (self.peak_capital - self.current_capital) / self.peak_capital
        if drawdown >= self.config.max_drawdown:
            return False
        
        return True
    
    def calculate_position_size(self, entry_price: float, sl: Optional[float], risk_fraction: Optional[float] = None) -> float:
        """
        Calculate position size based on risk.
        
        Args:
            entry_price: Entry price
            sl: Stop loss price
            risk_fraction: Fraction of capital to risk (overrides config)
        
        Returns:
            Position size in lots
        """
        risk = risk_fraction or self.config.risk_per_trade
        risk_amount = self.current_capital * risk
        
        if sl is None:
            # Fixed position size
            return min(0.1, self.config.max_position_size)
        
        # Calculate stop distance
        stop_distance = abs(entry_price - sl)
        if stop_distance == 0:
            return 0.01
        
        # Position size = Risk Amount / (Stop Distance * Pip Value * Lot Size)
        pip_distance = stop_distance / self.pip
        pip_value_per_lot = self.config.lot_size * self.pip
        
        size = risk_amount / (pip_distance * pip_value_per_lot)
        
        # Apply leverage
        max_size = (self.current_capital * self.config.leverage) / (entry_price * self.config.lot_size)
        
        # Clamp to limits
        size = min(size, max_size, self.config.max_position_size)
        size = max(size, 0.01)  # Minimum 0.01 lots
        
        return round(size, 2)
    
    def open_position(self, signal, candle) -> Optional[Position]:
        """
        Open a new position from signal.
        
        Args:
            signal: TradeSignal
            candle: Current candle data
        
        Returns:
            Position if opened, None if rejected
        """
        if not self.can_open_position(signal.type):
            return None
        
        # Calculate entry price with slippage and spread
        # Use raw Bid/Ask if available from tick data
        bid = candle.get('bid', candle['close'] - self.config.spread_pips * self.pip / 2)
        ask = candle.get('ask', candle['close'] + self.config.spread_pips * self.pip / 2)
        
        slippage = self._calculate_slippage(candle)
        
        if signal.type == 'BUY':
            entry_price = signal.entry_price or ask  # Pay the Ask for longs
            entry_price += slippage
        else:
            entry_price = signal.entry_price or bid  # Receive the Bid for shorts
            entry_price -= slippage
        
        # Calculate size
        size = signal.size
        if size is None:
            size = self.calculate_position_size(entry_price, signal.sl, signal.risk)
        
        # Calculate commission (notional-based or per-lot)
        if self.config.use_notional_commission:
            notional_value = entry_price * size * self.config.lot_size
            commission = notional_value * self.config.commission_rate
        else:
            commission = size * self.config.commission_per_lot
        
        self.current_capital -= commission
        self.total_commission += commission
        self.total_slippage += slippage * size * self.config.lot_size
        
        # Calculate initial margin
        notional = entry_price * size * self.config.lot_size
        initial_margin = notional / self.config.leverage
        
        # Create position with enhanced fields
        self.trade_counter += 1
        position = Position(
            id=self.trade_counter,
            symbol=self.config.symbol,
            type=signal.type,
            entry_price=entry_price,
            entry_time=candle['time'],
            size=size,
            sl=signal.sl,
            tp=signal.tp,
            comment=signal.comment,
            max_price=entry_price,
            min_price=entry_price,
            overlapping_trades=len(self.positions),  # Count current open positions
            capital_before=self.current_capital,
            initial_margin=initial_margin
        )
        
        self.positions.append(position)
        return position
    
    def close_position(self, position: Position, exit_price: float, exit_time: Any, reason: str):
        """
        Close a position and record the trade.
        
        Args:
            position: Position to close
            exit_price: Exit price
            exit_time: Exit time
            reason: Exit reason (TP/SL/Signal/End)
        """
        if position not in self.positions:
            return
        
        # Calculate PnL
        if position.type == 'BUY':
            pnl_pips = (exit_price - position.entry_price) / self.pip
        else:
            pnl_pips = (position.entry_price - exit_price) / self.pip
        
        pip_value = self.config.lot_size * self.pip
        pnl = pnl_pips * pip_value * position.size
        pnl_pct = pnl / self.initial_capital
        
        # Calculate R-Multiple
        r_multiple = 0.0
        if position.sl:
            risk_pips = abs(position.entry_price - position.sl) / self.pip
            if risk_pips > 0:
                r_multiple = pnl_pips / risk_pips
        
        # Calculate MFE/MAE
        if position.type == 'BUY':
            mfe = (position.max_price - position.entry_price) / self.pip
            mae = (position.entry_price - position.min_price) / self.pip
        else:
            mfe = (position.entry_price - position.min_price) / self.pip
            mae = (position.max_price - position.entry_price) / self.pip
        
        # Record trade
        trade = {
            'id': position.id,
            'symbol': position.symbol,
            'type': position.type,
            'entry_time': position.entry_time,
            'entry_price': position.entry_price,
            'exit_time': exit_time,
            'exit_price': exit_price,
            'size': position.size,
            'sl': position.sl,
            'tp': position.tp,
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'pnl_pips': pnl_pips,
            'duration': exit_time - position.entry_time if hasattr(exit_time, '__sub__') else None,
            'exit_reason': reason,
            'comment': position.comment,
            'mfe': mfe,
            'mae': mae,
            'r_multiple': r_multiple
        }
        
        self.closed_trades.append(trade)
        self.positions.remove(position)
        
        # Update capital
        self.current_capital += pnl
        self.daily_pnl += pnl
        self.peak_capital = max(self.peak_capital, self.current_capital)
    
    # ==================== TP/SL DETECTION ====================
    
    def check_exit(self, position: Position, candle: Dict) -> Tuple[Optional[str], Optional[float]]:
        """
        Check if position should exit on this candle.
        
        CORRECT LOGIC:
        - BUY: TP hit when HIGH >= TP, SL hit when LOW <= SL
        - SELL: TP hit when LOW <= TP, SL hit when HIGH >= SL
        
        Args:
            position: Open position
            candle: Current candle OHLC
        
        Returns:
            (exit_reason, exit_price) or (None, None)
        """
        high = candle['high']
        low = candle['low']
        
        tp_hit = False
        sl_hit = False
        
        if position.type == 'BUY':
            # BUY: TP is above entry, SL is below entry
            if position.tp and high >= position.tp:
                tp_hit = True
            if position.sl and low <= position.sl:
                sl_hit = True
        else:  # SELL
            # SELL: TP is below entry, SL is above entry
            if position.tp and low <= position.tp:
                tp_hit = True
            if position.sl and high >= position.sl:
                sl_hit = True
        
        # Update max/min for MFE/MAE
        position.max_price = max(position.max_price, high)
        position.min_price = min(position.min_price, low)
        
        # Determine exit
        if tp_hit and sl_hit:
            # AMBIGUOUS - both could have been hit
            # Option 1: Use tick data (if available)
            # Option 2: Assume worst case (SL first)
            if self.config.assume_worst_case:
                return 'SL', position.sl
            else:
                return 'TP', position.tp
        elif tp_hit:
            return 'TP', position.tp
        elif sl_hit:
            return 'SL', position.sl
        
        return None, None
    
    def is_tick_fetch_needed(self, position: Position, candle: Dict) -> bool:
        """
        Check if tick data is needed for accurate exit resolution.
        Only needed when BOTH TP and SL are within candle range.
        
        Args:
            position: Open position
            candle: Current candle
        
        Returns:
            True if ticks needed
        """
        if not self.config.use_tick_resolution:
            return False
        
        high = candle['high']
        low = candle['low']
        
        if position.type == 'BUY':
            tp_in_range = position.tp and low <= position.tp <= high
            sl_in_range = position.sl and low <= position.sl <= high
        else:
            tp_in_range = position.tp and low <= position.tp <= high
            sl_in_range = position.sl and low <= position.sl <= high
        
        return tp_in_range and sl_in_range
    
    def resolve_with_ticks(self, position: Position, ticks: pd.DataFrame) -> Tuple[Optional[str], Optional[float]]:
        """
        Resolve ambiguous exit using tick data.
        
        Args:
            position: Open position
            ticks: Tick data for the candle
        
        Returns:
            (exit_reason, exit_price)
        """
        if ticks.empty:
            # Fall back to worst case
            return 'SL', position.sl
        
        for _, tick in ticks.iterrows():
            price = tick['price'] if 'price' in tick else tick.get('close', tick.get('bid'))
            
            if position.type == 'BUY':
                if position.sl and price <= position.sl:
                    return 'SL', position.sl
                if position.tp and price >= position.tp:
                    return 'TP', position.tp
            else:
                if position.sl and price >= position.sl:
                    return 'SL', position.sl
                if position.tp and price <= position.tp:
                    return 'TP', position.tp
        
        return None, None
    
    # ==================== HELPERS ====================
    
    def _calculate_slippage(self, candle: Dict) -> float:
        """Calculate slippage based on model"""
        if self.config.slippage_model == 'none':
            return 0.0
        elif self.config.slippage_model == 'fixed':
            return self.config.slippage_pips * self.pip
        elif self.config.slippage_model == 'random':
            return np.random.uniform(0, self.config.slippage_max_pips) * self.pip
        elif self.config.slippage_model == 'volume':
            # Higher volume = lower slippage
            vol = candle.get('volume', 1000)
            factor = min(1.0, 1000 / (vol + 1))
            return self.config.slippage_pips * self.pip * factor
        elif self.config.slippage_model == 'atr':
            # ATR-based variable slippage
            return self._calculate_atr_slippage(candle)
        return 0.0
    
    def _calculate_atr_slippage(self, candle: Dict) -> float:
        """
        Slippage scales with volatility (ATR).
        High ATR = more slippage due to fast market.
        """
        base_slippage = self.config.slippage_pips * self.pip
        if self.current_atr <= 0:
            return base_slippage
        
        atr_factor = self.current_atr / (self.pip * 10)  # Normalize ATR
        variable_slippage = base_slippage * (1 + atr_factor)
        return min(variable_slippage, self.config.slippage_max_pips * self.pip)
    
    def set_current_atr(self, atr: float):
        """Set current ATR for variable slippage calculation."""
        self.current_atr = atr
    
    def update_daily_tracking(self, current_time):
        """Reset daily tracking if new day"""
        if hasattr(current_time, 'date'):
            today = current_time.date()
            if self.current_date != today:
                self.current_date = today
                self.daily_pnl = 0.0
    
    def get_unrealized_pnl(self, current_price: float) -> float:
        """Calculate total unrealized PnL"""
        total = 0.0
        for pos in self.positions:
            if pos.type == 'BUY':
                pnl = (current_price - pos.entry_price) * pos.size * self.config.lot_size
            else:
                pnl = (pos.entry_price - current_price) * pos.size * self.config.lot_size
            total += pnl
        return total
    
    def get_equity(self, current_price: float) -> float:
        """Get current equity (capital + unrealized)"""
        return self.current_capital + self.get_unrealized_pnl(current_price)
    
    # ==================== MARGIN & LIQUIDATION ENGINE ====================
    
    def calculate_margin_used(self) -> float:
        """Calculate total margin in use by open positions."""
        total_margin = 0.0
        for pos in self.positions:
            notional = pos.entry_price * pos.size * self.config.lot_size
            margin = notional / self.config.leverage
            total_margin += margin
        return total_margin
    
    def calculate_free_margin(self, current_price: float) -> float:
        """Calculate available margin for new trades."""
        equity = self.get_equity(current_price)
        used = self.calculate_margin_used()
        return equity - used
    
    def get_margin_level(self, current_price: float) -> float:
        """Calculate margin level as percentage (Equity / Used Margin * 100)."""
        used = self.calculate_margin_used()
        if used <= 0:
            return float('inf')
        return (self.get_equity(current_price) / used) * 100
    
    def check_liquidation(self, candle: Dict) -> List[Tuple[Position, float]]:
        """
        Check if any position should be liquidated due to margin breach.
        Maintenance Margin = maintenance_margin_pct of Initial Margin (default 50%)
        
        Returns:
            List of (position, liquidation_price) tuples
        """
        liquidated = []
        equity = self.get_equity(candle['close'])
        
        for pos in self.positions:
            notional = pos.entry_price * pos.size * self.config.lot_size
            initial_margin = notional / self.config.leverage
            maintenance_margin = initial_margin * self.config.maintenance_margin_pct
            
            # Check if equity < maintenance margin (STOP-OUT)
            if equity < maintenance_margin:
                # Force liquidation at the WORST price for this candle
                if pos.type == 'BUY':
                    liquidation_price = candle['low']  # Worst for longs
                else:
                    liquidation_price = candle['high']  # Worst for shorts
                
                liquidated.append((pos, liquidation_price))
                self.liquidation_count += 1
        
        return liquidated
    
    # ==================== LIMIT ORDER PROCESSING ====================
    
    def add_limit_order(self, order_type: str, limit_price: float, size: float,
                        sl: Optional[float], tp: Optional[float],
                        created_time: Any, expiry_bars: int = 100,
                        comment: str = '') -> LimitOrder:
        """
        Add a pending limit order.
        
        Args:
            order_type: 'BUY_LIMIT' or 'SELL_LIMIT'
            limit_price: Price at which order should fill
            size: Position size
            sl: Stop loss for resulting position
            tp: Take profit for resulting position
            created_time: Order creation time
            expiry_bars: Bars until order expires
            comment: Order comment
        """
        self.order_counter += 1
        order = LimitOrder(
            id=self.order_counter,
            symbol=self.config.symbol,
            type=order_type,
            limit_price=limit_price,
            size=size,
            sl=sl,
            tp=tp,
            created_time=created_time,
            expiry_bars=expiry_bars,
            comment=comment
        )
        self.pending_orders.append(order)
        return order
    
    def check_limit_order_fill(self, order: LimitOrder, candle: Dict) -> Optional[Position]:
        """
        Check if limit order should fill.
        BUY_LIMIT fills when Ask <= limit_price
        SELL_LIMIT fills when Bid >= limit_price
        No slippage applied to limit orders (maker).
        
        Returns:
            Position if filled, 'EXPIRED' if expired, None if still pending
        """
        ask = candle.get('ask', candle['high'])
        bid = candle.get('bid', candle['low'])
        
        fill = False
        direction = 'BUY' if 'BUY' in order.type else 'SELL'
        
        if order.type == 'BUY_LIMIT' and ask <= order.limit_price:
            fill = True
        elif order.type == 'SELL_LIMIT' and bid >= order.limit_price:
            fill = True
        
        if fill:
            # Fill at limit price with maker commission
            return self._fill_limit_order(order, order.limit_price, candle, direction)
        
        order.bars_active += 1
        if order.bars_active >= order.expiry_bars:
            self.pending_orders.remove(order)
            return 'EXPIRED'
        
        return None
    
    def _fill_limit_order(self, order: LimitOrder, fill_price: float, 
                          candle: Dict, direction: str) -> Position:
        """
        Fill a limit order at specified price with maker commission.
        """
        # Remove from pending
        if order in self.pending_orders:
            self.pending_orders.remove(order)
        
        # Calculate maker commission (lower than taker)
        notional_value = fill_price * order.size * self.config.lot_size
        commission = notional_value * self.config.maker_commission_rate
        
        self.current_capital -= commission
        self.total_commission += commission
        
        # Calculate initial margin
        initial_margin = notional_value / self.config.leverage
        
        # Create position
        self.trade_counter += 1
        position = Position(
            id=self.trade_counter,
            symbol=self.config.symbol,
            type=direction,
            entry_price=fill_price,
            entry_time=candle['time'],
            size=order.size,
            sl=order.sl,
            tp=order.tp,
            comment=f"[LIMIT] {order.comment}",
            max_price=fill_price,
            min_price=fill_price,
            overlapping_trades=len(self.positions),
            capital_before=self.current_capital,
            initial_margin=initial_margin
        )
        
        self.positions.append(position)
        return position
    
    def process_pending_orders(self, candle: Dict) -> List[Position]:
        """
        Process all pending limit orders for the current candle.
        
        Returns:
            List of positions created from filled orders
        """
        filled_positions = []
        
        for order in list(self.pending_orders):
            result = self.check_limit_order_fill(order, candle)
            if isinstance(result, Position):
                filled_positions.append(result)
            # 'EXPIRED' case is handled inside check_limit_order_fill
        
        return filled_positions


if __name__ == "__main__":
    print("Trade Simulator - Core backtesting logic")
    print("Use with BacktestEngine for full simulation")
