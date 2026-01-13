import pandas as pd
from datetime import timedelta
from data_engine import DataEngine
from trade_manager import TradeManager

class Backtester:
    def __init__(self, data_engine: DataEngine, trade_manager: TradeManager):
        self.data = data_engine
        self.tm = trade_manager

    def run(self, symbol, timeframe, start_str, end_str, strategy_func, initial_capital=10000, commission_rate=0.0):
        print(f"--- Starting Backtest for {symbol} ---")
        
        # Update TradeManager settings
        self.tm.initial_capital = initial_capital
        self.tm.current_capital = initial_capital
        self.tm.commission_rate = commission_rate
        self.tm.equity_curve = [{'time': None, 'equity': initial_capital}]
        self.tm.drawdown_curve = []
        self.tm.trades = []
        
        # Tick Buffer
        self.tick_buffer = None
        self.tick_buffer_start = None
        self.tick_buffer_end = None
        
        # 1. Fetch OHLCV Data
        df = self.data.get_candles(symbol, timeframe, start_str, end_str)
        if df.empty:
            print("No data found.")
            return

        # 2. Run Strategy to get signals
        signals = strategy_func(df)
        
        # Index signals for O(1) lookup
        signals_by_index = {s['index']: s for s in signals}

        # 3. Main Loop
        for i in range(len(df)):
            candle = df.iloc[i]
            current_time = candle['time']
            open_price = candle['open']
            high_price = candle['high']
            low_price = candle['low']
            close_price = candle['close']
            
            # --- A. Check Active Trades for Exit (TP/SL) ---
            active_trades = self.tm.get_active_trades(symbol)
            for trade in active_trades:
                # Check if TP or SL is within this candle's range
                hit_tp = False
                hit_sl = False
                
                if trade.type == 'BUY':
                    # BUY: TP is above entry (need high to reach it), SL is below entry (need low to reach it)
                    if trade.tp and high_price >= trade.tp: hit_tp = True
                    if trade.sl and low_price <= trade.sl: hit_sl = True
                else: # SELL
                    # SELL: TP is below entry (need low to reach it), SL is above entry (need high to reach it)
                    if trade.tp and low_price <= trade.tp: hit_tp = True
                    if trade.sl and high_price >= trade.sl: hit_sl = True
                
                # Optimization: Only fetch ticks if BOTH TP and SL are hit (Ambiguous Exit)
                # If only one is hit, we know which one it is.
                ambiguous_exit = hit_tp and hit_sl
                
                if ambiguous_exit:
                    # **TICK RESOLUTION NEEDED**
                    # Fetch ticks for this specific candle to see what happened first
                    
                    # Optimize: Batch Tick Fetching
                    # Check if we have ticks in buffer for current_time
                    if self.tick_buffer is None or self.tick_buffer.empty or \
                       current_time < self.tick_buffer_start or current_time >= self.tick_buffer_end:
                        
                        # Fetch next batch (Reduced to 1 hour for Crypto/Stocks)
                        self.tick_buffer_start = current_time
                        self.tick_buffer_end = current_time + timedelta(hours=1)
                        
                        # print(f"[Backtester] Fetching tick batch: {self.tick_buffer_start} - {self.tick_buffer_end}")
                        self.tick_buffer = self.data.get_ticks(
                            symbol, 
                            self.tick_buffer_start.strftime("%Y-%m-%d-%H-%M-%S"), 
                            self.tick_buffer_end.strftime("%Y-%m-%d-%H-%M-%S")
                        )
                    
                    # Slice ticks for this minute
                    tick_start = current_time
                    tick_end = current_time + timedelta(minutes=1)
                    
                    if not self.tick_buffer.empty:
                        mask = (self.tick_buffer['time'] >= tick_start) & (self.tick_buffer['time'] < tick_end)
                        ticks = self.tick_buffer.loc[mask]
                    else:
                        ticks = pd.DataFrame()

                    if not ticks.empty:
                        # Simulate tick by tick
                        for _, tick in ticks.iterrows():
                            price = tick['price']
                            time = tick['time']
                            
                            # Calculate tick slippage
                            tick_vol = tick['volume']
                            slip_pct = 0.0001 * (1000 / (tick_vol + 1))
                            slip_pct = min(slip_pct, 0.01)

                            if trade.type == 'BUY':
                                if trade.sl and price <= trade.sl:
                                    exec_p = trade.sl * (1 - slip_pct)
                                    self.tm.close_trade(trade, exec_p, time, f"SL Hit (Tick)", slippage=slip_pct)
                                    break
                                if trade.tp and price >= trade.tp:
                                    exec_p = trade.tp * (1 - slip_pct)
                                    self.tm.close_trade(trade, exec_p, time, f"TP Hit (Tick)", slippage=slip_pct)
                                    break
                            else: # SELL
                                if trade.sl and price >= trade.sl:
                                    exec_p = trade.sl * (1 + slip_pct)
                                    self.tm.close_trade(trade, exec_p, time, f"SL Hit (Tick)", slippage=slip_pct)
                                    break
                                if trade.tp and price <= trade.tp:
                                    exec_p = trade.tp * (1 + slip_pct)
                                    self.tm.close_trade(trade, exec_p, time, f"TP Hit (Tick)", slippage=slip_pct)
                                    break
                    else:
                        # No ticks available, fallback to OHLC
                        # If ambiguous but no ticks, assume SL hit first (Conservative)
                        candle_vol = candle['volume']
                        slip_pct = 0.0001 * (10000 / (candle_vol + 1))
                        slip_pct = min(slip_pct, 0.01)

                        if hit_sl:
                            exec_p = trade.sl * (1 - slip_pct) if trade.type == 'BUY' else trade.sl * (1 + slip_pct)
                            self.tm.close_trade(trade, exec_p, current_time, f"SL Hit (Ambiguous OHLC)", slippage=slip_pct)
                        elif hit_tp:
                            exec_p = trade.tp * (1 - slip_pct) if trade.type == 'BUY' else trade.tp * (1 + slip_pct)
                            self.tm.close_trade(trade, exec_p, current_time, f"TP Hit (Ambiguous OHLC)", slippage=slip_pct)
                
                else:
                    # Not ambiguous - only one hit (or neither, but we filtered that)
                    # Execute immediately without ticks
                    candle_vol = candle['volume']
                    slip_pct = 0.0001 * (10000 / (candle_vol + 1))
                    slip_pct = min(slip_pct, 0.01)
                    
                    if hit_sl:
                        exec_p = trade.sl * (1 - slip_pct) if trade.type == 'BUY' else trade.sl * (1 + slip_pct)
                        self.tm.close_trade(trade, exec_p, current_time, f"SL Hit (OHLC)", slippage=slip_pct)
                    elif hit_tp:
                        exec_p = trade.tp * (1 - slip_pct) if trade.type == 'BUY' else trade.tp * (1 + slip_pct)
                        self.tm.close_trade(trade, exec_p, current_time, f"TP Hit (OHLC)", slippage=slip_pct)

            # --- B. Check for New Signals ---
            if i in signals_by_index:
                sig = signals_by_index[i]
                
                # Calculate Slippage based on volume
                candle_vol = candle['volume']
                slippage_pct = 0.0001 * (10000 / (candle_vol + 1))
                slippage_pct = min(slippage_pct, 0.01)
                
                exec_price = close_price
                if sig['type'] == 'BUY':
                    exec_price = close_price * (1 + slippage_pct)
                else:
                    exec_price = close_price * (1 - slippage_pct)

                # Determine Position Size
                size = 1.0 # Default fixed size
                if 'size' in sig:
                    size = sig['size']
                elif 'risk' in sig and sig.get('sl'):
                    # Dynamic Sizing based on Risk %
                    size = self.tm.calculate_position_size(exec_price, sig['risk'], sig['sl'])

                self.tm.open_trade(
                    symbol=symbol,
                    type=sig['type'],
                    price=exec_price,
                    time=current_time,
                    size=size, 
                    sl=sig.get('sl'),
                    tp=sig.get('tp'),
                    comment=sig.get('comment', '') + f" (Slip: {slippage_pct:.4f})"
                )
            
            # --- C. Update Equity Curve ---
            # We pass current close price for unrealized PnL calculation
            self.tm.update_equity(current_time, {symbol: close_price})

        # 5. Close all open trades at the end
        final_time = df.iloc[-1]['time']
        final_price = df.iloc[-1]['close']
        active_trades = self.tm.get_active_trades(symbol)
        for trade in active_trades:
            self.tm.close_trade(trade, final_price, final_time, "End of Backtest")
            
        # Final Equity Update
        self.tm.update_equity(final_time, {symbol: final_price})

        # 4. Generate Report
        total_pnl = self.tm.get_total_pnl()
        print(f"--- Backtest Finished ---")
        print(f"Total PnL: {total_pnl}")
        print(f"Trades: {len(self.tm.get_closed_trades())} closed, {len(self.tm.get_active_trades())} open")
