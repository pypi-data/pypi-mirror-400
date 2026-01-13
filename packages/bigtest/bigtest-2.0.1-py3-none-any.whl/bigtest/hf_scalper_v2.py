"""
High-Frequency Scalping Strategy v2 for EUR/USD
1-minute timeframe with 1:100 leverage

IMPROVED VERSION:
- Wider ATR-based stops (1.5x ATR)
- Simpler, more reliable entries
- Better momentum confirmation
- Session-aware trading
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


class HFScalperV2:
    """
    Improved high-frequency scalper with better entries and wider stops.
    """
    
    def __init__(self, leverage=100, risk_per_trade=0.015):
        self.leverage = leverage
        self.risk_per_trade = risk_per_trade
        self.pip_value = 0.0001
        self.min_bars_between = 10  # More spacing between trades
        
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
    
    def _rsi(self, closes, period=14):
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
    
    def _atr(self, highs, lows, closes, period=14):
        n = len(closes)
        tr = np.zeros(n)
        tr[0] = highs[0] - lows[0]
        for i in range(1, n):
            tr[i] = max(highs[i] - lows[i], 
                       abs(highs[i] - closes[i-1]), 
                       abs(lows[i] - closes[i-1]))
        
        atr = np.zeros(n)
        if n >= period:
            atr[period-1] = np.mean(tr[:period])
            for i in range(period, n):
                atr[i] = (atr[i-1] * (period - 1) + tr[i]) / period
        return atr
    
    def _is_good_session(self, time):
        """Best trading hours for EUR/USD"""
        try:
            hour = time.hour
            # London 7-16, NY 13-21, overlap 13-16 is best
            return 8 <= hour <= 19
        except:
            return True
    
    def _calculate_indicators(self, df):
        closes = df['close'].values
        highs = df['high'].values
        lows = df['low'].values
        opens = df['open'].values
        n = len(df)
        
        ind = {}
        
        # Core EMAs
        ind['ema_8'] = self._ema(closes, 8)
        ind['ema_21'] = self._ema(closes, 21)
        ind['ema_50'] = self._ema(closes, 50)
        
        # RSI
        ind['rsi'] = self._rsi(closes, 14)
        
        # ATR
        ind['atr'] = self._atr(highs, lows, closes, 14)
        
        # Price position
        ind['above_ema21'] = closes > ind['ema_21']
        ind['above_ema50'] = closes > ind['ema_50']
        
        # Trend alignment
        ind['uptrend'] = (ind['ema_8'] > ind['ema_21']) & (ind['ema_21'] > ind['ema_50'])
        ind['downtrend'] = (ind['ema_8'] < ind['ema_21']) & (ind['ema_21'] < ind['ema_50'])
        
        # Strong momentum bars (last 3 bars)
        ind['momentum_up'] = np.zeros(n, dtype=bool)
        ind['momentum_down'] = np.zeros(n, dtype=bool)
        for i in range(5, n):
            up_bars = sum(1 for j in range(i-2, i+1) if closes[j] > opens[j])
            down_bars = sum(1 for j in range(i-2, i+1) if closes[j] < opens[j])
            ind['momentum_up'][i] = up_bars >= 2
            ind['momentum_down'][i] = down_bars >= 2
        
        # Recent higher highs / lower lows
        ind['higher_high'] = np.zeros(n, dtype=bool)
        ind['lower_low'] = np.zeros(n, dtype=bool)
        for i in range(5, n):
            ind['higher_high'][i] = highs[i] > max(highs[i-5:i])
            ind['lower_low'][i] = lows[i] < min(lows[i-5:i])
        
        # Candle strength
        body = np.abs(closes - opens)
        range_hl = highs - lows + 1e-10
        ind['strong_bar'] = body > 0.5 * range_hl
        ind['bullish'] = closes > opens
        ind['bearish'] = closes < opens
        
        return ind
    
    def generate_signals(self, df, symbol="EUR/USD"):
        print(f"[HF Scalper v2] Generating signals for {symbol}...")
        print(f"[HF Scalper v2] Data: {len(df)} bars, Leverage: {self.leverage}:1")
        
        n = len(df)
        if n < 60:
            return []
        
        ind = self._calculate_indicators(df)
        
        signals = []
        last_signal_bar = -100
        daily_trades = {}
        
        closes = df['close'].values
        
        for i in range(55, n):
            time = df.iloc[i]['time']
            
            # Session filter
            if not self._is_good_session(time):
                continue
            
            # Cooldown
            if i - last_signal_bar < self.min_bars_between:
                continue
            
            # Daily limit
            try:
                trade_date = time.date()
                if trade_date not in daily_trades:
                    daily_trades[trade_date] = 0
                if daily_trades[trade_date] >= 15:  # Max 15/day
                    continue
            except:
                trade_date = None
            
            atr = ind['atr'][i]
            if atr < self.pip_value * 2:
                atr = self.pip_value * 5
            
            close_price = closes[i]
            
            # WIDER stops: 1.5x ATR stop, 2.5x ATR target (1.67 R:R)
            sl_distance = 1.5 * atr
            tp_distance = 2.5 * atr
            
            signal_type = None
            reason = ""
            
            # ===== SIMPLE BUY RULES =====
            # 1. Trend aligned + momentum + RSI confirmation
            if (ind['uptrend'][i] and
                ind['momentum_up'][i] and
                ind['strong_bar'][i] and
                ind['bullish'][i] and
                40 < ind['rsi'][i] < 70):
                signal_type = 'BUY'
                reason = 'Trend+Mom'
            
            # 2. Breakout: higher high in uptrend
            elif (ind['uptrend'][i] and
                  ind['higher_high'][i] and
                  ind['bullish'][i] and
                  ind['rsi'][i] > 50):
                signal_type = 'BUY'
                reason = 'Breakout'
            
            # ===== SIMPLE SELL RULES =====
            # 1. Trend aligned + momentum + RSI confirmation
            elif (ind['downtrend'][i] and
                  ind['momentum_down'][i] and
                  ind['strong_bar'][i] and
                  ind['bearish'][i] and
                  30 < ind['rsi'][i] < 60):
                signal_type = 'SELL'
                reason = 'Trend+Mom'
            
            # 2. Breakdown: lower low in downtrend
            elif (ind['downtrend'][i] and
                  ind['lower_low'][i] and
                  ind['bearish'][i] and
                  ind['rsi'][i] < 50):
                signal_type = 'SELL'
                reason = 'Breakdown'
            
            if signal_type:
                if signal_type == 'BUY':
                    signals.append({
                        'index': i,
                        'time': time,
                        'type': 'BUY',
                        'sl': close_price - sl_distance,
                        'tp': close_price + tp_distance,
                        'risk': self.risk_per_trade,
                        'comment': f'HFv2 {reason}'
                    })
                else:
                    signals.append({
                        'index': i,
                        'time': time,
                        'type': 'SELL',
                        'sl': close_price + sl_distance,
                        'tp': close_price - tp_distance,
                        'risk': self.risk_per_trade,
                        'comment': f'HFv2 {reason}'
                    })
                
                last_signal_bar = i
                if trade_date:
                    daily_trades[trade_date] += 1
        
        print(f"[HF Scalper v2] Generated {len(signals)} signals")
        if daily_trades:
            avg_daily = len(signals) / len(daily_trades)
            print(f"[HF Scalper v2] Average trades/day: {avg_daily:.1f}")
        
        return signals


def hf_scalping_v2(df, symbol="EUR/USD"):
    strategy = HFScalperV2(leverage=100, risk_per_trade=0.015)
    return strategy.generate_signals(df, symbol)


if __name__ == "__main__":
    print("HF Scalper v2 - Improved Version")
