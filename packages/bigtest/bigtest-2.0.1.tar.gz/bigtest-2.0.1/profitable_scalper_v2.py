"""
Profitable Scalping Strategy V2 - Optimized R:R
Testing multiple configurations to find profitable setup
"""

from backtester_v2 import BacktestEngine
from backtest_config import BacktestConfig
from datetime import datetime, timedelta
import numpy as np

print('=' * 80)
print('PROFITABLE SCALPER V2 - OPTIMIZED R:R')
print('=' * 80)
print()

# Try different configurations
configs_to_test = [
    {'tp': 2.0, 'sl': 2.0, 'name': '1:1 Even R:R'},
    {'tp': 3.0, 'sl': 2.0, 'name': '1.5:1 Good R:R'},
    {'tp': 4.0, 'sl': 2.0, 'name': '2:1 Best R:R'},
]

base_config = BacktestConfig(
    symbol='EUR/USD',
    timeframe='1m',
    start_date=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
    end_date=datetime.now().strftime('%Y-%m-%d'),
    initial_capital=1000,
    leverage=300,
    risk_per_trade=0.01,  # 1% risk per trade
    max_pyramiding=1,     # Single position
    slippage_model='fixed',
    slippage_pips=0.1,
    commission_per_lot=5.0,
    spread_pips=0.3,
    assume_worst_case=False,
    trade_sessions=['london', 'newyork']
)

def create_strategy(tp_pips, sl_pips):
    """Create strategy with specified TP/SL"""
    
    def strategy(df):
        signals = []
        pip = 0.0001
        
        closes = df['close'].values
        opens = df['open'].values
        highs = df['high'].values
        lows = df['low'].values
        n = len(df)
        
        # EMA trend filter
        def ema(data, period):
            result = np.zeros(len(data))
            if len(data) < period:
                return result
            result[:period] = np.mean(data[:period])
            mult = 2 / (period + 1)
            for i in range(period, len(data)):
                result[i] = (data[i] - result[i-1]) * mult + result[i-1]
            return result
        
        ema_8 = ema(closes, 8)
        ema_21 = ema(closes, 21)
        
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
        
        rsi_vals = rsi(closes, 14)
        
        last_signal_bar = -5
        
        for i in range(25, n):
            if i - last_signal_bar < 5:  # Min 5 bars between signals
                continue
            
            close = closes[i]
            
            # Strong trend alignment
            uptrend = ema_8[i] > ema_21[i]
            downtrend = ema_8[i] < ema_21[i]
            
            # Momentum candle
            bullish = closes[i] > opens[i] and closes[i-1] > opens[i-1]
            bearish = closes[i] < opens[i] and closes[i-1] < opens[i-1]
            
            # RSI confirmation (not overbought/oversold)
            rsi_ok_buy = 40 < rsi_vals[i] < 70
            rsi_ok_sell = 30 < rsi_vals[i] < 60
            
            if uptrend and bullish and rsi_ok_buy:
                signals.append({
                    'index': i,
                    'time': df.iloc[i]['time'],
                    'type': 'BUY',
                    'tp': close + tp_pips * pip,
                    'sl': close - sl_pips * pip,
                    'risk': 0.01
                })
                last_signal_bar = i
                
            elif downtrend and bearish and rsi_ok_sell:
                signals.append({
                    'index': i,
                    'time': df.iloc[i]['time'],
                    'type': 'SELL',
                    'tp': close - tp_pips * pip,
                    'sl': close + sl_pips * pip,
                    'risk': 0.01
                })
                last_signal_bar = i
        
        return signals
    
    return strategy

# Test each configuration
results = []

for cfg in configs_to_test:
    print(f'\nTesting: {cfg["name"]} (TP={cfg["tp"]} SL={cfg["sl"]})')
    print('-' * 50)
    
    engine = BacktestEngine(base_config)
    strategy = create_strategy(cfg['tp'], cfg['sl'])
    metrics = engine.run(strategy)
    
    results.append({
        'name': cfg['name'],
        'tp': cfg['tp'],
        'sl': cfg['sl'],
        'trades': metrics.total_trades,
        'win_rate': metrics.win_rate,
        'pf': metrics.profit_factor,
        'net_pnl': metrics.net_profit,
        'return_pct': metrics.total_return_pct,
        'max_dd': metrics.max_drawdown_pct,
        'sharpe': metrics.sharpe_ratio
    })

# Find best configuration
print()
print('=' * 80)
print('CONFIGURATION COMPARISON')
print('=' * 80)
print(f'{"Config":<20} {"Trades":>8} {"Win%":>8} {"PF":>8} {"Net PnL":>12} {"Return":>10} {"MaxDD":>10}')
print('-' * 80)

best = None
best_pnl = float('-inf')

for r in results:
    print(f'{r["name"]:<20} {r["trades"]:>8} {r["win_rate"]*100:>7.1f}% {r["pf"]:>8.2f} ${r["net_pnl"]:>11.2f} {r["return_pct"]:>9.2f}% {r["max_dd"]*100:>9.2f}%')
    if r['net_pnl'] > best_pnl:
        best_pnl = r['net_pnl']
        best = r

print()
print(f'Best Configuration: {best["name"]}')
print(f'Net Profit: ${best["net_pnl"]:.2f} ({best["return_pct"]:.2f}%)')

# Run full report for best config
print()
print('Generating detailed report for best configuration...')
engine = BacktestEngine(base_config)
strategy = create_strategy(best['tp'], best['sl'])
metrics = engine.run(strategy)

# Daily breakdown
trades_df = engine.get_trades_df()
if not trades_df.empty:
    trades_df['date'] = trades_df['exit_time'].dt.date
    daily_pnl = trades_df.groupby('date')['pnl'].sum()
    
    print()
    print('DAILY PERFORMANCE:')
    for date, pnl in daily_pnl.items():
        pct = pnl / base_config.initial_capital * 100
        print(f'{date}: ${pnl:>8.2f} ({pct:>6.2f}%)')
    
    avg_daily = daily_pnl.mean()
    avg_daily_pct = avg_daily / base_config.initial_capital * 100
    print(f'\nAverage Daily: ${avg_daily:.2f} ({avg_daily_pct:.2f}%)')

engine.generate_html_report('profitable_scalper_v2_report.html')
print(f'\nReport saved to: profitable_scalper_v2_report.html')
