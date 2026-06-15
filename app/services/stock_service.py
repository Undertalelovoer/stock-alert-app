import yfinance as yf
import pandas as pd


def normalize_column_name(col):
    """
    yfinanceの列名が
    Close
    ('Close', 'AAPL')
    ('AAPL', 'Close')
    のどれで来ても close にそろえる
    """
    target_names = {
        "open": "open",
        "high": "high",
        "low": "low",
        "close": "close",
        "adj close": "adj_close",
        "adj_close": "adj_close",
        "volume": "volume",
    }

    if isinstance(col, tuple):
        parts = [str(p).lower().replace("_", " ").strip() for p in col]

        for part in parts:
            if part in target_names:
                return target_names[part]

        return "_".join(parts).replace(" ", "_")

    name = str(col).lower().replace("_", " ").strip()

    if name in target_names:
        return target_names[name]

    return name.replace(" ", "_")


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

    print(f"取得直後の列名 {symbol} {interval}:", df.columns)

    df = df.reset_index()

    df.columns = [normalize_column_name(col) for col in df.columns]

    # 重複列がある場合は最初の列だけ使う
    df = df.loc[:, ~df.columns.duplicated()]

    # adj_closeしかない場合の保険
    if "close" not in df.columns and "adj_close" in df.columns:
        df["close"] = df["adj_close"]

    print(f"整形後の列名 {symbol} {interval}:", df.columns.tolist())

    required_columns = ["open", "high", "low", "close", "volume"]

    missing = [col for col in required_columns if col not in df.columns]

    if missing:
        print(f"必要な列がありません: {missing}")
        print("現在の列名:", df.columns.tolist())
        return pd.DataFrame()

    for col in required_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["close"])

    return df