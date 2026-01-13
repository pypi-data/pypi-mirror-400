"""
High-Frequency Scalping Strategy for EUR/USD
1-minute timeframe with 1:100 leverage

Target: 10-20 trades per day, 20-30% daily profit

WARNING: This is an extremely aggressive strategy with high leverage.
         Only use with capital you can afford to lose completely.

Strategy Logic:
1. Trade during high-volatility sessions (London/NY overlap)
2. Use momentum + mean reversion combo
3. Quick entries and exits (5-15 pips profit target)
4. Tight stop losses (3-8 pips)
5. High win rate focus with R:R around 1.5:1
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


class HighFrequencyScalper:
    """
    Aggressive 1-minute scalping strategy with 1:100 leverage.
    Targets 10-20 trades per day during active sessions.
    """
    
    def __init__(self, leverage=100, risk_per_trade=0.02, daily_profit_target=0.25):
        """
        Args:
            leverage: Account leverage (default 100:1)
            risk_per_trade: Fraction of capital risked per trade (0.02 = 2%)
            daily_profit_target: Target daily return (0.25 = 25%)
        """
        self.leverage = leverage
        self.risk_per_trade = risk_per_trade
        self.daily_profit_target = daily_profit_target
        
        # Strategy parameters
        self.pip_value = 0.0001  # EUR/USD pip
        self.target_pips = 8    # Take profit in pips
        self.stop_pips = 5      # Stop loss in pips (1.6:1 R:R)
        self.min_bars_between = 5  # Minimum 5 minutes between trades
        
    def _ema(self, data, period):
        """Fast EMA calculation"""
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
        """Fast RSI for quick momentum"""
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
        """ATR for volatility-adjusted stops"""
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
    
    def _is_active_session(self, time):
        """Check if in active trading session (London-NY overlap best)"""
        if pd.isna(time):
            return True
        
        try:
            hour = time.hour
            # London: 8-16 UTC, NY: 13-21 UTC
            # Best overlap: 13-16 UTC (8-11 AM EST)
            return 7 <= hour <= 20  # Extended active hours
        except:
            return True
    
    def _calculate_indicators(self, df):
        """Calculate scalping indicators"""
        closes = df['close'].values
        highs = df['high'].values
        lows = df['low'].values
        opens = df['open'].values
        n = len(df)
        
        ind = {}
        
        # Fast EMAs for scalping
        ind['ema_5'] = self._ema(closes, 5)
        ind['ema_10'] = self._ema(closes, 10)
        ind['ema_20'] = self._ema(closes, 20)
        
        # Fast RSI
        ind['rsi_7'] = self._rsi(closes, 7)
        
        # ATR for volatility
        ind['atr'] = self._atr(highs, lows, closes, 10)
        
        # Price momentum (3-bar)
        ind['momentum'] = np.zeros(n)
        for i in range(3, n):
            ind['momentum'][i] = (closes[i] - closes[i-3]) / (closes[i-3] + 1e-10)
        
        # EMA alignment
        ind['bullish_ema'] = (ind['ema_5'] > ind['ema_10']) & (ind['ema_10'] > ind['ema_20'])
        ind['bearish_ema'] = (ind['ema_5'] < ind['ema_10']) & (ind['ema_10'] < ind['ema_20'])
        
        # Candle patterns
        body = closes - opens
        range_hl = highs - lows + 1e-10
        ind['body_ratio'] = np.abs(body) / range_hl
        ind['bullish_candle'] = body > 0
        ind['bearish_candle'] = body < 0
        ind['strong_candle'] = ind['body_ratio'] > 0.6
        
        # RSI zones
        ind['rsi_oversold'] = ind['rsi_7'] < 30
        ind['rsi_overbought'] = ind['rsi_7'] > 70
        ind['rsi_bullish'] = (ind['rsi_7'] > 45) & (ind['rsi_7'] < 70)
        ind['rsi_bearish'] = (ind['rsi_7'] < 55) & (ind['rsi_7'] > 30)
        
        # Volatility filter (need minimum ATR)
        avg_atr = np.mean(ind['atr'][ind['atr'] > 0])
        ind['volatility_ok'] = ind['atr'] > 0.3 * avg_atr
        
        # EMA crossovers
        ind['ema_5_cross_10_up'] = np.zeros(n, dtype=bool)
        ind['ema_5_cross_10_down'] = np.zeros(n, dtype=bool)
        ema_diff = ind['ema_5'] - ind['ema_10']
        for i in range(1, n):
            if ema_diff[i] > 0 and ema_diff[i-1] <= 0:
                ind['ema_5_cross_10_up'][i] = True
            if ema_diff[i] < 0 and ema_diff[i-1] >= 0:
                ind['ema_5_cross_10_down'][i] = True
        
        # Price relative to EMA20
        ind['above_ema20'] = closes > ind['ema_20']
        ind['below_ema20'] = closes < ind['ema_20']
        
        # Quick momentum bounce
        ind['momentum_positive'] = ind['momentum'] > 0.0001
        ind['momentum_negative'] = ind['momentum'] < -0.0001
        
        return ind
    
    def generate_signals(self, df, symbol="EUR/USD"):
        """Generate high-frequency scalping signals"""
        print(f"[HF Scalper] Generating signals for {symbol}...")
        print(f"[HF Scalper] Data length: {len(df)} bars")
        print(f"[HF Scalper] Leverage: {self.leverage}:1")
        print(f"[HF Scalper] Risk per trade: {self.risk_per_trade*100:.1f}%")
        
        n = len(df)
        if n < 30:
            print("[HF Scalper] Not enough data")
            return []
        
        # Calculate indicators
        print("[HF Scalper] Calculating indicators...")
        ind = self._calculate_indicators(df)
        
        signals = []
        last_signal_bar = -100
        daily_trades = {}  # Track trades per day
        
        closes = df['close'].values
        
        for i in range(25, n):
            time = df.iloc[i]['time']
            
            # Session filter
            if not self._is_active_session(time):
                continue
            
            # Volatility filter
            if not ind['volatility_ok'][i]:
                continue
            
            # Cooldown
            if i - last_signal_bar < self.min_bars_between:
                continue
            
            # Count daily trades
            try:
                trade_date = time.date()
                if trade_date not in daily_trades:
                    daily_trades[trade_date] = 0
                
                # Limit to 20 trades per day max
                if daily_trades[trade_date] >= 20:
                    continue
            except:
                trade_date = None
            
            close_price = closes[i]
            atr = ind['atr'][i]
            
            if atr < self.pip_value:
                atr = self.pip_value * 5
            
            # Dynamic SL/TP based on ATR
            sl_distance = max(self.stop_pips * self.pip_value, 0.8 * atr)
            tp_distance = max(self.target_pips * self.pip_value, 1.3 * atr)
            
            signal_type = None
            reason = ""
            
            # ========== BUY SIGNALS ==========
            
            # 1. EMA crossover in uptrend
            if (ind['ema_5_cross_10_up'][i] and
                ind['above_ema20'][i] and
                ind['rsi_bullish'][i] and
                ind['bullish_candle'][i]):
                signal_type = 'BUY'
                reason = 'EMA Cross Up'
            
            # 2. RSI oversold bounce
            elif (ind['rsi_7'][i-1] < 25 and ind['rsi_7'][i] > 30 and
                  ind['bullish_candle'][i] and
                  ind['strong_candle'][i] and
                  ind['momentum_positive'][i]):
                signal_type = 'BUY'
                reason = 'RSI Bounce'
            
            # 3. Momentum breakout (all EMAs aligned + strong candle)
            elif (ind['bullish_ema'][i] and
                  ind['strong_candle'][i] and
                  ind['bullish_candle'][i] and
                  ind['rsi_7'][i] > 55 and ind['rsi_7'][i] < 75 and
                  ind['momentum'][i] > 0.0002):
                signal_type = 'BUY'
                reason = 'Momentum Breakout'
            
            # ========== SELL SIGNALS ==========
            
            # 1. EMA crossover in downtrend  
            elif (ind['ema_5_cross_10_down'][i] and
                  ind['below_ema20'][i] and
                  ind['rsi_bearish'][i] and
                  ind['bearish_candle'][i]):
                signal_type = 'SELL'
                reason = 'EMA Cross Down'
            
            # 2. RSI overbought rejection
            elif (ind['rsi_7'][i-1] > 75 and ind['rsi_7'][i] < 70 and
                  ind['bearish_candle'][i] and
                  ind['strong_candle'][i] and
                  ind['momentum_negative'][i]):
                signal_type = 'SELL'
                reason = 'RSI Rejection'
            
            # 3. Momentum breakdown
            elif (ind['bearish_ema'][i] and
                  ind['strong_candle'][i] and
                  ind['bearish_candle'][i] and
                  ind['rsi_7'][i] < 45 and ind['rsi_7'][i] > 25 and
                  ind['momentum'][i] < -0.0002):
                signal_type = 'SELL'
                reason = 'Momentum Breakdown'
            
            # Generate signal
            if signal_type:
                if signal_type == 'BUY':
                    signals.append({
                        'index': i,
                        'time': time,
                        'type': 'BUY',
                        'sl': close_price - sl_distance,
                        'tp': close_price + tp_distance,
                        'risk': self.risk_per_trade,
                        'comment': f'HF {reason}'
                    })
                else:
                    signals.append({
                        'index': i,
                        'time': time,
                        'type': 'SELL',
                        'sl': close_price + sl_distance,
                        'tp': close_price - tp_distance,
                        'risk': self.risk_per_trade,
                        'comment': f'HF {reason}'
                    })
                
                last_signal_bar = i
                if trade_date:
                    daily_trades[trade_date] += 1
        
        # Print daily distribution
        print(f"[HF Scalper] Generated {len(signals)} signals")
        if daily_trades:
            avg_daily = len(signals) / len(daily_trades) if daily_trades else 0
            print(f"[HF Scalper] Average trades/day: {avg_daily:.1f}")
        
        return signals


def hf_scalping_strategy(df, symbol="EUR/USD"):
    """Strategy function for bigtest backtester"""
    strategy = HighFrequencyScalper(
        leverage=100,
        risk_per_trade=0.02,  # 2% risk per trade
        daily_profit_target=0.25  # 25% daily target
    )
    return strategy.generate_signals(df, symbol)


if __name__ == "__main__":
    print("High-Frequency Scalping Strategy")
    print("Target: 10-20 trades/day, 20-30% daily return")
    print("Leverage: 1:100")
    print("\nWARNING: Extremely high risk strategy!")
