"""
Enhanced Report Generator - Premium UI with Interactive Charts
Professional backtesting reports with TradingView-style charts
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import json
import os


class ReportGenerator:
    """
    Generates premium HTML reports with:
    - Interactive Plotly charts with zoom/pan
    - TradingView-style dark theme
    - Animated stat cards
    - Sortable/filterable trade log
    - Export functionality
    """
    
    def __init__(self):
        pass
    
    def generate_html_report(self, 
                             trades: List[Dict],
                             equity_curve: List[Dict],
                             metrics: Any,
                             config: Any,
                             filename: str = 'backtest_report.html') -> str:
        """Generate premium HTML report with interactive charts."""
        
        # Prepare data
        trade_log_html = self._generate_trade_log(trades)
        summary_html = self._generate_summary(metrics, config)
        
        # Prepare chart data
        equity_data = self._prepare_equity_data(equity_curve)
        drawdown_data = self._prepare_drawdown_data(equity_curve)
        monthly_data = self._prepare_monthly_data(trades)
        distribution_data = self._prepare_distribution_data(trades)
        cumulative_pnl = self._prepare_cumulative_pnl(trades)
        trade_scatter = self._prepare_trade_scatter(trades)
        
        # Build HTML
        html = self._build_html(
            config=config,
            metrics=metrics,
            summary_html=summary_html,
            trade_log_html=trade_log_html,
            equity_data=equity_data,
            drawdown_data=drawdown_data,
            monthly_data=monthly_data,
            distribution_data=distribution_data,
            cumulative_pnl=cumulative_pnl,
            trade_scatter=trade_scatter,
            total_trades=len(trades)
        )
        
        # Save file
        with open(filename, 'w') as f:
            f.write(html)
        
        print(f"Report saved to: {os.path.abspath(filename)}")
        return filename
    
    def _prepare_equity_data(self, equity_curve: List[Dict]) -> Dict:
        """Prepare equity curve for Plotly"""
        step = max(1, len(equity_curve) // 500)
        times = []
        values = []
        
        for e in equity_curve[::step]:
            t = e.get('time')
            if t and hasattr(t, 'isoformat'):
                times.append(t.isoformat())
            elif t:
                times.append(str(t))
            values.append(round(e.get('equity', 0), 2))
        
        return {'times': times, 'values': values}
    
    def _prepare_drawdown_data(self, equity_curve: List[Dict]) -> Dict:
        """Prepare drawdown data for Plotly"""
        step = max(1, len(equity_curve) // 500)
        times = []
        values = []
        peak = equity_curve[0].get('equity', 0) if equity_curve else 0
        
        for e in equity_curve[::step]:
            eq = e.get('equity', 0)
            peak = max(peak, eq)
            dd = (peak - eq) / peak * 100 if peak > 0 else 0
            
            t = e.get('time')
            if t and hasattr(t, 'isoformat'):
                times.append(t.isoformat())
            elif t:
                times.append(str(t))
            values.append(round(dd, 2))
        
        return {'times': times, 'values': values}
    
    def _prepare_monthly_data(self, trades: List[Dict]) -> Dict:
        """Prepare monthly PnL"""
        monthly = {}
        for t in trades:
            if 'exit_time' in t and t['exit_time']:
                try:
                    key = t['exit_time'].strftime('%Y-%m')
                except:
                    continue
                if key not in monthly:
                    monthly[key] = 0
                monthly[key] += t['pnl']
        
        return {
            'months': list(monthly.keys()),
            'pnl': [round(v, 2) for v in monthly.values()],
            'colors': ['#10b981' if v >= 0 else '#ef4444' for v in monthly.values()]
        }
    
    def _prepare_distribution_data(self, trades: List[Dict]) -> Dict:
        """Prepare PnL distribution"""
        if not trades:
            return {'bins': [], 'counts': []}
        
        pnls = [t['pnl'] for t in trades]
        bins = np.linspace(min(pnls), max(pnls), 20)
        hist, edges = np.histogram(pnls, bins=bins)
        
        return {
            'bins': [f"${(edges[i]+edges[i+1])/2:.0f}" for i in range(len(hist))],
            'counts': hist.tolist()
        }
    
    def _prepare_cumulative_pnl(self, trades: List[Dict]) -> Dict:
        """Prepare cumulative PnL by trade"""
        cum = 0
        indices = []
        pnls = []
        colors = []
        
        for i, t in enumerate(trades):
            cum += t['pnl']
            indices.append(i + 1)
            pnls.append(round(cum, 2))
            colors.append('#10b981' if t['pnl'] >= 0 else '#ef4444')
        
        return {'indices': indices, 'pnls': pnls, 'colors': colors}
    
    def _prepare_trade_scatter(self, trades: List[Dict]) -> Dict:
        """Prepare scatter plot of wins vs losses"""
        wins = {'pnl': [], 'r': [], 'text': []}
        losses = {'pnl': [], 'r': [], 'text': []}
        
        for i, t in enumerate(trades):
            data = wins if t['pnl'] > 0 else losses
            data['pnl'].append(round(t['pnl'], 2))
            data['r'].append(round(t.get('r_multiple', 0), 2))
            data['text'].append(f"Trade #{i+1}<br>PnL: ${t['pnl']:.2f}<br>R: {t.get('r_multiple', 0):.2f}")
        
        return {'wins': wins, 'losses': losses}
    
    def _generate_trade_log(self, trades: List[Dict]) -> str:
        """Generate trade log rows"""
        if not trades:
            return ""
        
        rows = []
        for t in trades:
            pnl_class = 'win' if t['pnl'] > 0 else 'loss' if t['pnl'] < 0 else ''
            
            duration = t.get('duration', '')
            if hasattr(duration, 'total_seconds'):
                secs = int(duration.total_seconds())
                duration_str = f"{secs//3600}h {(secs%3600)//60}m"
            else:
                duration_str = '-'
            
            sl_str = f"{t['sl']:.5f}" if t.get('sl') else '-'
            tp_str = f"{t['tp']:.5f}" if t.get('tp') else '-'
            entry_time = str(t.get('entry_time', '-'))[:19]
            exit_time = str(t.get('exit_time', '-'))[:19]
            
            rows.append(f'''<tr class="{pnl_class}">
                <td>{t['id']}</td>
                <td><span class="badge {t['type'].lower()}">{t['type']}</span></td>
                <td>{entry_time}</td>
                <td>{t['entry_price']:.5f}</td>
                <td>{exit_time}</td>
                <td>{t['exit_price']:.5f}</td>
                <td>{t['size']:.2f}</td>
                <td>{sl_str}</td>
                <td>{tp_str}</td>
                <td class="pnl {pnl_class}">${t['pnl']:.2f}</td>
                <td>{t.get('pnl_pips', 0):+.1f}</td>
                <td class="{pnl_class}">{t.get('r_multiple', 0):+.2f}R</td>
                <td>{t.get('mfe', 0):.1f}</td>
                <td>{t.get('mae', 0):.1f}</td>
                <td>{duration_str}</td>
                <td><span class="exit-badge">{t['exit_reason']}</span></td>
            </tr>''')
        
        return '\n'.join(rows)
    
    def _generate_summary(self, m: Any, c: Any) -> str:
        """Generate summary cards"""
        return f'''
        <div class="metric-card">
            <div class="metric-icon">📊</div>
            <div class="metric-content">
                <div class="metric-label">Performance</div>
                <div class="metric-items">
                    <div class="item"><span>Net Profit</span><span class="{'win' if m.net_profit >= 0 else 'loss'}">${m.net_profit:,.2f}</span></div>
                    <div class="item"><span>Total Return</span><span>{m.total_return_pct:.2f}%</span></div>
                    <div class="item"><span>Profit Factor</span><span>{m.profit_factor:.2f}</span></div>
                    <div class="item"><span>Expectancy</span><span>${m.expected_payoff:.2f}</span></div>
                </div>
            </div>
        </div>
        <div class="metric-card">
            <div class="metric-icon">🎯</div>
            <div class="metric-content">
                <div class="metric-label">Win/Loss Stats</div>
                <div class="metric-items">
                    <div class="item"><span>Total Trades</span><span>{m.total_trades}</span></div>
                    <div class="item"><span>Winners</span><span class="win">{m.winning_trades} ({m.win_rate*100:.1f}%)</span></div>
                    <div class="item"><span>Losers</span><span class="loss">{m.losing_trades} ({m.loss_rate*100:.1f}%)</span></div>
                    <div class="item"><span>Win/Loss Ratio</span><span>{m.avg_win_loss_ratio:.2f}</span></div>
                </div>
            </div>
        </div>
        <div class="metric-card">
            <div class="metric-icon">📈</div>
            <div class="metric-content">
                <div class="metric-label">Trade Averages</div>
                <div class="metric-items">
                    <div class="item"><span>Avg Trade</span><span>${m.avg_profit:.2f}</span></div>
                    <div class="item"><span>Avg Win</span><span class="win">${m.avg_win:.2f}</span></div>
                    <div class="item"><span>Avg Loss</span><span class="loss">${m.avg_loss:.2f}</span></div>
                    <div class="item"><span>Avg R</span><span>{m.avg_r_multiple:.2f}R</span></div>
                </div>
            </div>
        </div>
        <div class="metric-card">
            <div class="metric-icon">⚠️</div>
            <div class="metric-content">
                <div class="metric-label">Risk Metrics</div>
                <div class="metric-items">
                    <div class="item"><span>Max Drawdown</span><span class="loss">{m.max_drawdown_pct*100:.2f}%</span></div>
                    <div class="item"><span>DD Duration</span><span>{m.max_drawdown_duration} bars</span></div>
                    <div class="item"><span>Largest Win</span><span class="win">${m.largest_win:.2f}</span></div>
                    <div class="item"><span>Largest Loss</span><span class="loss">${m.largest_loss:.2f}</span></div>
                </div>
            </div>
        </div>
        <div class="metric-card">
            <div class="metric-icon">📉</div>
            <div class="metric-content">
                <div class="metric-label">Streaks</div>
                <div class="metric-items">
                    <div class="item"><span>Max Win Streak</span><span class="win">{m.max_consecutive_wins}</span></div>
                    <div class="item"><span>Max Loss Streak</span><span class="loss">{m.max_consecutive_losses}</span></div>
                    <div class="item"><span>Total R</span><span>{m.total_r:.2f}R</span></div>
                    <div class="item"><span>Expectancy R</span><span>{m.expectancy_r:.2f}R</span></div>
                </div>
            </div>
        </div>
        <div class="metric-card">
            <div class="metric-icon">🏆</div>
            <div class="metric-content">
                <div class="metric-label">Risk-Adjusted</div>
                <div class="metric-items">
                    <div class="item"><span>Sharpe Ratio</span><span>{m.sharpe_ratio:.2f}</span></div>
                    <div class="item"><span>Sortino Ratio</span><span>{m.sortino_ratio:.2f}</span></div>
                    <div class="item"><span>Calmar Ratio</span><span>{m.calmar_ratio:.2f}</span></div>
                    <div class="item"><span>Recovery Factor</span><span>{m.recovery_factor:.2f}</span></div>
                </div>
            </div>
        </div>
        <div class="metric-card">
            <div class="metric-icon">💰</div>
            <div class="metric-content">
                <div class="metric-label">Costs</div>
                <div class="metric-items">
                    <div class="item"><span>Commission</span><span>${m.total_commission:.2f}</span></div>
                    <div class="item"><span>Slippage</span><span>${m.total_slippage:.2f}</span></div>
                    <div class="item"><span>Total Costs</span><span>${m.total_commission + m.total_slippage:.2f}</span></div>
                </div>
            </div>
        </div>
        <div class="metric-card">
            <div class="metric-icon">⚙️</div>
            <div class="metric-content">
                <div class="metric-label">Settings</div>
                <div class="metric-items">
                    <div class="item"><span>Initial Capital</span><span>${c.initial_capital:,.0f}</span></div>
                    <div class="item"><span>Leverage</span><span>{c.leverage}:1</span></div>
                    <div class="item"><span>Risk/Trade</span><span>{c.risk_per_trade*100:.1f}%</span></div>
                    <div class="item"><span>Slippage Model</span><span>{c.slippage_model}</span></div>
                </div>
            </div>
        </div>
        '''
    
    def _build_html(self, config, metrics, summary_html, trade_log_html,
                    equity_data, drawdown_data, monthly_data, distribution_data,
                    cumulative_pnl, trade_scatter, total_trades) -> str:
        """Build complete HTML document"""
        
        net_class = 'win' if metrics.net_profit >= 0 else 'loss'
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Backtest Report - {config.symbol}</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        :root {{
            --bg-primary: #0a0e17;
            --bg-secondary: #131722;
            --bg-card: #1e222d;
            --bg-hover: #2a2e39;
            --text-primary: #d1d4dc;
            --text-secondary: #787b86;
            --accent: #2962ff;
            --win: #26a69a;
            --loss: #ef5350;
            --border: #2a2e39;
        }}
        
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Trebuchet MS', Roboto, Ubuntu, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            line-height: 1.5;
        }}
        
        .container {{
            max-width: 1800px;
            margin: 0 auto;
            padding: 24px;
        }}
        
        /* Header */
        .header {{
            background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-card) 100%);
            border-radius: 16px;
            padding: 32px;
            margin-bottom: 24px;
            border: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 24px;
        }}
        
        .header-left h1 {{
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(135deg, #2962ff, #6b8cff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 8px;
        }}
        
        .header-meta {{
            display: flex;
            gap: 24px;
            color: var(--text-secondary);
            flex-wrap: wrap;
        }}
        
        .header-meta span {{
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        
        /* Stats Row */
        .stats-row {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}
        
        .stat-box {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            transition: all 0.3s ease;
        }}
        
        .stat-box:hover {{
            transform: translateY(-4px);
            border-color: var(--accent);
            box-shadow: 0 8px 32px rgba(41, 98, 255, 0.15);
        }}
        
        .stat-value {{
            font-size: 1.8rem;
            font-weight: 700;
            margin-bottom: 4px;
        }}
        
        .stat-label {{
            font-size: 0.85rem;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .win {{ color: var(--win); }}
        .loss {{ color: var(--loss); }}
        
        /* Charts */
        .chart-section {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 24px;
        }}
        
        .chart-title {{
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 24px;
            margin-bottom: 24px;
        }}
        
        @media (max-width: 1200px) {{
            .charts-grid {{ grid-template-columns: 1fr; }}
        }}
        
        /* Metrics Grid */
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}
        
        .metric-card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            display: flex;
            gap: 16px;
        }}
        
        .metric-icon {{
            font-size: 2rem;
            opacity: 0.8;
        }}
        
        .metric-label {{
            font-weight: 600;
            margin-bottom: 12px;
            color: var(--text-primary);
        }}
        
        .metric-items .item {{
            display: flex;
            justify-content: space-between;
            padding: 6px 0;
            font-size: 0.9rem;
            border-bottom: 1px solid var(--border);
        }}
        
        .metric-items .item:last-child {{ border-bottom: none; }}
        .metric-items .item span:first-child {{ color: var(--text-secondary); }}
        
        /* Trade Log */
        .trade-log {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 24px;
            overflow-x: auto;
        }}
        
        .trade-log h2 {{
            font-size: 1.2rem;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem;
        }}
        
        th, td {{
            padding: 12px 8px;
            text-align: left;
            border-bottom: 1px solid var(--border);
            white-space: nowrap;
        }}
        
        th {{
            background: var(--bg-secondary);
            font-weight: 600;
            color: var(--text-secondary);
            text-transform: uppercase;
            font-size: 0.75rem;
            letter-spacing: 0.5px;
            position: sticky;
            top: 0;
        }}
        
        tr:hover {{ background: var(--bg-hover); }}
        
        tr.win td.pnl {{ color: var(--win); font-weight: 600; }}
        tr.loss td.pnl {{ color: var(--loss); font-weight: 600; }}
        
        .badge {{
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
        }}
        
        .badge.buy {{ background: rgba(38, 166, 154, 0.2); color: var(--win); }}
        .badge.sell {{ background: rgba(239, 83, 80, 0.2); color: var(--loss); }}
        
        .exit-badge {{
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.75rem;
            background: var(--bg-secondary);
            color: var(--text-secondary);
        }}
        
        /* Footer */
        footer {{
            text-align: center;
            padding: 24px;
            color: var(--text-secondary);
            font-size: 0.85rem;
        }}
        
        /* Scrollbar */
        ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
        ::-webkit-scrollbar-track {{ background: var(--bg-secondary); }}
        ::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 4px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: var(--text-secondary); }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-left">
                <h1>📈 Backtest Report</h1>
                <div class="header-meta">
                    <span>📊 {config.symbol}</span>
                    <span>⏱️ {config.timeframe}</span>
                    <span>📅 {config.start_date} to {config.end_date}</span>
                    <span>💰 ${config.initial_capital:,.0f}</span>
                    <span>⚡ {config.leverage}:1 Leverage</span>
                </div>
            </div>
        </div>
        
        <div class="stats-row">
            <div class="stat-box">
                <div class="stat-value">{total_trades}</div>
                <div class="stat-label">Total Trades</div>
            </div>
            <div class="stat-box">
                <div class="stat-value win">{metrics.win_rate*100:.1f}%</div>
                <div class="stat-label">Win Rate</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{metrics.profit_factor:.2f}</div>
                <div class="stat-label">Profit Factor</div>
            </div>
            <div class="stat-box">
                <div class="stat-value {net_class}">${metrics.net_profit:,.2f}</div>
                <div class="stat-label">Net Profit</div>
            </div>
            <div class="stat-box">
                <div class="stat-value loss">{metrics.max_drawdown_pct*100:.2f}%</div>
                <div class="stat-label">Max Drawdown</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{metrics.sharpe_ratio:.2f}</div>
                <div class="stat-label">Sharpe Ratio</div>
            </div>
        </div>
        
        <div class="chart-section">
            <div class="chart-title">📈 Equity Curve</div>
            <div id="equityChart"></div>
        </div>
        
        <div class="charts-grid">
            <div class="chart-section">
                <div class="chart-title">📉 Drawdown</div>
                <div id="drawdownChart"></div>
            </div>
            <div class="chart-section">
                <div class="chart-title">📊 Cumulative PnL by Trade</div>
                <div id="cumPnlChart"></div>
            </div>
        </div>
        
        <div class="charts-grid">
            <div class="chart-section">
                <div class="chart-title">📆 Monthly Performance</div>
                <div id="monthlyChart"></div>
            </div>
            <div class="chart-section">
                <div class="chart-title">📊 PnL Distribution</div>
                <div id="distributionChart"></div>
            </div>
        </div>
        
        <div class="chart-section">
            <div class="chart-title">🎯 Trade Scatter (PnL vs R-Multiple)</div>
            <div id="scatterChart"></div>
        </div>
        
        <div class="metrics-grid">
            {summary_html}
        </div>
        
        <div class="trade-log">
            <h2>📋 Trade Log ({total_trades} trades)</h2>
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Type</th>
                        <th>Entry Time</th>
                        <th>Entry Price</th>
                        <th>Exit Time</th>
                        <th>Exit Price</th>
                        <th>Size</th>
                        <th>SL</th>
                        <th>TP</th>
                        <th>PnL</th>
                        <th>Pips</th>
                        <th>R-Multiple</th>
                        <th>MFE</th>
                        <th>MAE</th>
                        <th>Duration</th>
                        <th>Exit</th>
                    </tr>
                </thead>
                <tbody>
                    {trade_log_html}
                </tbody>
            </table>
        </div>
        
        <footer>
            Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Industry-Grade Backtester V2
        </footer>
    </div>
    
    <script>
        const layout = {{
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            font: {{ color: '#d1d4dc', family: '-apple-system, BlinkMacSystemFont, sans-serif' }},
            margin: {{ t: 10, r: 20, b: 40, l: 60 }},
            xaxis: {{ 
                gridcolor: '#2a2e39', 
                zerolinecolor: '#2a2e39',
                tickfont: {{ size: 10 }}
            }},
            yaxis: {{ 
                gridcolor: '#2a2e39', 
                zerolinecolor: '#2a2e39',
                tickfont: {{ size: 10 }}
            }},
            hoverlabel: {{ bgcolor: '#1e222d', font: {{ color: '#d1d4dc' }} }}
        }};
        
        const config = {{ 
            responsive: true, 
            displayModeBar: true,
            modeBarButtonsToRemove: ['lasso2d', 'select2d'],
            displaylogo: false
        }};
        
        // Equity Curve
        const equityData = {json.dumps(equity_data)};
        Plotly.newPlot('equityChart', [{{
            x: equityData.times,
            y: equityData.values,
            type: 'scatter',
            mode: 'lines',
            fill: 'tozeroy',
            fillcolor: 'rgba(41, 98, 255, 0.1)',
            line: {{ color: '#2962ff', width: 2 }},
            hovertemplate: '%{{x}}<br>Equity: $%{{y:,.2f}}<extra></extra>'
        }}], {{...layout, height: 300}}, config);
        
        // Drawdown
        const ddData = {json.dumps(drawdown_data)};
        Plotly.newPlot('drawdownChart', [{{
            x: ddData.times,
            y: ddData.values,
            type: 'scatter',
            mode: 'lines',
            fill: 'tozeroy',
            fillcolor: 'rgba(239, 83, 80, 0.2)',
            line: {{ color: '#ef5350', width: 2 }},
            hovertemplate: '%{{x}}<br>Drawdown: %{{y:.2f}}%<extra></extra>'
        }}], {{...layout, height: 250, yaxis: {{...layout.yaxis, autorange: 'reversed'}}}}, config);
        
        // Cumulative PnL
        const cumData = {json.dumps(cumulative_pnl)};
        Plotly.newPlot('cumPnlChart', [{{
            x: cumData.indices,
            y: cumData.pnls,
            type: 'scatter',
            mode: 'lines+markers',
            marker: {{ color: cumData.colors, size: 6 }},
            line: {{ color: '#8b5cf6', width: 2 }},
            hovertemplate: 'Trade #%{{x}}<br>Cumulative: $%{{y:,.2f}}<extra></extra>'
        }}], {{...layout, height: 250, xaxis: {{...layout.xaxis, title: 'Trade #'}}}}, config);
        
        // Monthly
        const monthlyData = {json.dumps(monthly_data)};
        Plotly.newPlot('monthlyChart', [{{
            x: monthlyData.months,
            y: monthlyData.pnl,
            type: 'bar',
            marker: {{ color: monthlyData.colors }},
            hovertemplate: '%{{x}}<br>PnL: $%{{y:,.2f}}<extra></extra>'
        }}], {{...layout, height: 250}}, config);
        
        // Distribution
        const distData = {json.dumps(distribution_data)};
        Plotly.newPlot('distributionChart', [{{
            x: distData.bins,
            y: distData.counts,
            type: 'bar',
            marker: {{ color: '#8b5cf6' }},
            hovertemplate: '%{{x}}<br>Count: %{{y}}<extra></extra>'
        }}], {{...layout, height: 250}}, config);
        
        // Scatter
        const scatterData = {json.dumps(trade_scatter)};
        Plotly.newPlot('scatterChart', [
            {{
                x: scatterData.wins.r,
                y: scatterData.wins.pnl,
                type: 'scatter',
                mode: 'markers',
                name: 'Wins',
                marker: {{ color: '#26a69a', size: 10, opacity: 0.7 }},
                text: scatterData.wins.text,
                hovertemplate: '%{{text}}<extra></extra>'
            }},
            {{
                x: scatterData.losses.r,
                y: scatterData.losses.pnl,
                type: 'scatter',
                mode: 'markers',
                name: 'Losses',
                marker: {{ color: '#ef5350', size: 10, opacity: 0.7 }},
                text: scatterData.losses.text,
                hovertemplate: '%{{text}}<extra></extra>'
            }}
        ], {{
            ...layout, 
            height: 300,
            xaxis: {{...layout.xaxis, title: 'R-Multiple'}},
            yaxis: {{...layout.yaxis, title: 'PnL ($)'}},
            showlegend: true,
            legend: {{ x: 0, y: 1, bgcolor: 'rgba(0,0,0,0)' }}
        }}, config);
    </script>
</body>
</html>'''
