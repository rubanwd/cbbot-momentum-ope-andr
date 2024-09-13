# indicators.py

class Indicators:
    @staticmethod
    def calculate_ema(df, span):
        return df['close'].ewm(span=span, adjust=False).mean()

    @staticmethod
    def calculate_rsi(df, period=14):
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    @staticmethod
    def calculate_macd(df):
        short_ema = df['close'].ewm(span=12, adjust=False).mean()
        long_ema = df['close'].ewm(span=26, adjust=False).mean()
        macd = short_ema - long_ema
        macd_signal = macd.ewm(span=9, adjust=False).mean()
        return macd, macd_signal

    @staticmethod
    def calculate_stochastic_rsi(df, period=14):
        rsi = Indicators.calculate_rsi(df, period)
        min_rsi = rsi.rolling(window=period).min()
        max_rsi = rsi.rolling(window=period).max()
        stoch_rsi = (rsi - min_rsi) / (max_rsi - min_rsi)
        return stoch_rsi
