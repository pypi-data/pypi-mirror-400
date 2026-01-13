"""
Profitable Scalping Strategy - Target 15% Daily
High-frequency momentum scalper with 300x leverage
"""

from backtester_v2 import BacktestEngine
from backtest_config import BacktestConfig
from datetime import datetime, timedelta
import numpy as np

print('=' * 80)
print('PROFITABLE SCALPER - 15% DAILY TARGET')
print('=' * 80)
print()

# Configuration for aggressive scalping
config = BacktestConfig(
    symbol='EUR/USD',
    timeframe='1m',
    start_date=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
    end_date=datetime.now().strftime('%Y-%m-%d'),
    initial_capital=1000,
    leverage=300,
    risk_per_trade=0.005,  # 0.5% risk per trade (conservative with high leverage)
    max_pyramiding=3,       # Allow 3 concurrent trades
    slippage_model='fixed',
    slippage_pips=0.1,     # Minimal slippage
    commission_per_lot=5.0, # $5 per lot
    spread_pips=0.5,
    assume_worst_case=False,  # Optimistic for strategy testing
    trade_sessions=['london', 'newyork']  # High liquidity sessions
)

print(f'Configuration:')
print(f'  Symbol: {config.symbol}')
print(f'  Period: 1 month')
print(f'  Capital: ${config.initial_capital} x {config.leverage}:1 leverage')
print(f'  Risk/Trade: {config.risk_per_trade*100}%')
print(f'  Max Concurrent: {config.max_pyramiding}')
print(f'  Commission: ${config.commission_per_lot}/lot')
print(f'  Slippage: {config.slippage_pips} pips')
print()


def aggressive_scalper(df):
    """
    Aggressive micro-scalper targeting high win rate with tight TP.
    
    Strategy Logic:
    - Enter on strong momentum (2+ consecutive same-color candles)
    - Tight TP (1.5 pips) with wider SL (5 pips) for ~75% win rate
    - Trade only during high volatility (ATR filter)
    - Multiple entries allowed (pyramiding)
    """
    signals = []
    pip = 0.0001
    
    # Very tight scalping parameters
    tp_pips = 1.5   # Quick 1.5 pip profit
    sl_pips = 5.0   # 5 pip stop (1:3.3 risk reward)
    
    closes = df['close'].values
    opens = df['open'].values
    highs = df['high'].values
    lows = df['low'].values
    n = len(df)
    
    # Calculate indicators
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
        tr = np.zeros(len(high))
        for i in range(1, len(high)):
            hl = high[i] - low[i]
            hc = abs(high[i] - close[i-1])
            lc = abs(low[i] - close[i-1])
            tr[i] = max(hl, hc, lc)
        for i in range(period, len(high)):
            result[i] = np.mean(tr[i-period:i])
        return result
    
    ema_fast = ema(closes, 5)
    ema_slow = ema(closes, 13)
    atr_vals = atr(highs, lows, closes, 14)
    
    last_signal_bar = -3
    
    for i in range(20, n):
        # Rate limit: min 3 bars between signals
        if i - last_signal_bar < 3:
            continue
        
        close = closes[i]
        curr_atr = atr_vals[i]
        
        # Skip low volatility periods
        if curr_atr < 0.0002:  # Less than 2 pips ATR = too quiet
            continue
        
        # Trend direction
        uptrend = ema_fast[i] > ema_slow[i]
        downtrend = ema_fast[i] < ema_slow[i]
        
        # Momentum: 2 consecutive same-color candles
        bullish_momentum = (closes[i] > opens[i] and 
                          closes[i-1] > opens[i-1] and
                          closes[i] > closes[i-1])
        
        bearish_momentum = (closes[i] < opens[i] and 
                          closes[i-1] < opens[i-1] and
                          closes[i] < closes[i-1])
        
        # Strong candle body (at least 50% of range)
        body = abs(close - opens[i])
        range_size = highs[i] - lows[i]
        strong_candle = body > range_size * 0.5 if range_size > 0 else False
        
        if uptrend and bullish_momentum and strong_candle:
            signals.append({
                'index': i,
                'time': df.iloc[i]['time'],
                'type': 'BUY',
                'tp': close + tp_pips * pip,
                'sl': close - sl_pips * pip,
                'risk': 0.005,
                'comment': 'Bull Momentum'
            })
            last_signal_bar = i
            
        elif downtrend and bearish_momentum and strong_candle:
            signals.append({
                'index': i,
                'time': df.iloc[i]['time'],
                'type': 'SELL',
                'tp': close - tp_pips * pip,
                'sl': close + sl_pips * pip,
                'risk': 0.005,
                'comment': 'Bear Momentum'
            })
            last_signal_bar = i
    
    print(f'[Aggressive Scalper] Generated {len(signals)} signals')
    return signals


# Run backtest
print('Running 1-month backtest...')
print()
engine = BacktestEngine(config)
metrics = engine.run(aggressive_scalper)

# Calculate daily metrics
trades_df = engine.get_trades_df()
if not trades_df.empty:
    trades_df['date'] = trades_df['exit_time'].dt.date
    daily_pnl = trades_df.groupby('date')['pnl'].sum()
    
    print()
    print('=' * 80)
    print('DAILY PERFORMANCE')
    print('=' * 80)
    for date, pnl in daily_pnl.items():
        pct = pnl / config.initial_capital * 100
        status = '✓' if pct >= 15 else '○' if pct > 0 else '✗'
        print(f'{date}: ${pnl:>8.2f} ({pct:>6.2f}%) {status}')
    
    avg_daily = daily_pnl.mean()
    avg_daily_pct = avg_daily / config.initial_capital * 100
    profitable_days = (daily_pnl > 0).sum()
    target_days = (daily_pnl > config.initial_capital * 0.15).sum()
    
    print()
    print(f'Average Daily PnL: ${avg_daily:.2f} ({avg_daily_pct:.2f}%)')
    print(f'Profitable Days: {profitable_days}/{len(daily_pnl)}')
    print(f'Days >= 15%: {target_days}/{len(daily_pnl)}')

# Generate report
engine.generate_html_report('profitable_scalper_report.html')
print()
print(f'Report saved to: profitable_scalper_report.html')
