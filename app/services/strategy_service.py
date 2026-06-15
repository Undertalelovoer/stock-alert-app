from app.services.indicator_service import add_indicators


def judge_buy_signal(df_1m, df_5m, df_1h, df_1d):
    reasons = []

    df_1m = add_indicators(df_1m)
    df_5m = add_indicators(df_5m)
    df_1h = add_indicators(df_1h)
    df_1d = add_indicators(df_1d)

    if df_1m.empty or df_5m.empty or df_1h.empty or df_1d.empty:
        print("strategy_service: 指標計算後のデータが空です")
        return False, reasons

    if len(df_1m) < 30 or len(df_5m) < 30 or len(df_1h) < 30 or len(df_1d) < 30:
        print("strategy_service: データ件数が不足しています")
        return False, reasons

    latest_1m = df_1m.iloc[-1]
    prev_1m = df_1m.iloc[-2]
    latest_5m = df_5m.iloc[-1]
    latest_1h = df_1h.iloc[-1]
    latest_1d = df_1d.iloc[-1]

    # 条件A：ボリンジャーバンド -2σ + RCI
    bb_touch = latest_1m["low"] <= latest_1m["bb_lower_2"]
    rci9_oversold = latest_1m["rci9"] <= -80
    rci5_cross_up = prev_1m["rci5"] <= prev_1m["rci9"] and latest_1m["rci5"] > latest_1m["rci9"]
    rci5_slope_up = latest_1m["rci5"] - prev_1m["rci5"] >= 10

    if bb_touch and rci9_oversold and (rci5_cross_up or rci5_slope_up):
        reasons.append("ボリンジャーバンド-2σタッチ + RCI(9)-80以下 + RCI(5)反発")

    # 条件B：MACD回復 + VWAP上抜け
    macd_recovery = (
        prev_1m["macd_hist"] < 0
        and latest_1m["macd_hist"] > 0
        and latest_1m["macd"] < 0
    )

    vwap_break = (
        prev_1m["close"] <= prev_1m["vwap"]
        and latest_1m["close"] > latest_1m["vwap"]
    )

    if macd_recovery and vwap_break:
        reasons.append("MACDがマイナス圏から回復 + VWAP上抜け")

    # 条件C：最高値更新 + 出来高2倍
    recent_high = df_1m["high"].iloc[-21:-1].max()
    high_break = latest_1m["high"] > recent_high
    volume_double = latest_1m["volume"] >= latest_1m["volume_avg20"] * 2

    if high_break and volume_double:
        reasons.append("最高値更新 + 出来高2倍以上")

    # 条件D：日足・1時間足が上向き + 1分足RCI反発
    daily_trend = latest_1d["ema5"] > latest_1d["ema20"] and latest_1d["macd"] > 0
    hourly_trend = latest_1h["ema5"] > latest_1h["ema20"] and latest_1h["macd"] > 0

    rci_rebound = (
        prev_1m["rci9"] <= -80
        and latest_1m["rci9"] > prev_1m["rci9"]
    )

    if daily_trend and hourly_trend and rci_rebound:
        reasons.append("日足・1時間足が上向き + 1分足RCI(9)が-80以下から反発")

    # 条件E：5分足RSI + 1分足RCI
    if latest_5m["rsi5"] <= 25 and latest_1m["rci9"] <= -95:
        reasons.append("5分足RSIが25以下 + 1分足RCI(9)が-95以下")

    return len(reasons) > 0, reasons