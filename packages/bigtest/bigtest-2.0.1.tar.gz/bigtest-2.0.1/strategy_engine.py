import pandas as pd
import pythonpine as pp

class StrategyEngine:
    def __init__(self):
        pass

    def calculate_indicators(self, df):
        """
        Apply technical indicators using pythonpine.
        This method should be customized or subclassed for specific strategies.
        For now, we'll implement a generic interface that takes a strategy function.
        """
        # Ensure we have list inputs as pythonpine expects lists
        closes = df['close'].tolist()
        highs = df['high'].tolist()
        lows = df['low'].tolist()
        opens = df['open'].tolist()
        volumes = df['volume'].tolist()
        
        # Example: Calculate generic indicators that might be useful
        # In a real scenario, the user would define what they want.
        # We will attach them to the DataFrame for easy access.
        
        # We can't pre-calculate everything. 
        # Instead, we'll let the specific strategy logic call pp functions.
        pass

    def run_strategy(self, df, strategy_func):
        """
        Executes a user-defined strategy function on the dataframe.
        The strategy function should accept the dataframe and return a list of signals.
        
        Signal format:
        [
            {'index': 10, 'time': '...', 'type': 'BUY', 'sl': 100.0, 'tp': 110.0, 'comment': '...'},
            ...
        ]
        """
        # Convert columns to lists for pythonpine
        # We pass the entire dataframe or specific lists to the strategy function
        return strategy_func(df)
