"""
Profitable Scalping Strategy V4 - Mean Reversion
Fade overbought/oversold with tight TP
"""

from backtester_v2 import BacktestEngine
from backtest_config import BacktestConfig
from datetime import datetime, timedelta
import numpy as np

print('=' * 80)
print('PROFITABLE SCALPER V4 - MEAN REVERSION')
print('=' * 80)
print()

config = BacktestConfig(
    symbol='EUR/USD',
    timeframe='1m',
    start_date=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
    end_date=datetime.now().strftime('%Y-%m-%d'),
    initial_capital=1000,
    leverage=300,
    risk_per_trade=0.015,  # 1.5% risk per trade
    max_pyramiding=3,
    slippage_model='fixed',
    slippage_pips=0.1,
    commission_per_lot=5.0,
    spread_pips=0.3,
    assume_worst_case=False,
    trade_sessions=['london', 'newyork']
)

print(f'Configuration:')
print(f'  Capital: ${config.initial_capital} x {config.leverage}:1')
print(f'  Risk/Trade: {config.risk_per_trade*100}%')
print()

def mean_reversion_scalper(df):
    """
    Mean reversion scalper:
    - Buy when RSI < 25 and price at lower Bollinger Band
    - Sell when RSI > 75 and price at upper Bollinger Band
    - Quick TP (2 pips), tight SL (3 pips) = 1:1.5 R:R
    - Need ~40% win rate to break even
    """
    signals = []
    pip = 0.0001
    
    tp_pips = 2.0
    sl_pips = 3.0
    
    closes = df['close'].values
    opens = df['open'].values
    highs = df['high'].values
    lows = df['low'].values
    n = len(df)
    
    # RSI
    def rsi(data, period=14):
        result = np.zeros(len(data))
        gains = np.zeros(len(data))
        losses = np.zeros(len(data))
        
        for i in range(1, len(data)):
            change = data[i] - data[i-1]
            if change > 0:
                gains[i] = change
            else:
                losses[i] = abs(change)
        
        for i in range(period, len(data)):
            avg_gain = np.mean(gains[i-period:i])
            avg_loss = np.mean(losses[i-period:i])
            if avg_loss > 0:
                rs = avg_gain / avg_loss
                result[i] = 100 - (100 / (1 + rs))
            else:
                result[i] = 100
        return result
    
    # Bollinger Bands
    def bollinger(data, period=20, std_dev=2):
        upper = np.zeros(len(data))
        lower = np.zeros(len(data))
        middle = np.zeros(len(data))
        
        for i in range(period, len(data)):
            slice_data = data[i-period:i]
            middle[i] = np.mean(slice_data)
            std = np.std(slice_data)
            upper[i] = middle[i] + std_dev * std
            lower[i] = middle[i] - std_dev * std
        
        return upper, middle, lower
    
    rsi_vals = rsi(closes, 7)  # Faster RSI
    bb_upper, bb_middle, bb_lower = bollinger(closes, 15, 2)
    
    last_signal_bar = -4
    
    for i in range(20, n):
        if i - last_signal_bar < 4:  # Min 4 bars between signals
            continue
        
        close = closes[i]
        
        # Mean reversion BUY: oversold
        if rsi_vals[i] < 25 and close <= bb_lower[i]:
            signals.append({
                'index': i,
                'time': df.iloc[i]['time'],
                'type': 'BUY',
                'tp': close + tp_pips * pip,
                'sl': close - sl_pips * pip,
                'risk': 0.015,
                'comment': 'MR Buy'
            })
            last_signal_bar = i
            
        # Mean reversion SELL: overbought
        elif rsi_vals[i] > 75 and close >= bb_upper[i]:
            signals.append({
                'index': i,
                'time': df.iloc[i]['time'],
                'type': 'SELL',
                'tp': close - tp_pips * pip,
                'sl': close + sl_pips * pip,
                'risk': 0.015,
                'comment': 'MR Sell'
            })
            last_signal_bar = i
    
    print(f'[Mean Reversion] Generated {len(signals)} signals')
    return signals


