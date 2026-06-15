import yfinance as yf
import pandas as pd


def get_price_data(symbol: str, interval: str):
    period_map = {
        "1m": "1d",
        "5m": "5d",
        "1h": "1mo",
        "1d": "6mo",
    }

    period = period_map.get(interval, "1d")

    df = yf.download(
        tickers=symbol,
        period=period,
        interval=interval,
        progress=False,
        auto_adjust=False,
        group_by="column",
    )

    if df.empty:
        print(f"データ取得失敗: {symbol} {interval}")
        return pd.DataFrame()

    print(f"取得直後の列名 {symbol} {interval}:", df.columns)

    # yfinanceでMultiIndexになる場合の対策
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [str(col[0]).lower().replace(" ", "_") for col in df.columns]
    else:
        df.columns = [str(col).lower().replace(" ", "_") for col in df.columns]

    df = df.reset_index()

    df.columns = [str(col).lower().replace(" ", "_") for col in df.columns]

    print(f"整形後の列名 {symbol} {interval}:", df.columns.tolist())

    required_columns = ["open", "high", "low", "close", "volume"]

    for col in required_columns:
        if col not in df.columns:
            print(f"必要な列がありません: {col}")
            print("現在の列名:", df.columns.tolist())
            return pd.DataFrame()

    return df