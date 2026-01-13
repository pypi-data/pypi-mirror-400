"""
UT Bot Strategy Backtest
Tests the UT Bot ATR Trailing Stop strategy on EURUSD and GBPUSD

This implements the ORIGINAL UT Bot dual trailing stop logic from utbot.py
with corrected indexing for backtesting.
"""
import pandas as pd
import numpy as np
from backtester import Backtester
from data_engine import DataEngine
from trade_manager import TradeManager
from reporter import Reporter
import os
from datetime import datetime, timedelta

# --- ATR Calculation ---
def calculate_atr(df, period=14):
    """Calculate Average True Range"""
    high = df['high']
    low = df['low']
    close = df['close']
    
    # True Range components
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    
    # True Range
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    # ATR (Simple Moving Average of TR)
    atr = tr.rolling(window=period).mean()
    return atr

# --- UT Bot Strategy (Original Logic) ---
def utbot_strategy_original(df, symbol, 
                            sell_sensitivity=2, sell_atr_period=14,
                            buy_sensitivity=2, buy_atr_period=14,
                            volume_filter_enabled=False,
                            min_bars_between_signals=5):
    """
    UT Bot ATR Trailing Stop Strategy - Original Logic
    
    This replicates the EXACT logic from utbot.py:
    - Two independent trailing stops (buy and sell)
    - Each uses ATR * sensitivity as the distance
    - Signals on crossover
    
    Key Fix: Use reasonable ATR periods (14 for both instead of 1 and 300)
    and add signal throttling to prevent whipsawing.
    """
    print(f"Calculating UT Bot indicators for {symbol}...")
    
    # Calculate ATRs
    df['atr_sell'] = calculate_atr(df, sell_atr_period)
    df['atr_buy'] = calculate_atr(df, buy_atr_period)
    
    # Volume Oscillator
    df['vol_short'] = df['volume'].rolling(5).mean()
    df['vol_long'] = df['volume'].rolling(20).mean()
    df['vol_osc'] = ((df['vol_short'] - df['vol_long']) / df['vol_long']) * 100
    
    signals = []
    
    # Start from where ATRs are valid
    start_idx = max(sell_atr_period, buy_atr_period) + 1
    
    # Initialize trailing stops
    prev_sell_trailing = df.iloc[start_idx]['close']
    prev_buy_trailing = df.iloc[start_idx]['close']
    
    # Track last signal bar for throttling
    last_signal_bar = -100
    
    for i in range(start_idx, len(df)):
        src = df.iloc[i]['close']
        src_prev = df.iloc[i-1]['close']
        
        atr_sell = df.iloc[i-1]['atr_sell']
        atr_buy = df.iloc[i-1]['atr_buy']
        
        if pd.isna(atr_sell) or pd.isna(atr_buy) or atr_sell == 0 or atr_buy == 0:
            continue
            
        sell_loss = sell_sensitivity * atr_sell
        buy_loss = buy_sensitivity * atr_buy
        
        # --- SELL Trailing Stop Logic (from utbot.py) ---
        if src > prev_sell_trailing and src_prev > prev_sell_trailing:
            sell_trailing = max(prev_sell_trailing, src - sell_loss)
        elif src < prev_sell_trailing and src_prev < prev_sell_trailing:
            sell_trailing = min(prev_sell_trailing, src + sell_loss)
        else:
            sell_trailing = src - sell_loss if src > prev_sell_trailing else src + sell_loss
        
        # --- BUY Trailing Stop Logic (from utbot.py) ---
        if src > prev_buy_trailing and src_prev > prev_buy_trailing:
            buy_trailing = max(prev_buy_trailing, src - buy_loss)
        elif src < prev_buy_trailing and src_prev < prev_buy_trailing:
            buy_trailing = min(prev_buy_trailing, src + buy_loss)
        else:
            buy_trailing = src - buy_loss if src > prev_buy_trailing else src + buy_loss
        
        # --- Crossover Detection (from utbot.py) ---
        sell_below = sell_trailing > src and prev_sell_trailing <= src_prev
        buy_above = src > buy_trailing and src_prev <= prev_buy_trailing
        
        # Volume filter
        vol_osc = df.iloc[i]['vol_osc']
        if volume_filter_enabled:
            vol_filter = vol_osc > 0 if pd.notna(vol_osc) else True
        else:
            vol_filter = True
        
        # --- Generate Signals ---
        time = df.iloc[i]['time']
        close = df.iloc[i]['close']
        
        # Signal throttling - minimum bars between signals
        bars_since_last = i - last_signal_bar
        
        # Use ATR-based SL/TP with positive R:R (1.5:2)
        sl_atr = max(atr_sell, atr_buy)
        sl_distance = 1.5 * sl_atr
        tp_distance = 2.0 * sl_atr
        
        # SELL Signal
        if src < sell_trailing and sell_below and vol_filter and bars_since_last >= min_bars_between_signals:
            sl = close + sl_distance
            tp = close - tp_distance
            signals.append({
                'index': i,
                'time': time,
                'type': 'SELL',
                'sl': sl,
                'tp': tp,
                'risk': 0.01,
                'comment': f'UT Bot Sell'
            })
            last_signal_bar = i
        
        # BUY Signal  
        elif src > buy_trailing and buy_above and vol_filter and bars_since_last >= min_bars_between_signals:
            sl = close - sl_distance
            tp = close + tp_distance
            signals.append({
                'index': i,
                'time': time,
                'type': 'BUY',
                'sl': sl,
                'tp': tp,
                'risk': 0.01,
                'comment': f'UT Bot Buy'
            })
            last_signal_bar = i
        
        # Update previous trailing stops
        prev_sell_trailing = sell_trailing
        prev_buy_trailing = buy_trailing
    
    print(f"Generated {len(signals)} signals for {symbol}.")
    return signals