# Also test a hybrid approach
def hybrid_scalper(df):
    """
    Hybrid scalper combining momentum and mean reversion:
    - Momentum during trends
    - Mean reversion during ranges
    - 2 pip TP / 2 pip SL (1:1 R:R)
    """
    signals = []
    pip = 0.0001
    
    tp_pips = 2.0
    sl_pips = 2.0
    
    closes = df['close'].values
    opens = df['open'].values
    highs = df['high'].values
    lows = df['low'].values
    n = len(df)
    
    # EMA
    def ema(data, period):
        result = np.zeros(len(data))
        if len(data) < period:
            return result
        result[:period] = np.mean(data[:period])
        mult = 2 / (period + 1)
        for i in range(period, len(data)):
            result[i] = (data[i] - result[i-1]) * mult + result[i-1]
        return result
    
    # ATR for volatility
    def atr(high, low, close, period=14):
        result = np.zeros(len(high))
        for i in range(period, len(high)):
            trs = []
            for j in range(i-period, i):
                hl = high[j] - low[j]
                hc = abs(high[j] - close[j-1]) if j > 0 else hl
                lc = abs(low[j] - close[j-1]) if j > 0 else hl
                trs.append(max(hl, hc, lc))
            result[i] = np.mean(trs)
        return result
    
    ema_5 = ema(closes, 5)
    ema_13 = ema(closes, 13)
    ema_21 = ema(closes, 21)
    atr_vals = atr(highs, lows, closes, 14)
    
    last_signal_bar = -3
    
    for i in range(25, n):
        if i - last_signal_bar < 3:
            continue
        
        close = closes[i]
        curr_atr = atr_vals[i]
        
        # Skip very low volatility
        if curr_atr < 0.0001:  # Less than 1 pip
            continue
        
        # Trend aligned
        strong_uptrend = ema_5[i] > ema_13[i] > ema_21[i]
        strong_downtrend = ema_5[i] < ema_13[i] < ema_21[i]
        
        # Pullback to fast EMA
        near_ema5 = abs(close - ema_5[i]) < curr_atr * 0.5
        
        # Momentum
        bullish = closes[i] > opens[i] and closes[i-1] > opens[i-1]
        bearish = closes[i] < opens[i] and closes[i-1] < opens[i-1]
        
        if strong_uptrend and bullish:
            signals.append({
                'index': i,
                'time': df.iloc[i]['time'],
                'type': 'BUY',
                'tp': close + tp_pips * pip,
                'sl': close - sl_pips * pip,
                'risk': 0.015
            })
            last_signal_bar = i
            
        elif strong_downtrend and bearish:
            signals.append({
                'index': i,
                'time': df.iloc[i]['time'],
                'type': 'SELL',
                'tp': close - tp_pips * pip,
                'sl': close + sl_pips * pip,
                'risk': 0.015
            })
            last_signal_bar = i
    
    print(f'[Hybrid] Generated {len(signals)} signals')
    return signals


# Test both strategies
print('Testing Mean Reversion...')
engine1 = BacktestEngine(config)
metrics1 = engine1.run(mean_reversion_scalper)

print()
print('Testing Hybrid...')
engine2 = BacktestEngine(config)
metrics2 = engine2.run(hybrid_scalper)

# Compare
print()
print('=' * 80)
print('STRATEGY COMPARISON')
print('=' * 80)
print(f'{"Strategy":<20} {"Trades":>8} {"Win%":>8} {"PF":>8} {"Net PnL":>12} {"Return":>10}')
print('-' * 70)
print(f'{"Mean Reversion":<20} {metrics1.total_trades:>8} {metrics1.win_rate*100:>7.1f}% {metrics1.profit_factor:>8.2f} ${metrics1.net_profit:>11.2f} {metrics1.total_return_pct:>9.2f}%')
print(f'{"Hybrid":<20} {metrics2.total_trades:>8} {metrics2.win_rate*100:>7.1f}% {metrics2.profit_factor:>8.2f} ${metrics2.net_profit:>11.2f} {metrics2.total_return_pct:>9.2f}%')

# Pick the better one
if metrics1.net_profit > metrics2.net_profit:
    best_engine = engine1
    best_name = 'Mean Reversion'
else:
    best_engine = engine2
    best_name = 'Hybrid'

print(f'\nBest Strategy: {best_name}')

# Daily analysis for best
trades_df = best_engine.get_trades_df()
if not trades_df.empty:
    trades_df['date'] = trades_df['exit_time'].dt.date
    daily_pnl = trades_df.groupby('date')['pnl'].sum()
    
    print()
    print('DAILY PERFORMANCE:')
    for date, pnl in daily_pnl.items():
        pct = pnl / config.initial_capital * 100
        print(f'{date}: ${pnl:>8.2f} ({pct:>6.2f}%)')
    
    print(f'\nTotal: ${daily_pnl.sum():.2f} ({daily_pnl.sum()/config.initial_capital*100:.2f}%)')

best_engine.generate_html_report('profitable_scalper_v4_report.html')
print(f'\nReport saved to: profitable_scalper_v4_report.html')
