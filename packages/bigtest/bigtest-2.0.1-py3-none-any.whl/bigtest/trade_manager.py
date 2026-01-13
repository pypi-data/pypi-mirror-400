import pandas as pd

class Trade:
    def __init__(self, id, symbol, type, entry_price, entry_time, size, sl, tp, capital_before, comment=""):
        self.id = id
        self.symbol = symbol
        self.type = type # 'BUY' or 'SELL'
        self.entry_price = entry_price
        self.entry_time = entry_time
        self.size = size
        self.sl = sl
        self.tp = tp
        self.comment = comment
        
        # New Professional Fields
        self.capital_before = capital_before
        self.capital_after = None
        self.exit_price = None
        self.exit_time = None
        self.pnl = 0.0
        self.pnl_pct = 0.0
        self.slippage = 0.0
        self.commission = 0.0
        self.status = 'OPEN'
        self.duration = None
        self.overlapping_trades = 0 # Count of other trades open at entry

    def close(self, price, time, slippage=0.0, commission=0.0):
        self.exit_price = price
        self.exit_time = time
        self.slippage = slippage
        self.commission = commission
        self.status = 'CLOSED'
        self.duration = self.exit_time - self.entry_time
        
        if self.type == 'BUY':
            self.pnl = (self.exit_price - self.entry_price) * self.size
            self.pnl_pct = (self.exit_price - self.entry_price) / self.entry_price
        else:
            self.pnl = (self.entry_price - self.exit_price) * self.size
            self.pnl_pct = (self.entry_price - self.exit_price) / self.entry_price
            
        # Adjust PnL for commission
        self.pnl -= self.commission
        
        self.capital_after = self.capital_before + self.pnl
        return self.pnl

    def to_dict(self):
        return {
            'ID': self.id,
            'Symbol': self.symbol,
            'Type': self.type,
            'Entry Time': self.entry_time,
            'Entry Price': self.entry_price,
            'Exit Time': self.exit_time,
            'Exit Price': self.exit_price,
            'Size': self.size,
            'PnL': self.pnl,
            'PnL %': self.pnl_pct * 100,
            'Capital Before': self.capital_before,
            'Capital After': self.capital_after,
            'Slippage': self.slippage,
            'Commission': self.commission,
            'Duration': str(self.duration),
            'Overlapping': self.overlapping_trades,
            'Comment': self.comment
        }

class TradeManager:
    def __init__(self, initial_capital=10000, max_pyramiding=1, commission_rate=0.0):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.max_pyramiding = max_pyramiding
        self.commission_rate = commission_rate # e.g. 0.001 for 0.1%
        
        self.trades = []
        self.trade_counter = 0
        
        # Time-series tracking
        self.equity_curve = [{'time': None, 'equity': initial_capital}] # Will update with first timestamp
        self.drawdown_curve = []

    def can_open_trade(self, symbol, type):
        active_trades = [t for t in self.trades if t.symbol == symbol and t.status == 'OPEN' and t.type == type]
        return len(active_trades) < self.max_pyramiding

    def calculate_position_size(self, price, risk_pct, sl):
        """
        Calculates position size based on risk percentage of current capital.
        risk_pct: e.g., 0.01 for 1% risk
        """
        if not sl:
            return 0.0
            
        risk_amount = self.current_capital * risk_pct
        price_diff = abs(price - sl)
        
        if price_diff == 0:
            return 0.0
            
        size = risk_amount / price_diff
        return size

    def open_trade(self, symbol, type, price, time, size, sl, tp, comment=""):
        if not self.can_open_trade(symbol, type):
            return None
            
        self.trade_counter += 1
        
        # Count overlapping trades (currently open)
        overlapping = len(self.get_active_trades())
        
        # Apply Entry Commission
        commission_cost = (price * size) * self.commission_rate
        self.current_capital -= commission_cost
        
        trade = Trade(
            id=self.trade_counter,
            symbol=symbol,
            type=type,
            entry_price=price,
            entry_time=time,
            size=size,
            sl=sl,
            tp=tp,
            capital_before=self.current_capital, # Capital after entry commission
            comment=comment
        )
        trade.commission += commission_cost # Track total commission
        trade.overlapping_trades = overlapping
        self.trades.append(trade)
        return trade

    def close_trade(self, trade, price, time, comment="", slippage=0.0):
        if trade in self.trades and trade.status == 'OPEN':
            # Calculate Exit Commission
            exit_commission = (price * trade.size) * self.commission_rate
            total_commission = trade.commission + exit_commission
            
            pnl = trade.close(price, time, slippage=slippage, commission=total_commission)
            if comment:
                trade.comment += f" [{comment}]"
            
            self.current_capital += pnl # PnL already includes commission deduction in Trade.close()
            return trade
        return None

    def update_equity(self, time, current_close_prices):
        """
        Updates the equity curve based on realized PnL + Unrealized PnL of open positions.
        current_close_prices: dict {symbol: price}
        """
        unrealized_pnl = 0.0
        for trade in self.get_active_trades():
            if trade.symbol in current_close_prices:
                curr_price = current_close_prices[trade.symbol]
                if trade.type == 'BUY':
                    unrealized_pnl += (curr_price - trade.entry_price) * trade.size
                else:
                    unrealized_pnl += (trade.entry_price - curr_price) * trade.size
        
        total_equity = self.current_capital + unrealized_pnl
        
        # Update Equity Curve
        self.equity_curve.append({'time': time, 'equity': total_equity})
        
        # Calculate Drawdown
        peak = max(d['equity'] for d in self.equity_curve)
        dd = (peak - total_equity) / peak if peak > 0 else 0
        self.drawdown_curve.append({'time': time, 'drawdown': dd * 100})

    def get_active_trades(self, symbol=None):
        if symbol:
            return [t for t in self.trades if t.status == 'OPEN' and t.symbol == symbol]
        return [t for t in self.trades if t.status == 'OPEN']

    def get_closed_trades(self):
        return [t for t in self.trades if t.status == 'CLOSED']

    def get_total_pnl(self):
        return sum(t.pnl for t in self.trades if t.status == 'CLOSED')
        
    def get_trades_df(self):
        return pd.DataFrame([t.to_dict() for t in self.trades])
