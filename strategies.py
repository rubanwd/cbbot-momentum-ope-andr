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
        # Calculate MACD, Stochastic RSI, and RSI as additional confirmation
        df['MACD'], df['MACD_Signal'] = self.indicators.calculate_macd(df)
        df['Stoch_RSI'] = self.indicators.calculate_stochastic_rsi(df)
        df['RSI'] = self.indicators.calculate_rsi(df, period=14)

        # Get the last two values to detect crossovers
        macd = df['MACD']
        macd_signal = df['MACD_Signal']
        stoch_rsi = df['Stoch_RSI']
        rsi = df['RSI']

        # MACD crossover detection
        macd_cross_above = (macd.iloc[-2] < macd_signal.iloc[-2]) and (macd.iloc[-1] > macd_signal.iloc[-1])
        macd_cross_below = (macd.iloc[-2] > macd_signal.iloc[-2]) and (macd.iloc[-1] < macd_signal.iloc[-1])

        # Stochastic RSI thresholds - slightly relaxed to capture more signals
        stoch_rsi_overbought = stoch_rsi.iloc[-1] > 0.7  # was 0.8
        stoch_rsi_oversold = stoch_rsi.iloc[-1] < 0.3  # was 0.2

        # RSI confirmation levels
        rsi_bullish = rsi.iloc[-1] > 50
        rsi_bearish = rsi.iloc[-1] < 50

        # Combine the indicators for stronger signals and apply confirmation with RSI
        if macd_cross_above and stoch_rsi_oversold and rsi_bullish:
            return 'long'
        elif macd_cross_below and stoch_rsi_overbought and rsi_bearish:
            return 'short'
        else:
            return None