# --- Simpler Trend-Following Strategy (for comparison) ---
def ema_crossover_strategy(df, symbol, fast_period=9, slow_period=21):
    """
    Simple EMA Crossover strategy for comparison baseline.
    """
    print(f"Calculating EMA indicators for {symbol}...")
    
    df['ema_fast'] = df['close'].ewm(span=fast_period, adjust=False).mean()
    df['ema_slow'] = df['close'].ewm(span=slow_period, adjust=False).mean()
    df['atr'] = calculate_atr(df, 14)
    
    signals = []
    start_idx = slow_period + 1
    last_signal_bar = -100
    
    for i in range(start_idx, len(df)):
        ema_fast = df.iloc[i]['ema_fast']
        ema_fast_prev = df.iloc[i-1]['ema_fast']
        ema_slow = df.iloc[i]['ema_slow']
        ema_slow_prev = df.iloc[i-1]['ema_slow']
        
        atr_val = df.iloc[i-1]['atr']
        if pd.isna(atr_val):
            continue
        
        time = df.iloc[i]['time']
        close = df.iloc[i]['close']
        
        # Golden Cross: Fast EMA crosses above Slow EMA
        if ema_fast_prev <= ema_slow_prev and ema_fast > ema_slow:
            if i - last_signal_bar >= 10:
                signals.append({
                    'index': i,
                    'time': time,
                    'type': 'BUY',
                    'sl': close - 2 * atr_val,
                    'tp': close + 3 * atr_val,
                    'risk': 0.01,
                    'comment': 'EMA Golden Cross'
                })
                last_signal_bar = i
        
        # Death Cross: Fast EMA crosses below Slow EMA
        elif ema_fast_prev >= ema_slow_prev and ema_fast < ema_slow:
            if i - last_signal_bar >= 10:
                signals.append({
                    'index': i,
                    'time': time,
                    'type': 'SELL',
                    'sl': close + 2 * atr_val,
                    'tp': close - 3 * atr_val,
                    'risk': 0.01,
                    'comment': 'EMA Death Cross'
                })
                last_signal_bar = i
    
    print(f"Generated {len(signals)} signals for {symbol}.")
    return signals


