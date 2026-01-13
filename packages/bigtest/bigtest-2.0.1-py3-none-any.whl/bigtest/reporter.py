import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

class Reporter:
    def __init__(self, trade_manager):
        self.tm = trade_manager

    def generate_html_report(self, filename="backtest_report.html", period_start=None, period_end=None):
        print("Generating Professional HTML Report...")
        
        # 1. Get Data
        trades_df = self.tm.get_trades_df()
        equity_df = pd.DataFrame(self.tm.equity_curve)
        drawdown_df = pd.DataFrame(self.tm.drawdown_curve)
        
        if equity_df.empty:
            print("No equity data to report.")
            return

        # 2. Calculate Advanced Metrics
        total_pnl = self.tm.get_total_pnl()
        total_trades = len(trades_df)
        win_rate = 0
        profit_factor = 0
        avg_trade = 0
        if 'drawdown' in drawdown_df.columns and not drawdown_df.empty:
            max_dd = drawdown_df['drawdown'].max()
        else:
            max_dd = 0.0
        
        
        # Initialize metrics
        win_rate = 0.0
        profit_factor = 0.0
        avg_trade = 0.0
        avg_slippage = 0.0
        
        if total_trades > 0:
            wins = trades_df[trades_df['PnL'] > 0]
            losses = trades_df[trades_df['PnL'] <= 0]
            win_rate = (len(wins) / total_trades) * 100
            gross_profit = wins['PnL'].sum()
            gross_loss = abs(losses['PnL'].sum())
            profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
            avg_trade = total_pnl / total_trades
            
            # Slippage Analysis
            if self.tm.trades:
                slippages = [t.slippage for t in self.tm.trades]
                if slippages:
                    avg_slippage = sum(slippages) / len(slippages)

        # 3. Create Charts (Dark Theme)
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                            vertical_spacing=0.05, row_heights=[0.7, 0.3],
                            subplot_titles=("Equity Curve", "Drawdown"))

        # Equity Line
        fig.add_trace(go.Scatter(x=equity_df['time'], y=equity_df['equity'], 
                                 mode='lines', name='Equity', line=dict(color='#00ff00', width=2)), row=1, col=1)
        
        # Drawdown Area
        # Drawdown Area
        if 'time' in drawdown_df.columns and 'drawdown' in drawdown_df.columns:
            fig.add_trace(go.Scatter(x=drawdown_df['time'], y=drawdown_df['drawdown'], 
                                     mode='lines', name='Drawdown %', fill='tozeroy', line=dict(color='#ff0000', width=1)), row=2, col=1)

        fig.update_layout(
            template="plotly_dark",
            title_text=f"Backtest Performance ({period_start} to {period_end})", 
            height=800,
            paper_bgcolor='#1e1e1e',
            plot_bgcolor='#1e1e1e',
            font=dict(family="Roboto, sans-serif", color="#e0e0e0")
        )

        # 4. Create HTML Content with Wall Street Styling
        
        # Colorize PnL in Table
        def color_pnl(val):
            color = '#00ff00' if val > 0 else '#ff0000'
            return f'<span style="color: {color}">{val:.2f}</span>'
            
        trades_html = trades_df.to_html(index=False, escape=False, formatters={'PnL': color_pnl, 'PnL %': color_pnl})
        trades_html = trades_html.replace('class="dataframe"', 'class="trade-table"') # Add class for styling

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>BigTest Professional Report</title>
            <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap" rel="stylesheet">
            <style>
                body {{ font-family: 'Roboto', sans-serif; margin: 0; padding: 20px; background-color: #121212; color: #e0e0e0; }}
                h1, h2, h3 {{ color: #ffffff; }}
                .container {{ max_width: 1200px; margin: 0 auto; }}
                
                /* Metrics Grid */
                .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 20px; margin-bottom: 30px; }}
                .card {{ background-color: #1e1e1e; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); text-align: center; border-top: 3px solid #333; }}
                .card h3 {{ font-size: 14px; text-transform: uppercase; color: #888; margin: 0 0 10px 0; }}
                .card p {{ font-size: 24px; font-weight: 700; margin: 0; }}
                .pos {{ color: #00ff00; }}
                .neg {{ color: #ff0000; }}
                
                /* Table Styling */
                .trade-table {{ width: 100%; border-collapse: collapse; margin-top: 20px; background-color: #1e1e1e; border-radius: 8px; overflow: hidden; }}
                .trade-table th, .trade-table td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #333; }}
                .trade-table th {{ background-color: #2c2c2c; color: #ffffff; font-weight: 600; text-transform: uppercase; font-size: 12px; }}
                .trade-table tr:hover {{ background-color: #252525; }}
                
                /* Chart Container */
                .chart-container {{ background-color: #1e1e1e; padding: 20px; border-radius: 8px; margin-bottom: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>BigTest Professional Report</h1>
                <p style="color: #888;">Period: {period_start} to {period_end}</p>
                
                <div class="metrics-grid">
                    <div class="card" style="border-top-color: {'#00ff00' if total_pnl >= 0 else '#ff0000'}">
                        <h3>Total PnL</h3>
                        <p class="{'pos' if total_pnl >= 0 else 'neg'}">${total_pnl:,.2f}</p>
                    </div>
                    <div class="card">
                        <h3>Win Rate</h3>
                        <p>{win_rate:.1f}%</p>
                    </div>
                    <div class="card">
                        <h3>Profit Factor</h3>
                        <p>{profit_factor:.2f}</p>
                    </div>
                    <div class="card">
                        <h3>Total Trades</h3>
                        <p>{total_trades}</p>
                    </div>
                    <div class="card">
                        <h3>Max Drawdown</h3>
                        <p class="neg">{max_dd:.2f}%</p>
                    </div>
                    <div class="card">
                        <h3>Avg Trade</h3>
                        <p>${avg_trade:.2f}</p>
                    </div>
                    <div class="card">
                        <h3>Avg Slippage</h3>
                        <p>{avg_slippage:.5f}</p>
                    </div>
                </div>

                <div class="chart-container">
                    {fig.to_html(full_html=False, include_plotlyjs='cdn')}
                </div>
                
                <h2>Trade Log</h2>
                <div style="overflow-x: auto;">
                    {trades_html}
                </div>
            </div>
        </body>
        </html>
        """
        
        with open(filename, "w") as f:
            f.write(html_content)
            
        print(f"Report saved to {os.path.abspath(filename)}")
