#  helpers.py

class Helpers:
    @staticmethod
    def calculate_and_print_indicators(df, indicators):
        # Calculate indicators
        df['EMA_9'] = indicators.calculate_ema(df, 9)
        df['RSI'] = indicators.calculate_rsi(df, 14)
        df['MACD'], df['MACD_Signal'] = indicators.calculate_macd(df)
        df['Stoch_RSI'] = indicators.calculate_stochastic_rsi(df)

        # Get the latest indicator values
        rsi = df['RSI'].iloc[-1]
        macd = df['MACD'].iloc[-1]
        macd_signal = df['MACD_Signal'].iloc[-1]
        stoch_rsi = df['Stoch_RSI'].iloc[-1]
        current_price = df['close'].iloc[-1]

        # Print the indicator values
        print(f"RSI: {rsi:.2f}")
        print(f"MACD: {macd:.4f}")
        print(f"MACD Signal: {macd_signal:.4f}")
        print(f"Stochastic RSI: {stoch_rsi:.4f}")
        print(f"Current Price: {current_price:.2f}")

        # Return the calculated indicators and price
        return rsi, macd, macd_signal, stoch_rsi, current_price
