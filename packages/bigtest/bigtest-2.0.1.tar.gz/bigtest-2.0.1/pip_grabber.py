"""
Pip Grabber - High Win Rate Scalping Strategy
EUR/USD 1-minute with 1:100 leverage

Strategy Logic:
- Take Profit: 1-2 pips (very tight)
- Stop Loss: 6-8 pips (3-4x TP)
- Goal: 70-80%+ win rate with many small wins
- Let the law of large numbers work in our favor

The math: If we win 75% of trades with 1.5 pip TP and lose 25% with 6 pip SL:
Expected value = 0.75 * 1.5 - 0.25 * 6 = 1.125 - 1.5 = -0.375 pips/trade (still negative!)

To be profitable we need: Win% * TP > Loss% * SL
With TP=2, SL=6: Need win rate > 75% (6/(6+2) = 75%)

So we target 80%+ win rate with smart entries!
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


class PipGrabber:
    """
    High win-rate scalping strategy.
    Takes tiny profits (1-2 pips) with wider stops (6-8 pips).
    """
    
    def __init__(self, leverage=100, risk_per_trade=0.01):
        self.leverage = leverage
        self.risk_per_trade = risk_per_trade
        self.pip = 0.0001
        
        # Core strategy parameters
        self.tp_pips = 2.0      # Take profit: 2 pips
        self.sl_pips = 8.0      # Stop loss: 8 pips (4:1 ratio)
        self.min_bars_between = 3  # Fast trading
        
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
    
    def _rsi(self, closes, period=5):
        """Very fast RSI for quick momentum"""
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
        """Trade only during active hours"""
        try:
            hour = time.hour
            return 7 <= hour <= 20  # Main trading hours
        except:
            return True
    
    def _calculate_indicators(self, df):
        closes = df['close'].values
        highs = df['high'].values
        lows = df['low'].values
        opens = df['open'].values
        n = len(df)
        
        ind = {}
        
        # Fast EMAs
        ind['ema_3'] = self._ema(closes, 3)
        ind['ema_8'] = self._ema(closes, 8)
        ind['ema_20'] = self._ema(closes, 20)
        
        # Very fast RSI
        ind['rsi_5'] = self._rsi(closes, 5)
        
        # Micro-trend (last 3 bars)
        ind['micro_up'] = np.zeros(n, dtype=bool)
        ind['micro_down'] = np.zeros(n, dtype=bool)
        for i in range(3, n):
            # 2 out of 3 bars going same direction
            ups = sum(1 for j in range(i-2, i+1) if closes[j] > opens[j])
            downs = sum(1 for j in range(i-2, i+1) if closes[j] < opens[j])
            ind['micro_up'][i] = ups >= 2
            ind['micro_down'][i] = downs >= 2
        
        # EMA trend
        ind['trend_up'] = (ind['ema_3'] > ind['ema_8']) & (ind['ema_8'] > ind['ema_20'])
        ind['trend_down'] = (ind['ema_3'] < ind['ema_8']) & (ind['ema_8'] < ind['ema_20'])
        
        # Price above/below fast EMA
        ind['above_ema3'] = closes > ind['ema_3']
        ind['below_ema3'] = closes < ind['ema_3']
        
        # Price crossing EMA8 (potential reversal)
        ind['cross_ema8_up'] = np.zeros(n, dtype=bool)
        ind['cross_ema8_down'] = np.zeros(n, dtype=bool)
        for i in range(1, n):
            if closes[i] > ind['ema_8'][i] and closes[i-1] <= ind['ema_8'][i-1]:
                ind['cross_ema8_up'][i] = True
            if closes[i] < ind['ema_8'][i] and closes[i-1] >= ind['ema_8'][i-1]:
                ind['cross_ema8_down'][i] = True
        
        # Candle direction
        ind['green'] = closes > opens
        ind['red'] = closes < opens
        
        # Strong candle (body > 50% of range)
        body = np.abs(closes - opens)
        range_hl = highs - lows + 1e-10
        ind['strong'] = body > 0.4 * range_hl
        
        # RSI momentum zones
        ind['rsi_bullish'] = ind['rsi_5'] > 50
        ind['rsi_bearish'] = ind['rsi_5'] < 50
        ind['rsi_strong_bull'] = ind['rsi_5'] > 60
        ind['rsi_strong_bear'] = ind['rsi_5'] < 40
        
        # Doji/indecision (avoid)
        ind['doji'] = body < 0.2 * range_hl
        
        return ind
    
    def generate_signals(self, df, symbol="EUR/USD"):
        print(f"[PipGrabber] Generating signals for {symbol}...")
        print(f"[PipGrabber] TP: {self.tp_pips} pips, SL: {self.sl_pips} pips")
        print(f"[PipGrabber] Data: {len(df)} bars")
        
        n = len(df)
        if n < 30:
            return []
        
        ind = self._calculate_indicators(df)
        
        signals = []
        last_signal_bar = -100
        daily_trades = {}
        
        closes = df['close'].values
        
        for i in range(25, n):
            time = df.iloc[i]['time']
            
            # Trading hours
            if not self._is_trading_hour(time):
                continue
            
            # Cooldown
            if i - last_signal_bar < self.min_bars_between:
                continue
            
            # Daily limit (20/day max)
            try:
                trade_date = time.date()
                if trade_date not in daily_trades:
                    daily_trades[trade_date] = 0
                if daily_trades[trade_date] >= 20:
                    continue
            except:
                trade_date = None
            
            # Skip indecision candles
            if ind['doji'][i]:
                continue
            
            close_price = closes[i]
            
            # Fixed pip-based SL/TP
            tp_distance = self.tp_pips * self.pip
            sl_distance = self.sl_pips * self.pip
            
            signal_type = None
            reason = ""
            
            # ========== HIGH PROBABILITY BUY SIGNALS ==========
            
            # 1. Strong trend continuation (highest probability)
            if (ind['trend_up'][i] and
                ind['green'][i] and
                ind['strong'][i] and
                ind['micro_up'][i] and
                ind['rsi_bullish'][i]):
                signal_type = 'BUY'
                reason = 'Trend'
            
            # 2. EMA8 bounce in uptrend
            elif (ind['cross_ema8_up'][i] and
                  ind['ema_8'][i] > ind['ema_20'][i] and
                  ind['green'][i] and
                  ind['rsi_5'][i] > 45):
                signal_type = 'BUY'
                reason = 'Bounce'
            
            # 3. Strong RSI momentum
            elif (ind['rsi_strong_bull'][i] and
                  ind['green'][i] and
                  ind['strong'][i] and
                  ind['above_ema3'][i] and
                  ind['ema_3'][i] > ind['ema_8'][i]):
                signal_type = 'BUY'
                reason = 'RSIMom'
            
            # ========== HIGH PROBABILITY SELL SIGNALS ==========
            
            # 1. Strong trend continuation
            elif (ind['trend_down'][i] and
                  ind['red'][i] and
                  ind['strong'][i] and
                  ind['micro_down'][i] and
                  ind['rsi_bearish'][i]):
                signal_type = 'SELL'
                reason = 'Trend'
            
            # 2. EMA8 rejection in downtrend
            elif (ind['cross_ema8_down'][i] and
                  ind['ema_8'][i] < ind['ema_20'][i] and
                  ind['red'][i] and
                  ind['rsi_5'][i] < 55):
                signal_type = 'SELL'
                reason = 'Reject'
            
            # 3. Strong RSI momentum down
            elif (ind['rsi_strong_bear'][i] and
                  ind['red'][i] and
                  ind['strong'][i] and
                  ind['below_ema3'][i] and
                  ind['ema_3'][i] < ind['ema_8'][i]):
                signal_type = 'SELL'
                reason = 'RSIMom'
            
            if signal_type:
                if signal_type == 'BUY':
                    signals.append({
                        'index': i,
                        'time': time,
                        'type': 'BUY',
                        'sl': close_price - sl_distance,
                        'tp': close_price + tp_distance,
                        'risk': self.risk_per_trade,
                        'comment': f'Grab {reason}'
                    })
                else:
                    signals.append({
                        'index': i,
                        'time': time,
                        'type': 'SELL',
                        'sl': close_price + sl_distance,
                        'tp': close_price - tp_distance,
                        'risk': self.risk_per_trade,
                        'comment': f'Grab {reason}'
                    })
                
                last_signal_bar = i
                if trade_date:
                    daily_trades[trade_date] += 1
        
        print(f"[PipGrabber] Generated {len(signals)} signals")
        if daily_trades:
            avg_daily = len(signals) / len(daily_trades)
            print(f"[PipGrabber] Avg trades/day: {avg_daily:.1f}")
        
        return signals


def pip_grabber_strategy(df, symbol="EUR/USD"):
    strategy = PipGrabber(leverage=100, risk_per_trade=0.01)
    return strategy.generate_signals(df, symbol)


if __name__ == "__main__":
    print("Pip Grabber - High Win Rate Scalper")
    print("TP: 2 pips, SL: 8 pips")
    print("Target: 75%+ win rate")
