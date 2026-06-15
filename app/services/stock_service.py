import yfinance as yf


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
        return df

    df = df.reset_index()

    df.columns = [str(c).lower().replace(" ", "_") for c in df.columns]

    rename_map = {
        "open": "open",
        "high": "high",
        "low": "low",
        "close": "close",
        "volume": "volume",
    }

    df = df.rename(columns=rename_map)

    return df