"""
Ultra-Tight Scalper - 1 Pip Take Profit
The simplest possible approach: grab 1 pip profit very quickly

Entry: After 2+ consecutive candles in same direction
Exit: 1 pip profit (0.0001) or 5 pip loss (0.0005)

Goal: High frequency, ultra-high win rate
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


class UltraTightScalper:
    def __init__(self, leverage=100):
        self.leverage = leverage
        self.pip = 0.0001
        self.tp_pips = 1.0  # 1 pip TP
        self.sl_pips = 5.0  # 5 pip SL
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
    
    def _is_trading_hour(self, time):
        try:
            hour = time.hour
            return 8 <= hour <= 18  # Tighter session
        except:
            return True
    
    def generate_signals(self, df, symbol="EUR/USD"):
        print(f"[UltraTight] Generating signals for {symbol}...")
        print(f"[UltraTight] TP: {self.tp_pips} pip, SL: {self.sl_pips} pips")
        
        n = len(df)
        if n < 20:
            return []
        
        closes = df['close'].values
        opens = df['open'].values
        highs = df['high'].values
        lows = df['low'].values
        
        # Calculate fast EMA
        ema_5 = self._ema(closes, 5)
        ema_10 = self._ema(closes, 10)
        
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
                if daily_trades[trade_date] >= 25:
                    continue
            except:
                trade_date = None
            
            close_price = closes[i]
            
            # Count consecutive candles
            consec_up = 0
            consec_down = 0
            for j in range(i, max(i-5, 0), -1):
                if closes[j] > opens[j]:
                    consec_up += 1
                else:
                    break
            for j in range(i, max(i-5, 0), -1):
                if closes[j] < opens[j]:
                    consec_down += 1
                else:
                    break
            
            # Current candle is strong
            body = abs(closes[i] - opens[i])
            range_hl = highs[i] - lows[i] + 1e-10
            is_strong = body > 0.5 * range_hl
            
            # EMA direction
            ema_up = ema_5[i] > ema_10[i]
            ema_down = ema_5[i] < ema_10[i]
            
            signal_type = None
            
            # BUY: 2+ green candles + EMA alignment + strong current
            if consec_up >= 2 and ema_up and is_strong and closes[i] > opens[i]:
                signal_type = 'BUY'
            
            # SELL: 2+ red candles + EMA alignment + strong current
            elif consec_down >= 2 and ema_down and is_strong and closes[i] < opens[i]:
                signal_type = 'SELL'
            
            if signal_type:
                tp_dist = self.tp_pips * self.pip
                sl_dist = self.sl_pips * self.pip
                
                if signal_type == 'BUY':
                    signals.append({
                        'index': i,
                        'time': time,
                        'type': 'BUY',
                        'sl': close_price - sl_dist,
                        'tp': close_price + tp_dist,
                        'risk': 0.01,
                        'comment': f'Ultra {consec_up}G'
                    })
                else:
                    signals.append({
                        'index': i,
                        'time': time,
                        'type': 'SELL',
                        'sl': close_price + sl_dist,
                        'tp': close_price - tp_dist,
                        'risk': 0.01,
                        'comment': f'Ultra {consec_down}R'
                    })
                
                last_signal_bar = i
                if trade_date:
                    daily_trades[trade_date] += 1
        
        print(f"[UltraTight] Generated {len(signals)} signals")
        if daily_trades:
            print(f"[UltraTight] Avg/day: {len(signals)/len(daily_trades):.1f}")
        
        return signals


def ultra_tight_strategy(df, symbol="EUR/USD"):
    strategy = UltraTightScalper(leverage=100)
    return strategy.generate_signals(df, symbol)
