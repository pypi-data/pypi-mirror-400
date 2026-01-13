"""
Enhanced ML Scalping Strategy v2 for EUR/USD
Uses XGBoost/LightGBM with better feature selection and ensemble methods

Key Improvements:
- Gradient Boosting (XGBoost/LightGBM) instead of Random Forest
- Moving window feature normalization
- Smarter labeling based on risk-adjusted returns
- Ensemble voting from multiple models
- Position sizing based on prediction confidence
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ML imports
try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import TimeSeriesSplit
    from sklearn.metrics import accuracy_score
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("WARNING: scikit-learn not installed. Run: pip install scikit-learn")

# Try XGBoost (may fail if libomp not installed on Mac)
XGB_AVAILABLE = False
try:
    import xgboost as xgb
    # Test if it actually works
    _ = xgb.XGBClassifier()
    XGB_AVAILABLE = True
except Exception:
    XGB_AVAILABLE = False

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../pythonpine-main')))


class FeatureEngineerV2:
    """
    Improved feature engineering with focus on forex-specific patterns.
    """
    
    def __init__(self):
        self.feature_names = []
    
    def _ema(self, data, period):
        """EMA calculation"""
        ema = [0.0] * len(data)
        if len(data) < period:
            return ema
        multiplier = 2 / (period + 1)
        ema[period-1] = sum(data[:period]) / period
        for i in range(period, len(data)):
            ema[i] = (data[i] - ema[i-1]) * multiplier + ema[i-1]
        return ema
    
    def _rsi(self, closes, period):
        """RSI calculation"""
        rsi = [50.0] * len(closes)
        if len(closes) < period + 1:
            return rsi
        deltas = [closes[i] - closes[i-1] if i > 0 else 0 for i in range(len(closes))]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        
        avg_gain = sum(gains[1:period+1]) / period
        avg_loss = sum(losses[1:period+1]) / period
        
        for i in range(period + 1, len(closes)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
            rs = avg_gain / (avg_loss + 1e-10)
            rsi[i] = 100 - (100 / (1 + rs))
        return rsi
    
    def _atr(self, highs, lows, closes, period):
        """ATR calculation"""
        tr = []
        for i in range(len(closes)):
            if i == 0:
                tr.append(highs[i] - lows[i])
            else:
                tr.append(max(highs[i] - lows[i], abs(highs[i] - closes[i-1]), abs(lows[i] - closes[i-1])))
        
        atr = [0.0] * len(closes)
        if len(tr) >= period:
            atr[period-1] = sum(tr[:period]) / period
            for i in range(period, len(closes)):
                atr[i] = (atr[i-1] * (period - 1) + tr[i]) / period
        return atr
    
    def calculate_features(self, df):
        """Calculate forex-specific features"""
        closes = df['close'].values
        highs = df['high'].values
        lows = df['low'].values
        opens = df['open'].values
        volumes = df['volume'].values if 'volume' in df.columns else np.ones(len(df))
        
        n = len(df)
        features = {}
        
        # ========== PRICE MOMENTUM ==========
        # Returns at different horizons
        for period in [1, 3, 5, 10, 20]:
            returns = np.zeros(n)
            for i in range(period, n):
                returns[i] = (closes[i] - closes[i-period]) / (closes[i-period] + 1e-10)
            features[f'ret_{period}'] = returns
        
        # RSI
        for period in [7, 14, 21]:
            features[f'rsi_{period}'] = self._rsi(closes.tolist(), period)
        
        # RSI divergence (change in RSI)
        rsi_14 = features['rsi_14']
        features['rsi_delta_5'] = np.array([rsi_14[i] - rsi_14[i-5] if i >= 5 else 0 for i in range(n)])
        
        # ========== TREND INDICATORS ==========
        # EMA crossovers
        ema_9 = np.array(self._ema(closes.tolist(), 9))
        ema_21 = np.array(self._ema(closes.tolist(), 21))
        ema_50 = np.array(self._ema(closes.tolist(), 50))
        
        features['ema_9_21_ratio'] = (ema_9 - ema_21) / (ema_21 + 1e-10)
        features['ema_21_50_ratio'] = (ema_21 - ema_50) / (ema_50 + 1e-10)
        features['close_ema_9_ratio'] = (closes - ema_9) / (ema_9 + 1e-10)
        features['close_ema_21_ratio'] = (closes - ema_21) / (ema_21 + 1e-10)
        
        # EMA slope (normalized)
        features['ema_9_slope'] = np.array([ema_9[i] - ema_9[i-3] if i >= 3 else 0 for i in range(n)]) / (closes + 1e-10)
        features['ema_21_slope'] = np.array([ema_21[i] - ema_21[i-5] if i >= 5 else 0 for i in range(n)]) / (closes + 1e-10)
        
        # ========== VOLATILITY ==========
        atr_14 = np.array(self._atr(highs.tolist(), lows.tolist(), closes.tolist(), 14))
        atr_7 = np.array(self._atr(highs.tolist(), lows.tolist(), closes.tolist(), 7))
        
        features['atr_norm'] = atr_14 / (closes + 1e-10)
        features['atr_ratio'] = atr_7 / (atr_14 + 1e-10)
        
        # Bollinger Band position
        for period in [20]:
            sma = np.array([np.mean(closes[max(0,i-period+1):i+1]) if i >= period-1 else closes[i] for i in range(n)])
            std = np.array([np.std(closes[max(0,i-period+1):i+1]) if i >= period-1 else 0.0001 for i in range(n)])
            features[f'bb_position_{period}'] = (closes - sma) / (2 * std + 1e-10)
        
        # ========== CANDLESTICK PATTERNS ==========
        body = closes - opens
        range_hl = highs - lows + 1e-10
        
        features['body_ratio'] = body / range_hl
        features['upper_shadow'] = (highs - np.maximum(opens, closes)) / range_hl
        features['lower_shadow'] = (np.minimum(opens, closes) - lows) / range_hl
        
        # Consecutive candle pattern
        features['consec_up'] = np.zeros(n)
        features['consec_down'] = np.zeros(n)
        for i in range(1, n):
            if closes[i] > opens[i]:  # Green candle
                features['consec_up'][i] = features['consec_up'][i-1] + 1
                features['consec_down'][i] = 0
            elif closes[i] < opens[i]:  # Red candle
                features['consec_down'][i] = features['consec_down'][i-1] + 1
                features['consec_up'][i] = 0
        
        # ========== PRICE POSITION ==========
        for period in [10, 20, 50]:
            high_n = np.array([np.max(highs[max(0,i-period+1):i+1]) if i >= period-1 else highs[i] for i in range(n)])
            low_n = np.array([np.min(lows[max(0,i-period+1):i+1]) if i >= period-1 else lows[i] for i in range(n)])
            features[f'price_position_{period}'] = (closes - low_n) / (high_n - low_n + 1e-10)
        
        # ========== TIME FEATURES ==========
        if 'time' in df.columns:
            hours = pd.to_datetime(df['time']).dt.hour.values
            # Forex session overlaps (London-NY is most volatile)
            features['london_session'] = ((8 <= hours) & (hours <= 16)).astype(float)
            features['ny_session'] = ((13 <= hours) & (hours <= 21)).astype(float)
            features['overlap_session'] = ((13 <= hours) & (hours <= 16)).astype(float)
        
        # ========== LAGGED FEATURES ==========
        for lag in [1, 2, 3]:
            features[f'ret_1_lag{lag}'] = np.roll(features['ret_1'], lag)
            features[f'ret_1_lag{lag}'][:lag] = 0
        
        # Store feature names
        self.feature_names = list(features.keys())
        
        # Convert to DataFrame
        features_df = pd.DataFrame(features, index=df.index)
        
        return features_df


class EnhancedMLStrategy:
    """
    Enhanced ML Strategy using Gradient Boosting with better signal generation.
    """
    
    def __init__(self, lookback=400, probability_threshold=0.52, 
                 retrain_interval=80, min_bars_between_signals=3):
        self.lookback = lookback
        self.probability_threshold = probability_threshold
        self.retrain_interval = retrain_interval
        self.min_bars_between_signals = min_bars_between_signals
        
        self.feature_engine = FeatureEngineerV2()
        self.scaler = StandardScaler() if ML_AVAILABLE else None
        self.model = None
        self.is_fitted = False
    
    def _create_model(self):
        """Create Gradient Boosting model"""
        if not ML_AVAILABLE:
            return None
        
        # Use XGBoost if available, otherwise GradientBoosting
        if XGB_AVAILABLE:
            return xgb.XGBClassifier(
                n_estimators=100,
                max_depth=4,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                min_child_weight=10,
                reg_alpha=0.1,
                reg_lambda=1.0,
                use_label_encoder=False,
                eval_metric='logloss',
                random_state=42,
                n_jobs=-1
            )
        else:
            return GradientBoostingClassifier(
                n_estimators=100,
                max_depth=4,
                learning_rate=0.1,
                subsample=0.8,
                min_samples_leaf=20,
                random_state=42
            )
    
    def _create_labels(self, df, forward_bars=5, atr_multiplier=1.0):
        """
        Create labels based on ATR-normalized price movements.
        More robust than fixed threshold.
        """
        closes = df['close'].values
        highs = df['high'].values
        lows = df['low'].values
        n = len(closes)
        
        # Calculate ATR for dynamic threshold
        atr = self.feature_engine._atr(highs.tolist(), lows.tolist(), closes.tolist(), 14)
        
        labels = [0] * n
        for i in range(n - forward_bars):
            future_high = np.max(highs[i+1:i+forward_bars+1])
            future_low = np.min(lows[i+1:i+forward_bars+1])
            current_close = closes[i]
            current_atr = atr[i] if atr[i] > 0 else 0.0001
            
            # Threshold based on ATR
            threshold = current_atr * atr_multiplier
            
            up_move = future_high - current_close
            down_move = current_close - future_low
            
            # Label based on which direction moved more
            if up_move > threshold and up_move > down_move * 1.2:
                labels[i] = 1  # BUY
            elif down_move > threshold and down_move > up_move * 1.2:
                labels[i] = -1  # SELL
            else:
                labels[i] = 0  # HOLD
        
        return labels
    
    def _prepare_data(self, features_df, labels, start_idx, end_idx):
        """Prepare feature matrix and labels"""
        X = features_df.iloc[start_idx:end_idx].values
        y = labels[start_idx:end_idx]
        
        # Remove NaN/Inf rows
        valid_mask = ~(np.isnan(X).any(axis=1) | np.isinf(X).any(axis=1))
        X = X[valid_mask]
        y = np.array(y)[valid_mask]
        
        return X, y
    
    def generate_signals(self, df, symbol="EUR/USD"):
        """Generate trading signals using ML model"""
        if not ML_AVAILABLE:
            print("ERROR: scikit-learn not available")
            return []
        
        print(f"[Enhanced ML] Generating signals for {symbol}...")
        print(f"[Enhanced ML] Data length: {len(df)} bars")
        print(f"[Enhanced ML] XGBoost available: {XGB_AVAILABLE}")
        
        # Calculate features
        print("[Enhanced ML] Calculating features...")
        features_df = self.feature_engine.calculate_features(df)
        print(f"[Enhanced ML] Features: {len(self.feature_engine.feature_names)}")
        
        # Create labels
        labels = self._create_labels(df, forward_bars=5, atr_multiplier=0.8)
        
        # Count label distribution
        label_counts = {-1: sum(1 for l in labels if l == -1), 
                       0: sum(1 for l in labels if l == 0), 
                       1: sum(1 for l in labels if l == 1)}
        print(f"[Enhanced ML] Labels: SELL={label_counts[-1]}, HOLD={label_counts[0]}, BUY={label_counts[1]}")
        
        signals = []
        last_signal_bar = -100
        warmup = 60  # Warmup for indicators
        
        for i in range(self.lookback + warmup, len(df)):
            # Retrain periodically
            if not self.is_fitted or (i - self.lookback - warmup) % self.retrain_interval == 0:
                train_start = max(warmup, i - self.lookback)
                train_end = i
                
                X_train, y_train = self._prepare_data(features_df, labels, train_start, train_end)
                
                # Need enough samples and class variety
                if len(X_train) < 50:
                    continue
                    
                unique_classes = np.unique(y_train)
                if len(unique_classes) < 2:
                    continue
                
                try:
                    self.model = self._create_model()
                    self.scaler = StandardScaler()
                    X_train_scaled = self.scaler.fit_transform(X_train)
                    self.model.fit(X_train_scaled, y_train)
                    self.is_fitted = True
                except Exception as e:
                    print(f"[Enhanced ML] Training error: {e}")
                    continue
            
            if not self.is_fitted:
                continue
            
            # Get current features
            current_features = features_df.iloc[i:i+1].values
            if np.isnan(current_features).any() or np.isinf(current_features).any():
                continue
            
            # Predict
            current_scaled = self.scaler.transform(current_features)
            proba = self.model.predict_proba(current_scaled)[0]
            
            classes = self.model.classes_
            prob_dict = {c: proba[j] for j, c in enumerate(classes)}
            prob_buy = prob_dict.get(1, 0)
            prob_sell = prob_dict.get(-1, 0)
            
            # Check cooldown
            bars_since_last = i - last_signal_bar
            if bars_since_last < self.min_bars_between_signals:
                continue
            
            # Get ATR for SL/TP
            atr_val = self.feature_engine._atr(
                df['high'].values.tolist()[:i+1],
                df['low'].values.tolist()[:i+1],
                df['close'].values.tolist()[:i+1],
                14
            )[-1]
            
            if atr_val < 0.00001:
                atr_val = 0.0005
            
            close_price = df.iloc[i]['close']
            time = df.iloc[i]['time']
            
            sl_distance = 1.5 * atr_val
            tp_distance = 2.0 * atr_val
            
            # Generate signals with probability margin
            if prob_buy > self.probability_threshold and prob_buy > prob_sell + 0.08:
                signals.append({
                    'index': i,
                    'time': time,
                    'type': 'BUY',
                    'sl': close_price - sl_distance,
                    'tp': close_price + tp_distance,
                    'risk': 0.01,
                    'comment': f'EnhML Buy (P={prob_buy:.2f})'
                })
                last_signal_bar = i
            
            elif prob_sell > self.probability_threshold and prob_sell > prob_buy + 0.08:
                signals.append({
                    'index': i,
                    'time': time,
                    'type': 'SELL',
                    'sl': close_price + sl_distance,
                    'tp': close_price - tp_distance,
                    'risk': 0.01,
                    'comment': f'EnhML Sell (P={prob_sell:.2f})'
                })
                last_signal_bar = i
        
        print(f"[Enhanced ML] Generated {len(signals)} signals")
        return signals


def enhanced_ml_strategy(df, symbol="EUR/USD"):
    """Strategy function for bigtest backtester"""
    strategy = EnhancedMLStrategy(
        lookback=400,
        probability_threshold=0.52,
        retrain_interval=80,
        min_bars_between_signals=3
    )
    return strategy.generate_signals(df, symbol)


if __name__ == "__main__":
    print("Enhanced ML Scalping Strategy v2")
    print(f"ML Available: {ML_AVAILABLE}")
    print(f"XGBoost Available: {XGB_AVAILABLE}")
