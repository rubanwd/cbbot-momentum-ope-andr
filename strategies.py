# strategy.py

import pandas as pd
from indicators import Indicators

class Strategies:
    def __init__(self):
        self.indicators = Indicators()

    def prepare_dataframe(self, historical_data):
        df = pd.DataFrame(historical_data)
        df.columns = ["timestamp", "open", "high", "low", "close", "volume", "turnover"]
        df[['open', 'high', 'low', 'close', 'volume', 'turnover']] = df[['open', 'high', 'low', 'close', 'volume', 'turnover']].astype(float)
        df.sort_values('timestamp', inplace=True)
        return df

    def momentum_strategy(self, df):
        # Calculate indicators needed for the strategy
        df['MACD'], df['MACD_Signal'] = self.indicators.calculate_macd(df)
        df['Stoch_RSI'] = self.indicators.calculate_stochastic_rsi(df)

        # Get the last two values to detect crossovers
        macd = df['MACD']
        macd_signal = df['MACD_Signal']
        stoch_rsi = df['Stoch_RSI']

        # MACD crossover detection
        macd_cross_above = (macd.iloc[-2] < macd_signal.iloc[-2]) and (macd.iloc[-1] > macd_signal.iloc[-1])
        macd_cross_below = (macd.iloc[-2] > macd_signal.iloc[-2]) and (macd.iloc[-1] < macd_signal.iloc[-1])

        # Stochastic RSI thresholds
        stoch_rsi_overbought = stoch_rsi.iloc[-1] > 0.8
        stoch_rsi_oversold = stoch_rsi.iloc[-1] < 0.2

        # Combine the indicators for signals
        # if macd_cross_above and stoch_rsi_oversold:
        #     return 'long'
        # elif macd_cross_below and stoch_rsi_overbought:
        #     return 'short'
        # else:
        #     return None

        return 'long'


