"""
Backtester V2 Diagnostic Test
Verify correct TP/SL detection
"""

from backtester_v2 import BacktestEngine
from backtest_config import BacktestConfig
from data_engine import DataEngine
from datetime import datetime, timedelta

print('=' * 70)
print('BACKTESTER V2 - DIAGNOSTIC TEST')
print('=' * 70)
print()

# Load data
end_date = datetime.now()
start_date = end_date - timedelta(days=3)

data_engine = DataEngine()
df = data_engine.get_candles('EUR/USD', '1m', start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))

print(f'Data loaded: {len(df)} bars')
print()

# Find a guaranteed TP hit scenario
print('TEST 1: BUY with guaranteed TP hit')
print('-' * 50)

test_bar = None
test_tp = None
test_sl = None

for i in range(50, len(df)-2):
    entry = df.iloc[i]['close']
    next_high = df.iloc[i+1]['high']
    
    if (next_high - entry) / 0.0001 >= 2.0:  # 2+ pip move up
        test_bar = i
        test_tp = entry + 0.00015  # 1.5 pip TP (will be hit)
        test_sl = entry - 0.0010   # 10 pip SL (far)
        
        print(f'Bar {i}: Entry={entry:.5f}')
        print(f'  Next bar high={next_high:.5f} (+{(next_high-entry)/0.0001:.1f} pips)')
        print(f'  TP={test_tp:.5f} (should hit)')
        break

if test_bar is not None:
    # Create config
    config = BacktestConfig(
        symbol='EUR/USD',
        timeframe='1m',
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        initial_capital=1000,
        leverage=1,
        risk_per_trade=0.01,
        slippage_model='none',
        assume_worst_case=True
    )
    
    # Strategy that generates single signal
    def test_strategy(df):
        return [{'index': test_bar, 'time': df.iloc[test_bar]['time'], 'type': 'BUY', 
                 'tp': test_tp, 'sl': test_sl, 'risk': 0.01}]
    
    # Run backtest
    engine = BacktestEngine(config)
    metrics = engine.run(test_strategy, data=df)
    
    # Check result
    trades = engine.simulator.closed_trades
    if trades:
        t = trades[0]
        is_tp = t['exit_reason'] == 'TP'
        print()
        print(f'RESULT:')
        print(f'  Exit Price: {t["exit_price"]:.5f}')
        print(f'  Exit Reason: {t["exit_reason"]}')
        print(f'  PnL: ${t["pnl"]:.2f}')
        print()
        print(f'TEST 1: {"PASS ✓" if is_tp else "FAIL ✗"}')
else:
    print('No suitable test bar found - market too quiet')

print()
print('=' * 70)
print('TEST 2: SELL with guaranteed TP hit')
print('-' * 50)

test_bar = None
for i in range(50, len(df)-2):
    entry = df.iloc[i]['close']
    next_low = df.iloc[i+1]['low']
    
    if (entry - next_low) / 0.0001 >= 2.0:  # 2+ pip move down
        test_bar = i
        test_tp = entry - 0.00015  # 1.5 pip TP (will be hit for SELL)
        test_sl = entry + 0.0010   # 10 pip SL (far)
        
        print(f'Bar {i}: Entry={entry:.5f}')
        print(f'  Next bar low={next_low:.5f} (-{(entry-next_low)/0.0001:.1f} pips)')
        print(f'  TP={test_tp:.5f} (should hit)')
        break

if test_bar is not None:
    config = BacktestConfig(
        symbol='EUR/USD',
        timeframe='1m',
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        initial_capital=1000,
        leverage=1,
        risk_per_trade=0.01,
        slippage_model='none',
        assume_worst_case=True
    )
    
    def test_strategy2(df):
        return [{'index': test_bar, 'time': df.iloc[test_bar]['time'], 'type': 'SELL', 
                 'tp': test_tp, 'sl': test_sl, 'risk': 0.01}]
    
    engine = BacktestEngine(config)
    metrics = engine.run(test_strategy2, data=df)
    
    trades = engine.simulator.closed_trades
    if trades:
        t = trades[0]
        is_tp = t['exit_reason'] == 'TP'
        print()
        print(f'RESULT:')
        print(f'  Exit Price: {t["exit_price"]:.5f}')
        print(f'  Exit Reason: {t["exit_reason"]}')
        print(f'  PnL: ${t["pnl"]:.2f}')
        print()
        print(f'TEST 2: {"PASS ✓" if is_tp else "FAIL ✗"}')

print()
print('=' * 70)
