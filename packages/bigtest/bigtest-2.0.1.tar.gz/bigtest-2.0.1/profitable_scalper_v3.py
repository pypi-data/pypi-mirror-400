"""
Profitable Scalping Strategy V3 - Ultra Aggressive
Maximize trade frequency with tight filters
"""

from backtester_v2 import BacktestEngine
from backtest_config import BacktestConfig
from datetime import datetime, timedelta
import numpy as np

print('=' * 80)
print('PROFITABLE SCALPER V3 - ULTRA AGGRESSIVE')
print('=' * 80)
print()

config = BacktestConfig(
    symbol='EUR/USD',
    timeframe='1m',
    start_date=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
    end_date=datetime.now().strftime('%Y-%m-%d'),
    initial_capital=1000,
    leverage=300,
    risk_per_trade=0.02,  # 2% risk per trade for more aggression
    max_pyramiding=5,     # Allow 5 concurrent trades
    slippage_model='fixed',
    slippage_pips=0.1,
    commission_per_lot=5.0,
    spread_pips=0.2,
    assume_worst_case=False,
    trade_sessions=['london', 'newyork']
)

print(f'Configuration:')
print(f'  Capital: ${config.initial_capital} x {config.leverage}:1')
print(f'  Risk/Trade: {config.risk_per_trade*100}%')
print(f'  Max Concurrent: {config.max_pyramiding}')
print()

def ultra_aggressive_scalper(df):
    """
    Ultra-aggressive micro scalper:
    - Very tight TP (1 pip) and SL (1 pip) for 1:1 R:R
    - High frequency (signal every 2 bars if conditions met)
    - Multiple positions allowed
    - Volume/ATR filter for volatility
    """
    signals = []
    pip = 0.0001
    
    tp_pips = 1.0  # 1 pip TP
    sl_pips = 1.0  # 1 pip SL (1:1 R:R)
    
    closes = df['close'].values
    opens = df['open'].values
    highs = df['high'].values
    lows = df['low'].values
    n = len(df)
    
    # Indicators
    def ema(data, period):
        result = np.zeros(len(data))
        if len(data) < period:
            return result
        result[:period] = np.mean(data[:period])
        mult = 2 / (period + 1)
        for i in range(period, len(data)):
            result[i] = (data[i] - result[i-1]) * mult + result[i-1]
        return result
    
    def atr(high, low, close, period=14):
        result = np.zeros(len(high))
        for i in range(1, len(high)):
            hl = high[i] - low[i]
            hc = abs(high[i] - close[i-1])
            lc = abs(low[i] - close[i-1])
            tr = max(hl, hc, lc)
            if i >= period:
                result[i] = np.mean([max(high[j]-low[j], abs(high[j]-close[j-1]), 
                                        abs(low[j]-close[j-1])) for j in range(i-period, i)])
            else:
                result[i] = tr
        return result
    
    ema_fast = ema(closes, 3)
    ema_slow = ema(closes, 8)
    atr_vals = atr(highs, lows, closes, 5)
    
    last_signal_bar = -2
    
    for i in range(10, n):
        if i - last_signal_bar < 2:  # Min 2 bars between signals
            continue
        
        close = closes[i]
        curr_atr = atr_vals[i]
        
        # Need minimum volatility (0.5 pip ATR)
        if curr_atr < 0.00005:
            continue
        
        # Scalping conditions
        uptrend = ema_fast[i] > ema_slow[i]
        downtrend = ema_fast[i] < ema_slow[i]
        
        # Strong momentum candle
        body = abs(close - opens[i])
        range_size = highs[i] - lows[i]
        bullish_candle = close > opens[i] and body > range_size * 0.6
        bearish_candle = close < opens[i] and body > range_size * 0.6
        
        # Price making new local high/low
        if uptrend and bullish_candle and close > max(closes[i-3:i]):
            signals.append({
                'index': i,
                'time': df.iloc[i]['time'],
                'type': 'BUY',
                'tp': close + tp_pips * pip,
                'sl': close - sl_pips * pip,
                'risk': 0.02
            })
            last_signal_bar = i
            
        elif downtrend and bearish_candle and close < min(closes[i-3:i]):
            signals.append({
                'index': i,
                'time': df.iloc[i]['time'],
                'type': 'SELL',
                'tp': close - tp_pips * pip,
                'sl': close + sl_pips * pip,
                'risk': 0.02
            })
            last_signal_bar = i
    
    print(f'[Ultra Aggressive] Generated {len(signals)} signals')
    return signals


# Run backtest
print('Running 1-month backtest...')
engine = BacktestEngine(config)
metrics = engine.run(ultra_aggressive_scalper)

# Daily analysis
trades_df = engine.get_trades_df()
if not trades_df.empty:
    trades_df['date'] = trades_df['exit_time'].dt.date
    daily_pnl = trades_df.groupby('date')['pnl'].sum()
    daily_trades = trades_df.groupby('date').size()
    
    print()
    print('=' * 80)
    print('DAILY PERFORMANCE')
    print('=' * 80)
    print(f'{"Date":<12} {"Trades":>8} {"PnL":>12} {"Return":>10} {"Status"}')
    print('-' * 80)
    
    for date in daily_pnl.index:
        pnl = daily_pnl[date]
        trades = daily_trades[date]
        pct = pnl / config.initial_capital * 100
        status = '✓' if pct >= 15 else '○' if pct > 0 else '✗'
        print(f'{date}    {trades:>8} ${pnl:>11.2f} {pct:>9.2f}% {status}')
    
    print()
    avg_daily = daily_pnl.mean()
    avg_daily_pct = avg_daily / config.initial_capital * 100
    avg_trades = daily_trades.mean()
    profitable_days = (daily_pnl > 0).sum()
    target_days = (daily_pnl > config.initial_capital * 0.15).sum()
    
    print(f'Average Daily PnL: ${avg_daily:.2f} ({avg_daily_pct:.2f}%)')
    print(f'Average Daily Trades: {avg_trades:.0f}')
    print(f'Profitable Days: {profitable_days}/{len(daily_pnl)}')
    print(f'Days >= 15%: {target_days}/{len(daily_pnl)}')
    
    # Monthly projection
    monthly_pnl = daily_pnl.sum()
    monthly_pct = monthly_pnl / config.initial_capital * 100
    print()
    print(f'Total Monthly PnL: ${monthly_pnl:.2f} ({monthly_pct:.2f}%)')

# Generate report
engine.generate_html_report('profitable_scalper_v3_report.html')
print()
print(f'Report saved to: profitable_scalper_v3_report.html')
