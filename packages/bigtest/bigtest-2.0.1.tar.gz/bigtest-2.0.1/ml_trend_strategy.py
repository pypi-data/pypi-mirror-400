"""
ML Trend-Following Strategy for EUR/USD
A more conservative approach designed for 1h timeframe

Key Principles:
1. Trade with the trend only (EMA 50/100 alignment)
2. Enter on pullbacks to support/resistance
3. Use ML to confirm momentum
4. Wider stops, higher R:R (1:3)
5. Fewer trades, higher quality
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False


class TrendFollowingStrategy:
    """
    Conservative trend-following strategy for forex.
    Designed for 1h timeframe with high R:R trades.
    """
    
    def __init__(self):
        self.scaler = StandardScaler() if ML_AVAILABLE else None
        self.model = None
        self.is_fitted = False
    
    def _ema(self, data, period):
        """EMA calculation"""
        n = len(data)
        ema = np.zeros(n)
        if n < period:
            return ema
        multiplier = 2 / (period + 1)
        ema[period-1] = np.mean(data[:period])
        for i in range(period, n):
            ema[i] = (data[i] - ema[i-1]) * multiplier + ema[i-1]
        return ema
    
    def _atr(self, highs, lows, closes, period):
        """ATR calculation"""
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
    
    def _rsi(self, closes, period=14):
        """RSI calculation"""
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
    
    def _calculate_indicators(self, df):
        """Calculate trend indicators"""
        closes = df['close'].values
        highs = df['high'].values
        lows = df['low'].values
        opens = df['open'].values
        n = len(df)
        
        ind = {}
        
        # Core EMAs for trend
        ind['ema_20'] = self._ema(closes, 20)
        ind['ema_50'] = self._ema(closes, 50)
        ind['ema_100'] = self._ema(closes, 100)
        
        # ATR
        ind['atr'] = self._atr(highs, lows, closes, 14)
        
        # RSI
        ind['rsi'] = self._rsi(closes, 14)
        
        # Trend direction
        ind['uptrend'] = (ind['ema_20'] > ind['ema_50']) & (ind['ema_50'] > ind['ema_100'])
        ind['downtrend'] = (ind['ema_20'] < ind['ema_50']) & (ind['ema_50'] < ind['ema_100'])
        
        # Pullback detection
        ind['pullback_to_ema20'] = np.zeros(n, dtype=bool)
        ind['rally_to_ema20'] = np.zeros(n, dtype=bool)
        
        for i in range(1, n):
            # Pullback: price touched or went below EMA20 then closed above
            if (lows[i] <= ind['ema_20'][i] * 1.002 and 
                closes[i] > ind['ema_20'][i] and
                closes[i] > opens[i]):  # Bullish close
                ind['pullback_to_ema20'][i] = True
            
            # Rally: price touched or went above EMA20 then closed below  
            if (highs[i] >= ind['ema_20'][i] * 0.998 and
                closes[i] < ind['ema_20'][i] and
                closes[i] < opens[i]):  # Bearish close
                ind['rally_to_ema20'][i] = True
        
        # Momentum confirmation
        ind['rsi_bullish'] = (ind['rsi'] > 40) & (ind['rsi'] < 70)
        ind['rsi_bearish'] = (ind['rsi'] < 60) & (ind['rsi'] > 30)
        
        # Candle strength
        body = np.abs(closes - opens)
        range_hl = highs - lows + 1e-10
        ind['strong_candle'] = body > 0.5 * range_hl
        ind['bullish_candle'] = closes > opens
        ind['bearish_candle'] = closes < opens
        
        return ind
    
    def _train_momentum_model(self, df, ind, end_idx, lookback=200):
        """Train simple momentum classifier"""
        if not ML_AVAILABLE:
            return
        
        closes = df['close'].values
        X = []
        y = []
        
        start_idx = max(105, end_idx - lookback)
        
        for i in range(start_idx, end_idx - 10):
            features = [
                ind['rsi'][i] / 100,
                1 if ind['uptrend'][i] else (-1 if ind['downtrend'][i] else 0),
                (closes[i] - ind['ema_20'][i]) / (ind['atr'][i] + 1e-10),
                (closes[i] - ind['ema_50'][i]) / (ind['atr'][i] + 1e-10),
                (ind['ema_20'][i] - ind['ema_50'][i]) / (ind['atr'][i] + 1e-10),
            ]
            
            # Label: future 10-bar return direction
            future_return = (closes[i+10] - closes[i]) / (closes[i] + 1e-10)
            atr_norm = ind['atr'][i] / (closes[i] + 1e-10)
            
            if future_return > atr_norm:
                label = 1
            elif future_return < -atr_norm:
                label = -1
            else:
                label = 0
            
            X.append(features)
            y.append(label)
        
        X = np.array(X)
        y = np.array(y)
        
        if len(X) < 30 or len(np.unique(y)) < 2:
            return
        
        try:
            self.model = RandomForestClassifier(
                n_estimators=30,
                max_depth=3,
                min_samples_leaf=15,
                random_state=42,
                n_jobs=-1
            )
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)
            self.model.fit(X_scaled, y)
            self.is_fitted = True
        except Exception:
            pass
    
    def _get_momentum_score(self, df, ind, i):
        """Get ML momentum score"""
        default_score = {1: 0.33, 0: 0.34, -1: 0.33}
        
        if not self.is_fitted:
            return default_score
        
        closes = df['close'].values
        
        try:
            features = np.array([
                ind['rsi'][i] / 100,
                1 if ind['uptrend'][i] else (-1 if ind['downtrend'][i] else 0),
                (closes[i] - ind['ema_20'][i]) / (ind['atr'][i] + 1e-10),
                (closes[i] - ind['ema_50'][i]) / (ind['atr'][i] + 1e-10),
                (ind['ema_20'][i] - ind['ema_50'][i]) / (ind['atr'][i] + 1e-10),
            ]).reshape(1, -1)
            
            features_scaled = self.scaler.transform(features)
            proba = self.model.predict_proba(features_scaled)[0]
            classes = self.model.classes_
            
            return {c: proba[j] for j, c in enumerate(classes)}
        except Exception:
            return {1: 0.33, 0: 0.34, -1: 0.33}
    
    def generate_signals(self, df, symbol="EUR/USD"):
        """Generate trend-following signals"""
        print(f"[TrendFollow] Generating signals for {symbol}...")
        print(f"[TrendFollow] Data length: {len(df)} bars")
        
        n = len(df)
        if n < 110:
            print("[TrendFollow] Not enough data")
            return []
        
        # Calculate indicators
        print("[TrendFollow] Calculating indicators...")
        ind = self._calculate_indicators(df)
        
        signals = []
        last_signal_bar = -100
        min_bars_between = 10  # Conservative spacing
        
        closes = df['close'].values
        
        for i in range(105, n):
            # Train model periodically
            if i % 50 == 0:
                self._train_momentum_model(df, ind, i)
            
            # Cooldown check
            if i - last_signal_bar < min_bars_between:
                continue
            
            atr = ind['atr'][i]
            if atr < 0.00001:
                continue
            
            close_price = closes[i]
            time = df.iloc[i]['time']
            
            # Get momentum score
            mom_score = self._get_momentum_score(df, ind, i)
            
            # ===== BUY SIGNAL =====
            # Requirements:
            # 1. In uptrend (EMA alignment)
            # 2. Pullback to EMA20 with bullish close
            # 3. RSI in healthy zone
            # 4. Strong bullish candle
            # 5. ML momentum favors up
            
            if (ind['uptrend'][i] and
                ind['pullback_to_ema20'][i] and
                ind['rsi_bullish'][i] and
                ind['strong_candle'][i] and
                ind['bullish_candle'][i] and
                mom_score.get(1, 0) > mom_score.get(-1, 0)):
                
                sl_distance = 2.5 * atr
                tp_distance = 3.5 * atr  # 1.4:1 R:R
                
                signals.append({
                    'index': i,
                    'time': time,
                    'type': 'BUY',
                    'sl': close_price - sl_distance,
                    'tp': close_price + tp_distance,
                    'risk': 0.01,
                    'comment': f'Trend Buy (Mom:{mom_score.get(1, 0):.2f})'
                })
                last_signal_bar = i
            
            # ===== SELL SIGNAL =====
            elif (ind['downtrend'][i] and
                  ind['rally_to_ema20'][i] and
                  ind['rsi_bearish'][i] and
                  ind['strong_candle'][i] and
                  ind['bearish_candle'][i] and
                  mom_score.get(-1, 0) > mom_score.get(1, 0)):
                
                sl_distance = 2.5 * atr
                tp_distance = 3.5 * atr
                
                signals.append({
                    'index': i,
                    'time': time,
                    'type': 'SELL',
                    'sl': close_price + sl_distance,
                    'tp': close_price - tp_distance,
                    'risk': 0.01,
                    'comment': f'Trend Sell (Mom:{mom_score.get(-1, 0):.2f})'
                })
                last_signal_bar = i
        
        print(f"[TrendFollow] Generated {len(signals)} signals")
        return signals


def trend_following_strategy(df, symbol="EUR/USD"):
    """Strategy function for bigtest backtester"""
    strategy = TrendFollowingStrategy()
    return strategy.generate_signals(df, symbol)


if __name__ == "__main__":
    print("ML Trend-Following Strategy")
    print(f"ML Available: {ML_AVAILABLE}")
