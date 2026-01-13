"""
Generate Visual HTML Report
Test backtester v2 with comprehensive reporting
"""

from backtester_v2 import BacktestEngine
from backtest_config import BacktestConfig
from datetime import datetime, timedelta
import numpy as np

print('=' * 70)
print('GENERATING VISUAL HTML REPORT')
print('=' * 70)
print()

# Configuration with volume-based slippage
config = BacktestConfig(
    symbol='EUR/USD',
    timeframe='1m',
    start_date=(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
    end_date=datetime.now().strftime('%Y-%m-%d'),
    initial_capital=10000,
    leverage=100,
    risk_per_trade=0.02,
    max_pyramiding=1,
    slippage_model='volume',  # Volume-based slippage
    slippage_pips=0.5,
    commission_per_lot=7.0,
    spread_pips=0.8,
    assume_worst_case=True,
    trade_sessions=['london', 'newyork']
)

print(f'Configuration:')
print(f'  Symbol: {config.symbol}')
print(f'  Capital: ${config.initial_capital:,} x {config.leverage}:1 leverage')
print(f'  Risk/Trade: {config.risk_per_trade*100}%')
print(f'  Slippage: {config.slippage_model} ({config.slippage_pips} pips base)')
print(f'  Sessions: {config.trade_sessions}')
print()

# Strategy with 3 pip TP / 10 pip SL (better R:R)
def momentum_strategy(df):
    """Momentum strategy with trend confirmation"""
    signals = []
    pip = 0.0001
    tp_pips = 3.0
    sl_pips = 10.0
    
    closes = df['close'].values
    highs = df['high'].values
    lows = df['low'].values
    n = len(df)
    
    # EMA calculations
    def ema(data, period):
        result = np.zeros(len(data))
        result[:period] = data[:period].mean()
        mult = 2 / (period + 1)
        for i in range(period, len(data)):
            result[i] = (data[i] - result[i-1]) * mult + result[i-1]
        return result
    
    ema_fast = ema(closes, 8)
    ema_slow = ema(closes, 21)
    
    last_signal = -20
    
    for i in range(25, n):
        if i - last_signal < 10:  # Min 10 bars between signals
            continue
        
        close = closes[i]
        prev_close = closes[i-1]
        
        # Trend confirmation
        uptrend = ema_fast[i] > ema_slow[i] and ema_fast[i-1] > ema_slow[i-1]
        downtrend = ema_fast[i] < ema_slow[i] and ema_fast[i-1] < ema_slow[i-1]
        
        # Momentum
        bullish = close > prev_close and prev_close > closes[i-2]
        bearish = close < prev_close and prev_close < closes[i-2]
        
        if uptrend and bullish:
            signals.append({
                'index': i,
                'time': df.iloc[i]['time'],
                'type': 'BUY',
                'tp': close + tp_pips * pip,
                'sl': close - sl_pips * pip,
                'risk': 0.02,
                'comment': 'Momentum Buy'
            })
            last_signal = i
        elif downtrend and bearish:
            signals.append({
                'index': i,
                'time': df.iloc[i]['time'],
                'type': 'SELL',
                'tp': close - tp_pips * pip,
                'sl': close + sl_pips * pip,
                'risk': 0.02,
                'comment': 'Momentum Sell'
            })
            last_signal = i
    
    print(f'[Strategy] Generated {len(signals)} signals')
    return signals

# Run backtest
engine = BacktestEngine(config)
metrics = engine.run(momentum_strategy)

# Generate HTML report
print()
print('Generating HTML report...')
engine.generate_html_report('backtest_report_v2.html')

# Print trade log sample
print()
print('=' * 70)
print('SAMPLE TRADE LOG (first 15 trades)')
print('=' * 70)
trades = engine.simulator.closed_trades
for i, t in enumerate(trades[:15]):
    result = 'WIN' if t['pnl'] > 0 else 'LOSS'
    pips = t.get('pnl_pips', 0)
    r = t.get('r_multiple', 0)
    mfe = t.get('mfe', 0)
    mae = t.get('mae', 0)
    print(f'{i+1:2}. {t["type"]:4} {result:4} | Exit: {t["exit_reason"]:15} | '
          f'PnL: ${t["pnl"]:7.2f} ({pips:+5.1f}p) | R: {r:+5.2f} | MFE: {mfe:4.1f} | MAE: {mae:4.1f}')

print()
print('=' * 70)
print(f'Report saved to: backtest_report_v2.html')
print('Open in browser to view charts and full trade log!')
print('=' * 70)