def run_utbot_test(symbol, start_date, end_date, timeframe="1h", strategy="utbot"):
    """Run UT Bot backtest for a symbol"""
    print(f"\n{'='*60}")
    print(f"BACKTEST: {symbol} - {strategy.upper()}")
    print(f"Period: {start_date} to {end_date}")
    print(f"Timeframe: {timeframe}")
    print(f"{'='*60}")
    
    data_engine = DataEngine()
    trade_manager = TradeManager()
    backtester = Backtester(data_engine, trade_manager)
    
    # Strategy selection
    def strategy_wrapper(df):
        if strategy == "utbot":
            return utbot_strategy_original(
                df, symbol,
                sell_sensitivity=2, sell_atr_period=14,
                buy_sensitivity=2, buy_atr_period=14,
                volume_filter_enabled=False,
                min_bars_between_signals=5
            )
        else:
            return ema_crossover_strategy(df, symbol)
    
    try:
        backtester.run(
            symbol=symbol,
            timeframe=timeframe,
            start_str=start_date,
            end_str=end_date,
            strategy_func=strategy_wrapper,
            initial_capital=10000,
            commission_rate=0.00002
        )
        
        # Generate Report
        reporter = Reporter(trade_manager)
        safe_symbol = symbol.replace("/", "_")
        report_file = f"report_UTBOT_{safe_symbol}_{timeframe}.html"
        reporter.generate_html_report(report_file, start_date, end_date)
        
        # Print Summary
        closed_trades = trade_manager.get_closed_trades()
        total_pnl = trade_manager.get_total_pnl()
        
        wins = [t for t in closed_trades if t.pnl > 0]
        losses = [t for t in closed_trades if t.pnl <= 0]
        
        print(f"\n--- RESULTS for {symbol} ---")
        print(f"Total Trades: {len(closed_trades)}")
        print(f"Wins: {len(wins)} | Losses: {len(losses)}")
        if closed_trades:
            win_rate = len(wins) / len(closed_trades) * 100
            print(f"Win Rate: {win_rate:.1f}%")
        print(f"Total PnL: ${total_pnl:.2f}")
        print(f"Report: {report_file}")
        
        return {
            'symbol': symbol,
            'trades': len(closed_trades),
            'wins': len(wins),
            'losses': len(losses),
            'pnl': total_pnl,
            'report': report_file
        }
        
    except Exception as e:
        print(f"ERROR running test for {symbol}: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    # Last Month: November 6, 2025 to December 6, 2025
    start_date = "2025-11-06"
    end_date = "2025-12-06"
    
    print("\n" + "="*70)
    print("UT BOT STRATEGY BACKTEST - CORRECTED")
    print("="*70)
    print(f"Test Period: {start_date} to {end_date}")
    print("Pairs: EUR/USD, GBP/USD")
    print("Timeframe: 1H (for less noise)")
    print("Parameters: ATR 14, Sensitivity 2, Min 5 bars between signals")
    print("="*70)
    
    results = []
    
    # Test EUR/USD on 1H (less noisy than 15m)
    result = run_utbot_test("EUR/USD", start_date, end_date, "1h", "utbot")
    if result:
        results.append(result)
    
    # Test GBP/USD on 1H
    result = run_utbot_test("GBP/USD", start_date, end_date, "1h", "utbot")
    if result:
        results.append(result)
    
    # Print Combined Summary
    if results:
        print("\n" + "="*70)
        print("COMBINED RESULTS")
        print("="*70)
        
        total_trades = sum(r['trades'] for r in results)
        total_wins = sum(r['wins'] for r in results)
        total_pnl = sum(r['pnl'] for r in results)
        
        print(f"{'Symbol':<12} {'Trades':<10} {'Wins':<8} {'Losses':<8} {'Win %':<10} {'PnL':<12}")
        print("-" * 60)
        
        for r in results:
            win_pct = (r['wins'] / r['trades'] * 100) if r['trades'] > 0 else 0
            print(f"{r['symbol']:<12} {r['trades']:<10} {r['wins']:<8} {r['losses']:<8} {win_pct:<10.1f} ${r['pnl']:<11.2f}")
        
        print("-" * 60)
        total_win_pct = (total_wins / total_trades * 100) if total_trades > 0 else 0
        print(f"{'TOTAL':<12} {total_trades:<10} {total_wins:<8} {total_trades - total_wins:<8} {total_win_pct:<10.1f} ${total_pnl:<11.2f}")
        print("="*70)
