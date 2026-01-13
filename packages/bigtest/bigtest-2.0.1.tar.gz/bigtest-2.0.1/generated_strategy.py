import pythonpine as pp

def rsi_strategy(df):
    signals = []
    closes = df['close'].tolist()
    highs = df['high'].tolist()
    lows = df['low'].tolist()
    opens = df['open'].tolist()
    volumes = df['volume'].tolist()

    length = 14
    overbought = 70
    oversold = 30
    r = pp.rsi(closes, length)

    # Trading Logic Loop
    for i in range(50, len(df)):
        if r[i] < oversold:
            signals.append({'index': i, 'type': 'BUY', 'sl': 0, 'tp': 0, 'comment': 'Long'})
        if r[i] > overbought:
            pass # strategy.close('Long') - Manual logic needed for direction

    return signals