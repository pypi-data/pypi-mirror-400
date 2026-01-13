"""
Hybrid ML Scalping Strategy for EUR/USD
Combines rule-based entry signals with ML confirmation

Approach:
1. Use classic technical patterns (EMA crossover, RSI divergence) for primary signals
2. ML model provides confirmation/rejection based on market regime
3. Strict trade management with dynamic SL/TP

This is more robust than pure ML because:
- Human-designed rules capture known edge cases
- ML adds adaptive filtering based on current conditions
- Reduces overfitting by limiting ML's role to confirmation
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


class HybridScalpingStrategy:
    """
    Hybrid strategy combining rule-based signals with ML confirmation.
    """
    
    def __init__(self):
        self.scaler = StandardScaler() if ML_AVAILABLE else None
        self.model = None
        self.is_fitted = False
    
    def _ema(self, data, period):
        """EMA calculation"""
        ema = np.zeros(len(data))
        if len(data) < period:
            return ema
        multiplier = 2 / (period + 1)
        ema[period-1] = np.mean(data[:period])
        for i in range(period, len(data)):
            ema[i] = (data[i] - ema[i-1]) * multiplier + ema[i-1]
        return ema
    
    def _rsi(self, closes, period):
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
    
    def _calculate_indicators(self, df):
        """Calculate all necessary indicators"""
        closes = df['close'].values
        highs = df['high'].values
        lows = df['low'].values
        opens = df['open'].values
        n = len(df)
        
        indicators = {}
        
        # EMAs
        indicators['ema_9'] = self._ema(closes, 9)
        indicators['ema_21'] = self._ema(closes, 21)
        indicators['ema_50'] = self._ema(closes, 50)
        
        # RSI
        indicators['rsi_14'] = self._rsi(closes, 14)
        
        # ATR
        indicators['atr_14'] = self._atr(highs, lows, closes, 14)
        
        # Price position relative to EMAs
        indicators['above_ema9'] = closes > indicators['ema_9']
        indicators['above_ema21'] = closes > indicators['ema_21']
        indicators['above_ema50'] = closes > indicators['ema_50']
        
        # EMA crossovers
        ema_9_21_diff = indicators['ema_9'] - indicators['ema_21']
        indicators['ema_9_cross_21_up'] = np.zeros(n, dtype=bool)
        indicators['ema_9_cross_21_down'] = np.zeros(n, dtype=bool)
        for i in range(1, n):
            if ema_9_21_diff[i] > 0 and ema_9_21_diff[i-1] <= 0:
                indicators['ema_9_cross_21_up'][i] = True
            if ema_9_21_diff[i] < 0 and ema_9_21_diff[i-1] >= 0:
                indicators['ema_9_cross_21_down'][i] = True
        
        # RSI divergence (momentum)
        indicators['rsi_oversold'] = indicators['rsi_14'] < 30
        indicators['rsi_overbought'] = indicators['rsi_14'] > 70
        indicators['rsi_bullish'] = (indicators['rsi_14'] > 50) & (indicators['rsi_14'] < 70)
        indicators['rsi_bearish'] = (indicators['rsi_14'] < 50) & (indicators['rsi_14'] > 30)
        
        # Candle patterns
        body = np.abs(closes - opens)
        range_hl = highs - lows + 1e-10
        indicators['strong_bullish'] = (closes > opens) & (body > 0.6 * range_hl)
        indicators['strong_bearish'] = (closes < opens) & (body > 0.6 * range_hl)
        
        # Trend strength
        indicators['ema_21_slope'] = np.zeros(n)
        for i in range(5, n):
            indicators['ema_21_slope'][i] = (indicators['ema_21'][i] - indicators['ema_21'][i-5]) / (closes[i] + 1e-10)
        
        # Recent high/low
        for i in range(20, n):
            indicators[f'near_high_20_{i}'] = closes[i] > 0.98 * np.max(highs[i-20:i+1])
            indicators[f'near_low_20_{i}'] = closes[i] < 1.02 * np.min(lows[i-20:i+1])
        
        return indicators
    
    def _generate_rule_signals(self, df, indicators, i):
        """
        Generate rule-based signals.
        Returns: 'BUY', 'SELL', or None
        """
        closes = df['close'].values
        
        # Skip if no ATR data
        atr = indicators['atr_14'][i]
        if atr < 0.00001:
            return None
        
        signal = None
        reason = ""
        
        # ====== BUY SIGNALS ======
        
        # 1. EMA 9/21 Golden Cross with trend confirmation
        if (indicators['ema_9_cross_21_up'][i] and 
            indicators['above_ema50'][i] and
            indicators['rsi_bullish'][i]):
            signal = 'BUY'
            reason = "EMA Cross + Trend"
        
        # 2. RSI Oversold bounce in uptrend
        elif (indicators['rsi_14'][i-1] < 30 and 
              indicators['rsi_14'][i] > 30 and
              indicators['above_ema21'][i] and
              i > 1):
            signal = 'BUY'
            reason = "RSI Bounce"
        
        # 3. Strong bullish candle after pullback to EMA21
        elif (indicators['strong_bullish'][i] and
              closes[i-1] < indicators['ema_21'][i-1] * 1.001 and
              closes[i-1] > indicators['ema_21'][i-1] * 0.999 and
              indicators['ema_21_slope'][i] > 0.00001 and
              i > 1):
            signal = 'BUY'
            reason = "EMA21 Bounce"
        
        # ====== SELL SIGNALS ======
        
        # 1. EMA 9/21 Death Cross with trend confirmation
        if (indicators['ema_9_cross_21_down'][i] and 
            not indicators['above_ema50'][i] and
            indicators['rsi_bearish'][i]):
            signal = 'SELL'
            reason = "EMA Cross + Trend"
        
        # 2. RSI Overbought rejection in downtrend
        elif (indicators['rsi_14'][i-1] > 70 and 
              indicators['rsi_14'][i] < 70 and
              not indicators['above_ema21'][i] and
              i > 1):
            signal = 'SELL'
            reason = "RSI Rejection"
        
        # 3. Strong bearish candle after rally to EMA21
        elif (indicators['strong_bearish'][i] and
              closes[i-1] > indicators['ema_21'][i-1] * 0.999 and
              closes[i-1] < indicators['ema_21'][i-1] * 1.001 and
              indicators['ema_21_slope'][i] < -0.00001 and
              i > 1):
            signal = 'SELL'
            reason = "EMA21 Rejection"
        
        return (signal, reason) if signal else (None, None)
    
    def _prepare_ml_features(self, df, indicators, i):
        """Prepare features for ML confirmation"""
        closes = df['close'].values
        
        features = [
            indicators['rsi_14'][i] / 100,  # Normalized RSI
            1 if indicators['above_ema9'][i] else 0,
            1 if indicators['above_ema21'][i] else 0,
            1 if indicators['above_ema50'][i] else 0,
            indicators['ema_21_slope'][i] * 1000,  # Scaled slope
            indicators['atr_14'][i] / (closes[i] + 1e-10) * 100,  # ATR percentage
            (closes[i] - indicators['ema_21'][i]) / (closes[i] + 1e-10),  # Distance from EMA21
        ]
        
        return np.array(features).reshape(1, -1)
    
    def _prepare_ml_training_data(self, df, indicators, start_idx, end_idx):
        """Prepare training data for ML model"""
        closes = df['close'].values
        X = []
        y = []
        
        for i in range(start_idx, end_idx - 5):
            features = self._prepare_ml_features(df, indicators, i).flatten()
            
            # Label based on future 5-bar return
            future_return = (closes[i+5] - closes[i]) / (closes[i] + 1e-10)
            atr = indicators['atr_14'][i]
            threshold = atr / (closes[i] + 1e-10) * 0.5
            
            if future_return > threshold:
                label = 1  # Good for BUY
            elif future_return < -threshold:
                label = -1  # Good for SELL
            else:
                label = 0  # Neutral
            
            X.append(features)
            y.append(label)
        
        return np.array(X), np.array(y)
    
    def _train_ml_model(self, df, indicators, end_idx, lookback=300):
        """Train ML model for confirmation"""
        if not ML_AVAILABLE:
            return
        
        start_idx = max(60, end_idx - lookback)
        X, y = self._prepare_ml_training_data(df, indicators, start_idx, end_idx)
        
        if len(X) < 50 or len(np.unique(y)) < 2:
            return
        
        try:
            self.model = RandomForestClassifier(
                n_estimators=50,
                max_depth=4,
                min_samples_leaf=20,
                random_state=42,
                n_jobs=-1
            )
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)
            self.model.fit(X_scaled, y)
            self.is_fitted = True
        except Exception:
            pass
    
    def _get_ml_confirmation(self, df, indicators, i, signal_type):
        """Get ML confirmation for a signal"""
        if not self.is_fitted or not ML_AVAILABLE:
            return True, 0.5  # Default: allow without ML
        
        try:
            features = self._prepare_ml_features(df, indicators, i)
            features_scaled = self.scaler.transform(features)
            proba = self.model.predict_proba(features_scaled)[0]
            
            classes = self.model.classes_
            prob_dict = {c: proba[j] for j, c in enumerate(classes)}
            
            if signal_type == 'BUY':
                prob_favorable = prob_dict.get(1, 0)
                prob_unfavorable = prob_dict.get(-1, 0)
            else:
                prob_favorable = prob_dict.get(-1, 0)
                prob_unfavorable = prob_dict.get(1, 0)
            
            # Confirm if favorable probability is higher
            confirmed = prob_favorable > prob_unfavorable and prob_favorable > 0.35
            return confirmed, prob_favorable
        except Exception:
            return True, 0.5
    
    def generate_signals(self, df, symbol="EUR/USD"):
        """Generate trading signals"""
        print(f"[Hybrid] Generating signals for {symbol}...")
        print(f"[Hybrid] Data length: {len(df)} bars")
        
        n = len(df)
        if n < 60:
            print("[Hybrid] Not enough data")
            return []
        
        # Calculate indicators
        print("[Hybrid] Calculating indicators...")
        indicators = self._calculate_indicators(df)
        
        signals = []
        last_signal_bar = -50
        min_bars_between = 8
        retraining_interval = 100
        
        for i in range(60, n):
            # Retrain ML periodically
            if i % retraining_interval == 0:
                self._train_ml_model(df, indicators, i)
            
            # Check cooldown
            if i - last_signal_bar < min_bars_between:
                continue
            
            # Get rule-based signal
            signal_type, reason = self._generate_rule_signals(df, indicators, i)
            
            if signal_type is None:
                continue
            
            # Get ML confirmation
            confirmed, prob = self._get_ml_confirmation(df, indicators, i, signal_type)
            
            if not confirmed:
                continue
            
            # Generate signal
            close_price = df.iloc[i]['close']
            time = df.iloc[i]['time']
            atr = indicators['atr_14'][i]
            
            if atr < 0.00001:
                atr = 0.0005
            
            sl_distance = 2.0 * atr
            tp_distance = 3.0 * atr  # 1.5 R:R
            
            if signal_type == 'BUY':
                signals.append({
                    'index': i,
                    'time': time,
                    'type': 'BUY',
                    'sl': close_price - sl_distance,
                    'tp': close_price + tp_distance,
                    'risk': 0.01,
                    'comment': f'Hybrid Buy: {reason} (ML:{prob:.2f})'
                })
            else:
                signals.append({
                    'index': i,
                    'time': time,
                    'type': 'SELL',
                    'sl': close_price + sl_distance,
                    'tp': close_price - tp_distance,
                    'risk': 0.01,
                    'comment': f'Hybrid Sell: {reason} (ML:{prob:.2f})'
                })
            
            last_signal_bar = i
        
        print(f"[Hybrid] Generated {len(signals)} signals")
        return signals


def hybrid_ml_strategy(df, symbol="EUR/USD"):
    """Strategy function for bigtest backtester"""
    strategy = HybridScalpingStrategy()
    return strategy.generate_signals(df, symbol)


if __name__ == "__main__":
    print("Hybrid ML Scalping Strategy")
    print(f"ML Available: {ML_AVAILABLE}")
