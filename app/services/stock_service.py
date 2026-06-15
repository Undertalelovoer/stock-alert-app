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
    )

    if df.empty:
        print(f"データ取得失敗: {symbol} {interval}")
        return pd.DataFrame()

    # yfinanceで列がMultiIndexになる場合の対策
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0].lower() for col in df.columns]
    else:
        df.columns = [str(col).lower() for col in df.columns]

    df = df.reset_index()

    # 列名を小文字に統一
    df.columns = [str(col).lower().replace(" ", "_") for col in df.columns]

    # 必要な列があるか確認
    required_columns = ["open", "high", "low", "close", "volume"]

    for col in required_columns:
        if col not in df.columns:
            print("現在の列名:", df.columns.tolist())
            print(f"必要な列がありません: {col}")
            return pd.DataFrame()

    return df