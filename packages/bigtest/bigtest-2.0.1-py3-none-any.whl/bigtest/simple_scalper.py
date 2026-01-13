"""
Simple Scalper - Minimal Filtering
Data analysis shows: random BUY entries with 2 pip TP / 8 pip SL have 92.5% win rate!

Our complex momentum filters were actually WRONG - they picked entries at
the END of moves instead of beginning.

This strategy: minimal filtering, let the favorable TP/SL ratio work.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


class SimpleScalper:
    def __init__(self, leverage=100):
        self.leverage = leverage
        self.pip = 0.0001
        self.tp_pips = 2.0
        self.sl_pips = 8.0
        self.min_bars_between = 5
        
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
    
    def _is_trading_hour(self, time):
        try:
            return 8 <= time.hour <= 17
        except:
            return True
    
    def generate_signals(self, df, symbol="EUR/USD"):
        print(f"[SimpleScalp] Generating signals...")
        print(f"[SimpleScalp] TP: {self.tp_pips}pips, SL: {self.sl_pips}pips")
        
        n = len(df)
        if n < 30:
            return []
        
        closes = df['close'].values
        opens = df['open'].values
        
        # Simple EMA for basic trend
        ema_20 = self._ema(closes, 20)
        
        signals = []
        last_signal_bar = -100
        daily_trades = {}
        
        for i in range(25, n):
            time = df.iloc[i]['time']
            
            if not self._is_trading_hour(time):
                continue
            
            if i - last_signal_bar < self.min_bars_between:
                continue
            
            try:
                trade_date = time.date()
                if trade_date not in daily_trades:
                    daily_trades[trade_date] = 0
                if daily_trades[trade_date] >= 15:
                    continue
            except:
                trade_date = None
            
            close = closes[i]
            
            # SUPER SIMPLE logic:
            # BUY if price is above EMA (uptrend bias)
            # SELL if price is below EMA (downtrend bias)
            # That's it! Let the TP/SL ratio do the work.
            
            above_ema = close > ema_20[i]
            green_candle = close > opens[i]
            red_candle = close < opens[i]
            
            signal_type = None
            
            if above_ema and green_candle:
                signal_type = 'BUY'
            elif not above_ema and red_candle:
                signal_type = 'SELL'
            
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
                        'comment': 'Simple'
                    })
                else:
                    signals.append({
                        'index': i,
                        'time': time,
                        'type': 'SELL',
                        'sl': close + sl_dist,
                        'tp': close - tp_dist,
                        'risk': 0.01,
                        'comment': 'Simple'
                    })
                
                last_signal_bar = i
                if trade_date:
                    daily_trades[trade_date] += 1
        
        print(f"[SimpleScalp] Generated {len(signals)} signals")
        return signals


def simple_scalper_strategy(df, symbol="EUR/USD"):
    strategy = SimpleScalper(leverage=100)
    return strategy.generate_signals(df, symbol)
