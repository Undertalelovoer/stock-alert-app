from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler

from app.config import WATCHLIST_FILE, LAST_NOTIFIED_FILE
from app.services.json_service import load_json, save_json
from app.services.stock_service import get_price_data
from app.services.strategy_service import judge_buy_signal
from app.services.line_service import send_line_message


def already_notified(symbol: str, minutes: int = 30) -> bool:
    data = load_json(LAST_NOTIFIED_FILE, {})

    if symbol not in data:
        return False

    last_time = datetime.fromisoformat(data[symbol]["last_notified_at"])
    return datetime.now() - last_time < timedelta(minutes=minutes)


def save_notified(symbol: str, reasons):
    data = load_json(LAST_NOTIFIED_FILE, {})

    data[symbol] = {
        "last_notified_at": datetime.now().isoformat(),
        "reasons": reasons,
    }

    save_json(LAST_NOTIFIED_FILE, data)


def check_all_stocks():
    watchlist = load_json(WATCHLIST_FILE, [])

    for item in watchlist:
        try:
            if not item.get("enabled", True):
                continue

            symbol = item["symbol"]
            company_name = item["name"]

            if already_notified(symbol):
                continue

            print(f"チェック中: {company_name} {symbol}")

            df_1m = get_price_data(symbol, "1m")
            df_5m = get_price_data(symbol, "5m")
            df_1h = get_price_data(symbol, "1h")
            df_1d = get_price_data(symbol, "1d")

            is_buy, reasons = judge_buy_signal(df_1m, df_5m, df_1h, df_1d)

            if is_buy:
                latest_price = df_1m.iloc[-1]["close"]

                message = (
                    "【株価BUY通知】\n"
                    f"会社名: {company_name}\n"
                    f"銘柄: {symbol}\n"
                    f"現在値: {latest_price}\n\n"
                    "条件:\n"
                    + "\n".join([f"・{r}" for r in reasons])
                )

                send_line_message(message)
                save_notified(symbol, reasons)

        except Exception as e:
            print(f"check_all_stocks error: {item}")
            print("ERROR:", repr(e))
            continue


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_all_stocks, "interval", minutes=1)
    scheduler.start()