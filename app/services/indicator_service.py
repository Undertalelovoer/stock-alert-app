import pandas as pd


def calc_rci(series: pd.Series, period: int) -> pd.Series:
    def rci_window(values):
        n = len(values)
        time_rank = pd.Series(range(1, n + 1))
        price_rank = pd.Series(values).rank(method="average")
        d = time_rank - price_rank
        return (1 - (6 * (d ** 2).sum()) / (n * (n ** 2 - 1))) * 100

    return series.rolling(period).apply(rci_window, raw=False)


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()

    required_columns = ["open", "high", "low", "close", "volume"]
    missing = [col for col in required_columns if col not in df.columns]

    if missing:
        print("indicator_serviceで必要な列がありません:", missing)
        print("現在の列名:", df.columns.tolist())
        return pd.DataFrame()

    close = df["close"]

    # 以下、元の処理を続ける
    df["ema5"] = close.ewm(span=5, adjust=False).mean()
    df["ema20"] = close.ewm(span=20, adjust=False).mean()

    df["bb_mid"] = close.rolling(20).mean()
    df["bb_std"] = close.rolling(20).std()
    df["bb_lower_2"] = df["bb_mid"] - 2 * df["bb_std"]

    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    df["macd"] = ema12 - ema26
    df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()
    df["macd_hist"] = df["macd"] - df["macd_signal"]

    diff = close.diff()
    gain = diff.clip(lower=0)
    loss = -diff.clip(upper=0)

    avg_gain = gain.rolling(5).mean()
    avg_loss = loss.rolling(5).mean()
    rs = avg_gain / avg_loss

    df["rsi5"] = 100 - (100 / (1 + rs))

    df["rci5"] = calc_rci(close, 5)
    df["rci9"] = calc_rci(close, 9)

    typical_price = (df["high"] + df["low"] + df["close"]) / 3
    df["vwap"] = (typical_price * df["volume"]).cumsum() / df["volume"].cumsum()

    df["volume_avg20"] = df["volume"].rolling(20).mean()

    return df