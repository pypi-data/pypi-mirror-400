"""
Full Strategy Test with Backtester V2
Test pip grabber strategy with the new engine
"""

from backtester_v2 import BacktestEngine
from backtest_config import BacktestConfig
from data_engine import DataEngine
from datetime import datetime, timedelta
import numpy as np

print('=' * 70)
print('PIP GRABBER STRATEGY - BACKTESTER V2')
print('=' * 70)
print()

# Configuration
config = BacktestConfig(
    symbol='EUR/USD',
    timeframe='1m',
    start_date=(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
    end_date=datetime.now().strftime('%Y-%m-%d'),
    initial_capital=1000,
    leverage=100,
    risk_per_trade=0.01,
    max_pyramiding=1,
    slippage_model='fixed',
    slippage_pips=0.3,
    commission_per_lot=7.0,
    spread_pips=0.5,
    assume_worst_case=True,
    trade_sessions=['london', 'newyork']
)

print(f'Config:')
print(f'  Symbol: {config.symbol}')
print(f'  Capital: ${config.initial_capital} x {config.leverage}:1')
print(f'  Risk/Trade: {config.risk_per_trade*100}%')
print(f'  Sessions: {config.trade_sessions}')
print()

# Simple momentum strategy
def pip_grabber_strategy_v2(df):
    """
    Simple momentum strategy with 2 pip TP / 8 pip SL
    """
    signals = []
    pip = 0.0001
    tp_pips = 2.0
    sl_pips = 8.0
    
    closes = df['close'].values
    n = len(df)
    
    # Simple EMA calculation
    ema_period = 20
    ema = np.zeros(n)
    ema[:ema_period] = closes[:ema_period].mean()
    mult = 2 / (ema_period + 1)
    for i in range(ema_period, n):
        ema[i] = (closes[i] - ema[i-1]) * mult + ema[i-1]
    
    last_signal_bar = -10
    
    for i in range(ema_period + 5, n):
        if i - last_signal_bar < 5:  # Min 5 bars between signals
            continue
        
        close = closes[i]
        
        # Simple trend following
        above_ema = close > ema[i]
        green = close > df.iloc[i]['open']
        red = close < df.iloc[i]['open']
        
        if above_ema and green:
            signals.append({
                'index': i,
                'time': df.iloc[i]['time'],
                'type': 'BUY',
                'tp': close + tp_pips * pip,
                'sl': close - sl_pips * pip,
                'risk': 0.01
            })
            last_signal_bar = i
        elif not above_ema and red:
            signals.append({
                'index': i,
                'time': df.iloc[i]['time'],
                'type': 'SELL',
                'tp': close - tp_pips * pip,
                'sl': close + sl_pips * pip,
                'risk': 0.01
            })
            last_signal_bar = i
    
    print(f'[Strategy] Generated {len(signals)} signals')
    return signals

# Run backtest
engine = BacktestEngine(config)
metrics = engine.run(pip_grabber_strategy_v2)

# Print detailed results
print()
print('=' * 70)
print('DETAILED TRADE ANALYSIS')
print('=' * 70)
print()

trades = engine.simulator.closed_trades
wins = [t for t in trades if t['pnl'] > 0]
losses = [t for t in trades if t['pnl'] <= 0]

# Exit reason breakdown
exit_reasons = {}
for t in trades:
    r = t['exit_reason']
    if r not in exit_reasons:
        exit_reasons[r] = 0
    exit_reasons[r] += 1

print('Exit Reasons:')
for reason, count in exit_reasons.items():
    pct = count / len(trades) * 100 if trades else 0
    print(f'  {reason}: {count} ({pct:.1f}%)')

print()
print('Sample Trades:')
for t in trades[:10]:
    result = 'WIN' if t['pnl'] > 0 else 'LOSS'
    pips = t.get('pnl_pips', 0)
    print(f'  {t["type"]} {result}: {t["exit_reason"]} | PnL: ${t["pnl"]:.2f} ({pips:+.1f} pips)')

print()
print('=' * 70)
