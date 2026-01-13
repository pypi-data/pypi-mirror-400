"""
Mean Reversion Scalper for EUR/USD
1-minute timeframe

KEY INSIGHT: After consecutive strong moves, price often retraces.
Instead of chasing momentum, we FADE the extreme moves.

Strategy:
- After 3+ pips move in one direction, bet on retracement
- TP: 1-2 pips (just grab the bounce)
- SL: 3-4 pips (tight but not too tight)
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


class MeanReversionScalper:
    def __init__(self, leverage=100):
        self.leverage = leverage
        self.pip = 0.0001
        self.tp_pips = 1.5   # Small TP
        self.sl_pips = 4.0   # Moderate SL
        self.min_bars_between = 2
        
    def _ema(self, data, period):
        n = len(data)
        ema = np.zeros(n)
        if n < period:
            return ema
        multiplier = 2 / (period + 1)
        ema[period-1] = np.mean(data[:period])
        for i in range(period, n):
            ema[i] = (data[i] - ema[i-1]) * multiplier + ema[i-1]
        return ema
    
    def _rsi(self, closes, period=7):
        n = len(closes)
        rsi = np.full(n, 50.0)
        if n < period + 1:
            return rsi
        deltas = np.diff(closes, prepend=closes[0])
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        avg_gain = np.mean(gains[1:period+1])
        avg_loss = np.mean(losses[1:period+1])
        for i in range(period + 1, n):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
            rs = avg_gain / (avg_loss + 1e-10)
            rsi[i] = 100 - (100 / (1 + rs))
        return rsi
    
    def _is_trading_hour(self, time):
        try:
            return 8 <= time.hour <= 18
        except:
            return True
    
    def generate_signals(self, df, symbol="EUR/USD"):
        print(f"[MeanRev] Generating signals for {symbol}...")
        print(f"[MeanRev] TP: {self.tp_pips} pips, SL: {self.sl_pips} pips")
        
        n = len(df)
        if n < 20:
            return []
        
        closes = df['close'].values
        opens = df['open'].values
        highs = df['high'].values
        lows = df['low'].values
        
        ema_10 = self._ema(closes, 10)
        rsi = self._rsi(closes, 7)
        
        signals = []
        last_signal_bar = -100
        daily_trades = {}
        
        for i in range(10, n):
            time = df.iloc[i]['time']
            
            if not self._is_trading_hour(time):
                continue
            
            if i - last_signal_bar < self.min_bars_between:
                continue
            
            try:
                trade_date = time.date()
                if trade_date not in daily_trades:
                    daily_trades[trade_date] = 0
                if daily_trades[trade_date] >= 20:
                    continue
            except:
                trade_date = None
            
            close = closes[i]
            
            # Calculate recent move (last 3 bars)
            move_3bar = close - closes[i-3] if i >= 3 else 0
            move_pips = move_3bar / self.pip
            
            # Distance from EMA
            dist_from_ema = (close - ema_10[i]) / self.pip
            
            signal_type = None
            
            # ===== MEAN REVERSION: FADE THE MOVE =====
            
            # After strong UP move (3+ pips up), bet on pullback (SELL)
            if (move_pips >= 3.0 and
                rsi[i] > 70 and  # Overbought
                dist_from_ema > 1.5):  # Extended from EMA
                signal_type = 'SELL'
            
            # After strong DOWN move (3+ pips down), bet on bounce (BUY)
            elif (move_pips <= -3.0 and
                  rsi[i] < 30 and  # Oversold
                  dist_from_ema < -1.5):  # Extended from EMA
                signal_type = 'BUY'
            
            if signal_type:
                tp_dist = self.tp_pips * self.pip
                sl_dist = self.sl_pips * self.pip
                
                if signal_type == 'BUY':
                    signals.append({
                        'index': i,
                        'time': time,
                        'type': 'BUY',
                        'sl': close - sl_dist,
                        'tp': close + tp_dist,
                        'risk': 0.01,
                        'comment': f'MR Bounce'
                    })
                else:
                    signals.append({
                        'index': i,
                        'time': time,
                        'type': 'SELL',
                        'sl': close + sl_dist,
                        'tp': close - tp_dist,
                        'risk': 0.01,
                        'comment': f'MR Fade'
                    })
                
                last_signal_bar = i
                if trade_date:
                    daily_trades[trade_date] += 1
        
        print(f"[MeanRev] Generated {len(signals)} signals")
        return signals


def mean_reversion_strategy(df, symbol="EUR/USD"):
    strategy = MeanReversionScalper(leverage=100)
    return strategy.generate_signals(df, symbol)


if __name__ == "__main__":
    print("Mean Reversion Scalper")
