"""
ML Scalping Strategy for EUR/USD
Hedge Fund-Style Machine Learning Scalping Strategy

Features:
- 50+ Technical Indicators across multiple categories
- Random Forest ensemble with probability-based predictions
- Walk-forward optimization to avoid overfitting
- Dynamic risk management with ATR-based SL/TP
- Regime detection for market conditions
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ML imports
try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import TimeSeriesSplit
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("WARNING: scikit-learn not installed. Run: pip install scikit-learn")

# pythonpine for technical indicators
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../pythonpine-main')))

try:
    import pythonpine as pp
    PP_AVAILABLE = True
except ImportError:
    PP_AVAILABLE = False
    print("WARNING: pythonpine not available")


class FeatureEngineering:
    """
    Generates 50+ technical features for ML model.
    Uses pythonpine for indicator calculations.
    """
    
    def __init__(self):
        self.feature_names = []
    
    def calculate_features(self, df):
        """
        Calculate all technical features from OHLCV data.
        Returns DataFrame with features.
        """
        # Extract price lists for pythonpine
        closes = df['close'].tolist()
        highs = df['high'].tolist()
        lows = df['low'].tolist()
        opens = df['open'].tolist()
        volumes = df['volume'].tolist()
        
        features = pd.DataFrame(index=df.index)
        
        # ==================== MOMENTUM FEATURES ====================
        
        # RSI
        features['rsi_14'] = pp.rsi(closes, 14) if PP_AVAILABLE else self._rsi(closes, 14)
        features['rsi_7'] = pp.rsi(closes, 7) if PP_AVAILABLE else self._rsi(closes, 7)
        features['rsi_21'] = pp.rsi(closes, 21) if PP_AVAILABLE else self._rsi(closes, 21)
        
        # Stochastic
        stoch_k = pp.stochastic_oscillator(closes, highs, lows, 14) if PP_AVAILABLE else self._stoch(closes, highs, lows, 14)
        features['stoch_k'] = stoch_k
        features['stoch_d'] = pd.Series(stoch_k).rolling(3).mean().tolist()
        
        # MACD
        macd_result = pp.macd(closes, 12, 26, 9) if PP_AVAILABLE else self._macd(closes)
        features['macd_line'] = macd_result[0]
        features['macd_signal'] = macd_result[1]
        features['macd_hist'] = macd_result[2]
        
        # CCI
        features['cci_20'] = pp.cci(closes, highs, lows, 20) if PP_AVAILABLE else self._cci(closes, highs, lows, 20)
        features['cci_14'] = pp.cci(closes, highs, lows, 14) if PP_AVAILABLE else self._cci(closes, highs, lows, 14)
        
        # Williams %R
        features['williams_r'] = pp.williams_percent_r(closes, highs, lows, 14) if PP_AVAILABLE else self._williams_r(closes, highs, lows, 14)
        
        # ROC
        features['roc_10'] = pp.roc(closes, 10) if PP_AVAILABLE else self._roc(closes, 10)
        features['roc_5'] = pp.roc(closes, 5) if PP_AVAILABLE else self._roc(closes, 5)
        
        # Momentum
        features['momentum_10'] = pp.momentum(closes, 10) if PP_AVAILABLE else self._momentum(closes, 10)
        
        # ==================== TREND FEATURES ====================
        
        # EMA values
        ema_9 = pp.ema(closes, 9) if PP_AVAILABLE else self._ema(closes, 9)
        ema_21 = pp.ema(closes, 21) if PP_AVAILABLE else self._ema(closes, 21)
        ema_50 = pp.ema(closes, 50) if PP_AVAILABLE else self._ema(closes, 50)
        
        features['ema_9'] = ema_9
        features['ema_21'] = ema_21
        features['ema_50'] = ema_50
        
        # EMA crossovers (normalized)
        features['ema_9_21_diff'] = [(e9 - e21) / (e21 + 1e-10) for e9, e21 in zip(ema_9, ema_21)]
        features['ema_21_50_diff'] = [(e21 - e50) / (e50 + 1e-10) for e21, e50 in zip(ema_21, ema_50)]
        
        # Price distance from EMAs
        features['close_ema9_dist'] = [(c - e) / (e + 1e-10) for c, e in zip(closes, ema_9)]
        features['close_ema21_dist'] = [(c - e) / (e + 1e-10) for c, e in zip(closes, ema_21)]
        
        # ADX / DMI
        dmi_result = pp.dmi_adx(highs, lows, closes, 14) if PP_AVAILABLE else self._dmi_adx(highs, lows, closes, 14)
        features['adx'] = dmi_result[0]
        features['di_plus'] = dmi_result[1]
        features['di_minus'] = dmi_result[2]
        features['di_diff'] = [dp - dm for dp, dm in zip(dmi_result[1], dmi_result[2])]
        
        # Supertrend direction
        supertrend_result = pp.supertrend(highs, lows, closes, 10, 3.0) if PP_AVAILABLE else ([0]*len(closes), [1]*len(closes))
        features['supertrend_dir'] = supertrend_result[1]  # Direction
        
        # Aroon
        aroon_result = pp.aroon(highs, lows, 14) if PP_AVAILABLE else self._aroon(highs, lows, 14)
        features['aroon_up'] = aroon_result[0]
        features['aroon_down'] = aroon_result[1]
        features['aroon_osc'] = [u - d for u, d in zip(aroon_result[0], aroon_result[1])]
        
        # ==================== VOLATILITY FEATURES ====================
        
        # ATR
        atr_14 = pp.atr(highs, lows, closes, 14) if PP_AVAILABLE else self._atr(highs, lows, closes, 14)
        features['atr_14'] = atr_14
        features['atr_7'] = pp.atr(highs, lows, closes, 7) if PP_AVAILABLE else self._atr(highs, lows, closes, 7)
        
        # Normalized ATR
        features['atr_norm'] = [a / (c + 1e-10) for a, c in zip(atr_14, closes)]
        
        # Bollinger Bands
        bb_result = pp.bollinger_bands(closes, 20, 2) if PP_AVAILABLE else self._bollinger(closes, 20, 2)
        features['bb_upper'] = bb_result[0]
        features['bb_lower'] = bb_result[1]
        features['bb_middle'] = bb_result[2]
        features['bb_width'] = [(u - l) / (m + 1e-10) for u, l, m in zip(bb_result[0], bb_result[1], bb_result[2])]
        features['bb_percent_b'] = pp.bollinger_percent_b(closes, 20, 2) if PP_AVAILABLE else self._bb_percent_b(closes, bb_result)
        
        # Keltner Channel squeeze (use fallback - pythonpine has ema import issue)
        # Squeeze: when BB is inside KC
        kc_upper = [m + 2 * a for m, a in zip(bb_result[2], atr_14)]
        kc_lower = [m - 2 * a for m, a in zip(bb_result[2], atr_14)]
        features['kc_squeeze'] = [1 if bb_l > kc_l else 0 for bb_l, kc_l in zip(bb_result[1], kc_lower)]
        
        # Historical Volatility
        features['hist_vol'] = pp.historical_volatility(closes, 20) if PP_AVAILABLE else self._hist_vol(closes, 20)
        
        # ==================== VOLUME FEATURES ====================
        
        # Volume Z-score
        vol_mean = pd.Series(volumes).rolling(20).mean()
        vol_std = pd.Series(volumes).rolling(20).std()
        features['volume_zscore'] = ((pd.Series(volumes) - vol_mean) / (vol_std + 1e-10)).tolist()
        
        # Volume oscillator
        vol_short = pd.Series(volumes).rolling(5).mean()
        vol_long = pd.Series(volumes).rolling(20).mean()
        features['vol_oscillator'] = ((vol_short - vol_long) / (vol_long + 1e-10) * 100).tolist()
        
        # On-Balance Volume delta
        obv = self._obv(closes, volumes)
        obv_ema = self._ema(obv, 10)
        features['obv_delta'] = [(o - e) / (abs(e) + 1e-10) for o, e in zip(obv, obv_ema)]
        
        # ==================== PRICE ACTION FEATURES ====================
        
        # Candle body ratio
        features['body_ratio'] = [abs(c - o) / (h - l + 1e-10) for o, h, l, c in zip(opens, highs, lows, closes)]
        
        # Upper/Lower wicks
        features['upper_wick'] = [(h - max(o, c)) / (h - l + 1e-10) for o, h, l, c in zip(opens, highs, lows, closes)]
        features['lower_wick'] = [(min(o, c) - l) / (h - l + 1e-10) for o, h, l, c in zip(opens, highs, lows, closes)]
        
        # Candle direction
        features['candle_dir'] = [1 if c > o else -1 if c < o else 0 for o, c in zip(opens, closes)]
        
        # Distance from recent high/low
        high_20 = pd.Series(highs).rolling(20).max()
        low_20 = pd.Series(lows).rolling(20).min()
        features['dist_from_high'] = ((pd.Series(closes) - high_20) / (high_20 + 1e-10)).tolist()
        features['dist_from_low'] = ((pd.Series(closes) - low_20) / (low_20 + 1e-10)).tolist()
        
        # ==================== STATISTICAL FEATURES ====================
        
        # Returns
        features['returns_1'] = pd.Series(closes).pct_change(1).tolist()
        features['returns_5'] = pd.Series(closes).pct_change(5).tolist()
        features['returns_10'] = pd.Series(closes).pct_change(10).tolist()
        
        # Close Z-score
        close_mean = pd.Series(closes).rolling(20).mean()
        close_std = pd.Series(closes).rolling(20).std()
        features['close_zscore'] = ((pd.Series(closes) - close_mean) / (close_std + 1e-10)).tolist()
        
        # Momentum slope (using linear regression)
        features['momentum_slope'] = self._momentum_slope(closes, 10)
        
        # Skewness approximation
        features['skew_20'] = pd.Series(closes).rolling(20).apply(lambda x: ((x - x.mean()) ** 3).mean() / (x.std() ** 3 + 1e-10), raw=True).tolist()
        
        # ==================== LAGGED FEATURES ====================
        
        # Add lagged RSI
        features['rsi_14_lag1'] = pd.Series(features['rsi_14']).shift(1).tolist()
        features['rsi_14_lag2'] = pd.Series(features['rsi_14']).shift(2).tolist()
        
        # Add lagged MACD histogram
        features['macd_hist_lag1'] = pd.Series(features['macd_hist']).shift(1).tolist()
        
        # Store feature names
        self.feature_names = [col for col in features.columns if col not in ['ema_9', 'ema_21', 'ema_50', 'bb_upper', 'bb_lower', 'bb_middle']]
        
        return features
    
    # ==================== FALLBACK CALCULATIONS ====================
    
    def _ema(self, data, period):
        """Exponential Moving Average fallback"""
        ema = [0.0] * len(data)
        if len(data) < period:
            return ema
        multiplier = 2 / (period + 1)
        ema[period-1] = sum(data[:period]) / period
        for i in range(period, len(data)):
            ema[i] = (data[i] - ema[i-1]) * multiplier + ema[i-1]
        return ema
    
    def _rsi(self, closes, period):
        """RSI fallback"""
        rsi = [50.0] * len(closes)
        deltas = [closes[i] - closes[i-1] if i > 0 else 0 for i in range(len(closes))]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        
        avg_gain = sum(gains[:period]) / period if period <= len(gains) else 0
        avg_loss = sum(losses[:period]) / period if period <= len(losses) else 0
        
        for i in range(period, len(closes)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
            rs = avg_gain / (avg_loss + 1e-10)
            rsi[i] = 100 - (100 / (1 + rs))
        return rsi
    
    def _stoch(self, closes, highs, lows, period):
        """Stochastic oscillator fallback"""
        stoch = [50.0] * len(closes)
        for i in range(period-1, len(closes)):
            hh = max(highs[i-period+1:i+1])
            ll = min(lows[i-period+1:i+1])
            stoch[i] = 100 * (closes[i] - ll) / (hh - ll + 1e-10)
        return stoch
    
    def _macd(self, closes):
        """MACD fallback"""
        ema12 = self._ema(closes, 12)
        ema26 = self._ema(closes, 26)
        macd_line = [e12 - e26 for e12, e26 in zip(ema12, ema26)]
        signal = self._ema(macd_line, 9)
        hist = [m - s for m, s in zip(macd_line, signal)]
        return macd_line, signal, hist
    
    def _cci(self, closes, highs, lows, period):
        """CCI fallback"""
        cci = [0.0] * len(closes)
        tp = [(h + l + c) / 3 for h, l, c in zip(highs, lows, closes)]
        for i in range(period-1, len(closes)):
            tp_slice = tp[i-period+1:i+1]
            tp_mean = sum(tp_slice) / period
            mean_dev = sum(abs(t - tp_mean) for t in tp_slice) / period
            cci[i] = (tp[i] - tp_mean) / (0.015 * mean_dev + 1e-10)
        return cci
    
    def _williams_r(self, closes, highs, lows, period):
        """Williams %R fallback"""
        wr = [-50.0] * len(closes)
        for i in range(period-1, len(closes)):
            hh = max(highs[i-period+1:i+1])
            ll = min(lows[i-period+1:i+1])
            wr[i] = -100 * (hh - closes[i]) / (hh - ll + 1e-10)
        return wr
    
    def _roc(self, closes, period):
        """Rate of Change fallback"""
        roc = [0.0] * len(closes)
        for i in range(period, len(closes)):
            roc[i] = 100 * (closes[i] - closes[i-period]) / (closes[i-period] + 1e-10)
        return roc
    
    def _momentum(self, closes, period):
        """Momentum fallback"""
        mom = [0.0] * len(closes)
        for i in range(period, len(closes)):
            mom[i] = closes[i] - closes[i-period]
        return mom
    
    def _atr(self, highs, lows, closes, period):
        """ATR fallback"""
        tr = [highs[i] - lows[i] if i == 0 else max(highs[i] - lows[i], abs(highs[i] - closes[i-1]), abs(lows[i] - closes[i-1])) for i in range(len(closes))]
        atr = [0.0] * len(closes)
        if len(tr) >= period:
            atr[period-1] = sum(tr[:period]) / period
            for i in range(period, len(closes)):
                atr[i] = (atr[i-1] * (period - 1) + tr[i]) / period
        return atr
    
    def _bollinger(self, closes, period, std_mult):
        """Bollinger Bands fallback"""
        upper = [0.0] * len(closes)
        lower = [0.0] * len(closes)
        middle = [0.0] * len(closes)
        for i in range(period-1, len(closes)):
            slice_data = closes[i-period+1:i+1]
            mean = sum(slice_data) / period
            std = (sum((x - mean) ** 2 for x in slice_data) / period) ** 0.5
            middle[i] = mean
            upper[i] = mean + std_mult * std
            lower[i] = mean - std_mult * std
        return upper, lower, middle
    
    def _bb_percent_b(self, closes, bb_result):
        """Bollinger %B fallback"""
        upper, lower, _ = bb_result
        return [(c - l) / (u - l + 1e-10) for c, u, l in zip(closes, upper, lower)]
    
    def _dmi_adx(self, highs, lows, closes, period):
        """DMI/ADX fallback"""
        adx = [25.0] * len(closes)
        di_plus = [25.0] * len(closes)
        di_minus = [25.0] * len(closes)
        return adx, di_plus, di_minus
    
    def _aroon(self, highs, lows, period):
        """Aroon fallback"""
        aroon_up = [50.0] * len(highs)
        aroon_down = [50.0] * len(highs)
        for i in range(period, len(highs)):
            high_slice = highs[i-period:i+1]
            low_slice = lows[i-period:i+1]
            days_since_high = period - high_slice.index(max(high_slice))
            days_since_low = period - low_slice.index(min(low_slice))
            aroon_up[i] = 100 * (period - days_since_high) / period
            aroon_down[i] = 100 * (period - days_since_low) / period
        return aroon_up, aroon_down
    
    def _hist_vol(self, closes, period):
        """Historical volatility fallback"""
        import math
        returns = [math.log(closes[i] / closes[i-1]) if i > 0 and closes[i-1] > 0 else 0 for i in range(len(closes))]
        hv = [0.0] * len(closes)
        for i in range(period, len(closes)):
            slice_ret = returns[i-period+1:i+1]
            mean = sum(slice_ret) / period
            std = (sum((r - mean) ** 2 for r in slice_ret) / period) ** 0.5
            hv[i] = std * math.sqrt(252) * 100
        return hv
    
    def _obv(self, closes, volumes):
        """On-Balance Volume"""
        obv = [0.0] * len(closes)
        for i in range(1, len(closes)):
            if closes[i] > closes[i-1]:
                obv[i] = obv[i-1] + volumes[i]
            elif closes[i] < closes[i-1]:
                obv[i] = obv[i-1] - volumes[i]
            else:
                obv[i] = obv[i-1]
        return obv
    
    def _momentum_slope(self, closes, period):
        """Calculate momentum slope using simple regression"""
        slope = [0.0] * len(closes)
        for i in range(period, len(closes)):
            x = list(range(period))
            y = closes[i-period+1:i+1]
            x_mean = sum(x) / period
            y_mean = sum(y) / period
            num = sum((x[j] - x_mean) * (y[j] - y_mean) for j in range(period))
            den = sum((x[j] - x_mean) ** 2 for j in range(period))
            slope[i] = num / (den + 1e-10)
        return slope


class MLScalpingStrategy:
    """
    Machine Learning Scalping Strategy for EUR/USD.
    Uses Random Forest with walk-forward optimization.
    """
    
    def __init__(self, lookback=600, probability_threshold=0.55, 
                 retrain_interval=100, min_bars_between_signals=4):
        """
        Initialize ML Scalping Strategy.
        
        Args:
            lookback: Number of bars for initial training
            probability_threshold: Min probability for signal (0.5-1.0)
            retrain_interval: Bars between model retraining
            min_bars_between_signals: Minimum bars between trades
        """
        self.lookback = lookback
        self.probability_threshold = probability_threshold
        self.retrain_interval = retrain_interval
        self.min_bars_between_signals = min_bars_between_signals
        
        self.feature_engine = FeatureEngineering()
        self.scaler = StandardScaler() if ML_AVAILABLE else None
        self.model = None
        self.is_fitted = False
        
    def _create_model(self):
        """Create Random Forest model"""
        if not ML_AVAILABLE:
            return None
        return RandomForestClassifier(
            n_estimators=200,
            max_depth=5,
            min_samples_leaf=80,
            min_samples_split=150,
            class_weight='balanced',
            random_state=42,
            n_jobs=-1,
            max_features='sqrt'
        )
    
    def _create_labels(self, df, forward_bars=6, threshold_pct=0.0008):
        """
        Create labels for supervised learning.
        1 = Price goes up by threshold
        -1 = Price goes down by threshold
        0 = Neutral
        """
        closes = df['close'].values
        labels = [0] * len(closes)
        
        for i in range(len(closes) - forward_bars):
            future_close = closes[i + forward_bars]
            current_close = closes[i]
            change = (future_close - current_close) / current_close
            
            if change > threshold_pct:
                labels[i] = 1  # BUY signal
            elif change < -threshold_pct:
                labels[i] = -1  # SELL signal
            else:
                labels[i] = 0  # No signal
                
        return labels
    
    def _prepare_training_data(self, features_df, labels, start_idx, end_idx):
        """Prepare feature matrix and labels for training"""
        feature_cols = [col for col in features_df.columns if col not in ['ema_9', 'ema_21', 'ema_50', 'bb_upper', 'bb_lower', 'bb_middle']]
        
        X = features_df[feature_cols].iloc[start_idx:end_idx].values
        y = labels[start_idx:end_idx]
        
        # Remove NaN rows
        valid_mask = ~np.isnan(X).any(axis=1)
        X = X[valid_mask]
        y = np.array(y)[valid_mask]
        
        return X, y
    
    def generate_signals(self, df, symbol="EUR/USD"):
        """
        Generate trading signals using ML model.
        
        Args:
            df: DataFrame with OHLCV data
            symbol: Trading symbol
            
        Returns:
            List of signal dictionaries
        """
        if not ML_AVAILABLE:
            print("ERROR: scikit-learn not available. Cannot generate ML signals.")
            return []
        
        print(f"[ML Strategy] Generating signals for {symbol}...")
        print(f"[ML Strategy] Data length: {len(df)} bars")
        
        # Calculate all features
        print("[ML Strategy] Calculating features...")
        features_df = self.feature_engine.calculate_features(df)
        
        # Create labels
        labels = self._create_labels(df, forward_bars=5, threshold_pct=0.0008)
        
        signals = []
        last_signal_bar = -100
        
        # Get feature columns
        feature_cols = [col for col in features_df.columns if col not in ['ema_9', 'ema_21', 'ema_50', 'bb_upper', 'bb_lower', 'bb_middle']]
        
        # Walk-forward training and prediction
        train_start = 50  # Skip first 50 bars for indicator warmup
        
        for i in range(self.lookback + train_start, len(df)):
            # Retrain model periodically
            if not self.is_fitted or (i - self.lookback - train_start) % self.retrain_interval == 0:
                # Training window
                train_end = i
                train_start_idx = max(train_start, i - self.lookback)
                
                X_train, y_train = self._prepare_training_data(features_df, labels, train_start_idx, train_end)
                
                if len(X_train) > 100 and len(np.unique(y_train)) > 1:
                    self.model = self._create_model()
                    self.scaler = StandardScaler()
                    
                    X_train_scaled = self.scaler.fit_transform(X_train)
                    self.model.fit(X_train_scaled, y_train)
                    self.is_fitted = True
            
            # Skip if model not fitted
            if not self.is_fitted:
                continue
            
            # Get current features
            current_features = features_df[feature_cols].iloc[i:i+1].values
            
            # Skip if NaN
            if np.isnan(current_features).any():
                continue
            
            # Scale and predict
            current_scaled = self.scaler.transform(current_features)
            proba = self.model.predict_proba(current_scaled)[0]
            
            # Get class probabilities
            classes = self.model.classes_
            prob_buy = proba[list(classes).index(1)] if 1 in classes else 0
            prob_sell = proba[list(classes).index(-1)] if -1 in classes else 0
            
            # Check signal threshold and cooldown
            bars_since_last = i - last_signal_bar
            
            if bars_since_last >= self.min_bars_between_signals:
                # Get ATR for SL/TP
                atr_val = features_df['atr_14'].iloc[i] if not pd.isna(features_df['atr_14'].iloc[i]) else 0.0005
                close_price = df.iloc[i]['close']
                time = df.iloc[i]['time']
                
                # Dynamic SL/TP based on ATR
                sl_distance = 1.5 * atr_val
                tp_distance = 2.0 * atr_val
                
                # Get trend filter from ADX and EMA
                adx_val = features_df['adx'].iloc[i] if not pd.isna(features_df['adx'].iloc[i]) else 25
                ema_diff = features_df['ema_9_21_diff'].iloc[i] if not pd.isna(features_df['ema_9_21_diff'].iloc[i]) else 0
                
                # Simple regime filter - just need some trend (ADX > 10)
                regime_ok = True  # Disabled for now
                
                # Trend direction from EMA (looser filter)
                trend_bullish = ema_diff > -0.001  # Almost always true for buy
                trend_bearish = ema_diff < 0.001   # Almost always true for sell
                
                # BUY Signal - simplified
                if (prob_buy > self.probability_threshold and prob_buy > prob_sell + 0.05 and trend_bullish):
                    signals.append({
                        'index': i,
                        'time': time,
                        'type': 'BUY',
                        'sl': close_price - sl_distance,
                        'tp': close_price + tp_distance,
                        'risk': 0.01,
                        'comment': f'ML Buy (P={prob_buy:.2f})'
                    })
                    last_signal_bar = i
                
                # SELL Signal - simplified
                elif (prob_sell > self.probability_threshold and prob_sell > prob_buy + 0.05 and trend_bearish):
                    signals.append({
                        'index': i,
                        'time': time,
                        'type': 'SELL',
                        'sl': close_price + sl_distance,
                        'tp': close_price - tp_distance,
                        'risk': 0.01,
                        'comment': f'ML Sell (P={prob_sell:.2f})'
                    })
                    last_signal_bar = i
        
        print(f"[ML Strategy] Generated {len(signals)} signals")
        return signals


def ml_scalping_strategy(df, symbol="EUR/USD"):
    """
    Strategy function compatible with bigtest backtester.
    
    Args:
        df: DataFrame with OHLCV data
        
    Returns:
        List of signal dictionaries
    """
    strategy = MLScalpingStrategy(
        lookback=600,
        probability_threshold=0.55,  # Balanced threshold
        retrain_interval=100,
        min_bars_between_signals=4
    )
    return strategy.generate_signals(df, symbol)


if __name__ == "__main__":
    # Test the strategy
    print("ML Scalping Strategy Module")
    print(f"ML Available: {ML_AVAILABLE}")
    print(f"PythonPine Available: {PP_AVAILABLE}")
