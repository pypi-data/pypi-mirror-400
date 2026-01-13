import sys
import os
import pandas as pd
import dukascopy_python as dp
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional
import hashlib
from dukascopy_patch import apply_patch
import alpaca_trade_api as tradeapi
import ccxt
import time
import requests

# Apply patch on import
apply_patch()

class DataEngine:
    def __init__(self, cache_dir="data_cache"):
        self.cache_dir = cache_dir
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        # Batch tick cache for performance
        self.tick_batch_cache: Dict[str, pd.DataFrame] = {}
    
    def prefetch_ticks_for_range(self, symbol: str, start_dt: datetime, end_dt: datetime) -> Dict[str, pd.DataFrame]:
        """
        Pre-fetch all tick data for a date range into memory cache.
        Reduces I/O bottleneck during TP/SL resolution.
        
        Args:
            symbol: Trading symbol
            start_dt: Start datetime
            end_dt: End datetime
            
        Returns:
            Dict mapping candle timestamp (str) -> tick DataFrame
        """
        cache_key = f"{symbol}_{start_dt.strftime('%Y%m%d%H%M')}_{end_dt.strftime('%Y%m%d%H%M')}"
        
        # Check if already loaded
        if cache_key in self.tick_batch_cache:
            return self.tick_batch_cache
        
        print(f"[DataEngine] Pre-fetching ticks for {symbol} ({start_dt} to {end_dt})...")
        
        # Fetch full range at once
        try:
            full_ticks = self.get_dukascopy_ticks(symbol, start_dt, end_dt)
        except Exception as e:
            print(f"[DataEngine] Batch tick fetch error: {e}")
            return {}
        
        if full_ticks.empty:
            return {}
        
        # Group by minute for fast lookup
        full_ticks['minute'] = full_ticks['time'].dt.floor('1min')
        
        grouped_cache = {}
        for minute, group in full_ticks.groupby('minute'):
            grouped_cache[str(minute)] = group.reset_index(drop=True)
        
        self.tick_batch_cache = grouped_cache
        print(f"[DataEngine] Cached {len(grouped_cache)} minute-groups of tick data")
        
        return grouped_cache
    
    def get_cached_ticks(self, candle_time) -> Optional[pd.DataFrame]:
        """
        Get cached ticks for a specific candle time.
        Call prefetch_ticks_for_range first.
        """
        cache_key = str(candle_time)
        return self.tick_batch_cache.get(cache_key)

    def get_alpaca_candles(self, symbol, timeframe, start_str, end_str):
        print(f"[DataEngine] Fetching Alpaca candles for {symbol} ({timeframe})...")
        try:
            api = tradeapi.REST()
            # Map timeframe
            tf_map = {'1m': '1Min', '5m': '5Min', '15m': '15Min', '1h': '1Hour', '1d': '1Day'}
            tf = tf_map.get(timeframe, '1Min')
            
            start_dt = pd.to_datetime(start_str).tz_localize('UTC') if pd.to_datetime(start_str).tz is None else pd.to_datetime(start_str)
            end_dt = pd.to_datetime(end_str).tz_localize('UTC') if pd.to_datetime(end_str).tz is None else pd.to_datetime(end_str)
            
            bars = api.get_bars(symbol, tf, start=start_dt.isoformat(), end=end_dt.isoformat()).df
            
            if bars.empty:
                return pd.DataFrame()
                
            bars = bars.reset_index()
            # Alpaca cols: timestamp, open, high, low, close, volume, trade_count, vwap
            df = pd.DataFrame({
                'time': bars['timestamp'],
                'open': bars['open'],
                'high': bars['high'],
                'low': bars['low'],
                'close': bars['close'],
                'volume': bars['volume']
            })
            
            # Ensure UTC
            if df['time'].dt.tz is None:
                df['time'] = df['time'].dt.tz_localize('UTC')
            else:
                df['time'] = df['time'].dt.tz_convert('UTC')
                
            return df.sort_values('time').reset_index(drop=True)
            
        except Exception as e:
            print(f"[DataEngine] Error fetching Alpaca candles: {e}")
            return pd.DataFrame()

    def get_binance_candles(self, symbol, timeframe, start_str, end_str):
        print(f"[DataEngine] Fetching Binance candles for {symbol} ({timeframe})...")
        try:
            # Normalize Symbol: BTC/USD -> BTCUSDT
            bn_symbol = symbol.replace("/", "").replace("USD", "USDT") if "USDT" not in symbol else symbol.replace("/", "")
            
            base_url = "https://api.binance.com/api/v3/klines"
            
            start_dt = pd.to_datetime(start_str)
            end_dt = pd.to_datetime(end_str)
            
            start_ts = int(start_dt.timestamp() * 1000)
            end_ts = int(end_dt.timestamp() * 1000)
            current_start = start_ts
            
            all_klines = []
            
            while current_start < end_ts:
                params = {
                    'symbol': bn_symbol,
                    'interval': timeframe,
                    'startTime': current_start,
                    'endTime': end_ts,
                    'limit': 1000
                }
                
                resp = requests.get(base_url, params=params)
                if resp.status_code != 200:
                    print(f"Error: {resp.text}")
                    break
                    
                klines = resp.json()
                if not klines:
                    break
                    
                all_klines.extend(klines)
                
                # Update current_start
                last_time = klines[-1][0]
                if last_time == current_start:
                    current_start += 1
                else:
                    current_start = last_time + 1
                    
                if current_start >= end_ts:
                    break
                    
                time.sleep(0.1)
                
            if not all_klines:
                return pd.DataFrame()
                
            df = pd.DataFrame(all_klines, columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'q_vol', 'trades', 't_base', 't_quote', 'ignore'])
            df['time'] = pd.to_datetime(df['open_time'], unit='ms', utc=True)
            df['open'] = df['open'].astype(float)
            df['high'] = df['high'].astype(float)
            df['low'] = df['low'].astype(float)
            df['close'] = df['close'].astype(float)
            df['volume'] = df['volume'].astype(float)
            
            df = df[['time', 'open', 'high', 'low', 'close', 'volume']]
            
            # Filter range
            df = df[(df['time'] >= start_dt.replace(tzinfo=timezone.utc)) & (df['time'] <= end_dt.replace(tzinfo=timezone.utc))]
            
            return df.sort_values('time').reset_index(drop=True)
            
        except Exception as e:
            print(f"[DataEngine] Error fetching Binance candles: {e}")
            return pd.DataFrame()

    def get_candles(self, symbol, timeframe, start_str, end_str):
        """
        Fetch OHLCV data with routing.
        """
        if symbol in ["AAPL", "TSLA"]:
            return self.get_alpaca_candles(symbol, timeframe, start_str, end_str)
        elif "BTC" in symbol or "ETH" in symbol:
            return self.get_binance_candles(symbol, timeframe, start_str, end_str)
        
        # Default to finda (Dukascopy wrapper)
        # Re-import finda here to avoid breaking if not needed
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../finda')))
        from finda.ohlcv_fetcher import fetch_unified_ohclv
        
        print(f"[DataEngine] Fetching candles for {symbol} ({timeframe})...")
        try:
            res = fetch_unified_ohclv(
                symbol=symbol,
                user_tf=timeframe,
                user_start=start_str,
                user_end=end_str
            )
            
            if not res:
                print(f"[DataEngine] No data returned for {symbol}.")
                return pd.DataFrame()

            print(f"[DataEngine] Data fetched successfully. Length: {len(res[5])}")
            o, h, l, c, v, t = res
            
            df = pd.DataFrame({
                'time': pd.to_datetime(t),
                'open': o,
                'high': h,
                'low': l,
                'close': c,
                'volume': v
            })
            return df.sort_values('time').reset_index(drop=True)
            
        except Exception as e:
            print(f"[DataEngine] Error fetching candles: {e}")
            return pd.DataFrame()

            return df_synthetic

    def get_alpaca_ticks(self, symbol, start_dt, end_dt):
        """
        Fetch Tick data from Alpaca (Trades).
        """
        # Cache Key
        cache_filename = f"ALPACA_{symbol}_{start_dt.strftime('%Y%m%d%H%M')}_{end_dt.strftime('%Y%m%d%H%M')}.parquet"
        cache_path = os.path.join(self.cache_dir, cache_filename)
        
        if os.path.exists(cache_path):
            return pd.read_parquet(cache_path)
            
        print(f"[DataEngine] Fetching Alpaca ticks for {symbol}...")
        
        try:
            # Initialize API
            # Assumes env vars APCA_API_KEY_ID and APCA_API_SECRET_KEY are set
            # If not, this will likely fail or need hardcoded keys (not recommended)
            api = tradeapi.REST() 
            
            # Fetch Trades
            # Alpaca expects RFC3339 strings
            trades = api.get_trades(
                symbol, 
                start=start_dt.isoformat(), 
                end=end_dt.isoformat(),
                limit=10000 # Max limit, might need pagination for large ranges
            ).df
            
            if trades.empty:
                return pd.DataFrame()
                
            # Process
            # Alpaca returns index as timestamp (tz-aware)
            trades = trades.reset_index()
            # Columns: timestamp, exchange, price, size, id, conditions, tape
            
            df = pd.DataFrame({
                'time': trades['timestamp'],
                'price': trades['price'],
                'volume': trades['size']
            })
            
            # Ensure UTC
            if df['time'].dt.tz is None:
                df['time'] = df['time'].dt.tz_localize('UTC')
            else:
                df['time'] = df['time'].dt.tz_convert('UTC')
                
            # Save to Cache
            df.to_parquet(cache_path)
            return df
            
        except Exception as e:
            print(f"[DataEngine] Error fetching Alpaca ticks: {e}")
            return pd.DataFrame()

    def get_binance_ticks(self, symbol, start_dt, end_dt):
        """
        Fetch Tick data from Binance (AggTrades) using direct API.
        """
        # Normalize Symbol: BTC/USD -> BTCUSDT
        bn_symbol = symbol.replace("/", "").replace("USD", "USDT") if "USDT" not in symbol else symbol.replace("/", "")
        
        # Cache Key
        safe_symbol = bn_symbol
        cache_filename = f"BINANCE_{safe_symbol}_{start_dt.strftime('%Y%m%d%H%M')}_{end_dt.strftime('%Y%m%d%H%M')}.parquet"
        cache_path = os.path.join(self.cache_dir, cache_filename)
        
        if os.path.exists(cache_path):
            return pd.read_parquet(cache_path)
            
        print(f"[DataEngine] Fetching Binance ticks for {bn_symbol}...")
        
        try:
            base_url = "https://api.binance.com/api/v3/aggTrades"
            
            all_trades = []
            start_ts = int(start_dt.timestamp() * 1000)
            end_ts = int(end_dt.timestamp() * 1000)
            current_start = start_ts
            
            while current_start < end_ts:
                params = {
                    'symbol': bn_symbol,
                    'startTime': current_start,
                    'endTime': end_ts,
                    'limit': 1000
                }
                
                resp = requests.get(base_url, params=params)
                if resp.status_code != 200:
                    print(f"Error: {resp.text}")
                    break
                    
                trades = resp.json()
                if not trades:
                    break
                    
                all_trades.extend(trades)
                
                # Update current_start to last trade time + 1ms
                last_time = trades[-1]['T']
                if last_time == current_start:
                    # Avoid infinite loop
                    current_start += 1
                else:
                    current_start = last_time + 1
                    
                if current_start >= end_ts:
                    break
                    
                time.sleep(0.1)
            
            if not all_trades:
                return pd.DataFrame()
            
            df = pd.DataFrame(all_trades)
            df = df.rename(columns={'T': 'time', 'p': 'price', 'q': 'volume'})
            df['time'] = pd.to_datetime(df['time'], unit='ms', utc=True)
            df['price'] = df['price'].astype(float)
            df['volume'] = df['volume'].astype(float)
            
            df = df[['time', 'price', 'volume']]
            
            # Save to Cache
            df.to_parquet(cache_path)
            return df
            
        except Exception as e:
            print(f"[DataEngine] Error fetching Binance ticks: {e}")
            return pd.DataFrame()

    def get_ticks(self, symbol, start_str, end_str):
        """
        Fetch Tick data with routing to provider.
        """
        # Parse Dates
        try:
            start_dt = datetime.strptime(start_str, "%Y-%m-%d-%H-%M-%S").replace(tzinfo=timezone.utc)
            end_dt = datetime.strptime(end_str, "%Y-%m-%d-%H-%M-%S").replace(tzinfo=timezone.utc)
        except ValueError:
            start_dt = pd.to_datetime(start_str).to_pydatetime().replace(tzinfo=timezone.utc)
            end_dt = pd.to_datetime(end_str).to_pydatetime().replace(tzinfo=timezone.utc)

        # Routing
        if symbol in ["AAPL", "TSLA"]:
            return self.get_alpaca_ticks(symbol, start_dt, end_dt)
        elif "BTC" in symbol or "ETH" in symbol:
            return self.get_binance_ticks(symbol, start_dt, end_dt)
        else:
            # Default to Dukascopy (Forex)
            return self.get_dukascopy_ticks(symbol, start_dt, end_dt)

    def get_dukascopy_ticks(self, symbol, start_dt, end_dt):
        """
        Fetch Tick data using direct dukascopy_python integration with Caching.
        """
        # 1. Normalize Symbol (Dukascopy uses 'EUR/USD' apparently)
        # dk_symbol = symbol.replace("/", "").upper()
        dk_symbol = symbol.upper()
        
        # 3. Check Cache
        safe_symbol = dk_symbol.replace("/", "_")
        cache_filename = f"{safe_symbol}_{start_dt.strftime('%Y%m%d%H%M')}_{end_dt.strftime('%Y%m%d%H%M')}.parquet"
        cache_path = os.path.join(self.cache_dir, cache_filename)
        
        if os.path.exists(cache_path):
            # print(f"[DataEngine] Loading ticks from cache: {cache_filename}")
            return pd.read_parquet(cache_path)

        # 4. Fetch from API
        try:
            # Fetch BID
            df = dp.fetch(
                instrument=dk_symbol, 
                interval=dp.INTERVAL_TICK, 
                offer_side=dp.OFFER_SIDE_BID, 
                start=start_dt, 
                end=end_dt
            )
            
            if df.empty:
                return pd.DataFrame()
                
            # Standardize Columns
            df = df.reset_index()
            df.columns = [c.lower() for c in df.columns]
            
            if 'timestamp' in df.columns:
                df = df.rename(columns={'timestamp': 'time'})
            
            price_col = next((c for c in df.columns if 'bid' in c and 'vol' not in c), 'close')
            vol_col = next((c for c in df.columns if 'vol' in c), 'volume')
            
            df = df.rename(columns={price_col: 'price', vol_col: 'volume'})
            df = df[['time', 'price', 'volume']]
            
            # 5. Save to Cache
            df.to_parquet(cache_path)
            
            return df
            
        except Exception as e:
            print(f"[DataEngine] Error fetching ticks: {e}. Generating synthetic ticks from candles...")
            # Fallback: Generate Synthetic Ticks from 1m Candles
            # We need to pass strings to get_candles as per signature
            start_str = start_dt.strftime("%Y-%m-%d-%H-%M-%S")
            end_str = end_dt.strftime("%Y-%m-%d-%H-%M-%S")
            
            candles = self.get_candles(symbol, "1m", start_str, end_str)
            if candles.empty:
                return pd.DataFrame()
                
            synthetic_ticks = []
            for _, row in candles.iterrows():
                t = row['time']
                synthetic_ticks.append({'time': t, 'price': row['open'], 'volume': row['volume'] / 4})
                synthetic_ticks.append({'time': t + timedelta(seconds=15), 'price': row['low'], 'volume': row['volume'] / 4})
                synthetic_ticks.append({'time': t + timedelta(seconds=30), 'price': row['high'], 'volume': row['volume'] / 4})
                synthetic_ticks.append({'time': t + timedelta(seconds=45), 'price': row['close'], 'volume': row['volume'] / 4})
                
            df_synthetic = pd.DataFrame(synthetic_ticks)
            
            # Save to Cache
            if not df_synthetic.empty:
                df_synthetic.to_parquet(cache_path)
                
            return df_synthetic
