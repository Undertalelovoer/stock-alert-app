from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import COMPANIES_FILE, WATCHLIST_FILE
from app.services.json_service import load_json, save_json
from app.services.line_service import save_line_user, send_line_message
from app.scheduler import start_scheduler, check_all_stocks

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.on_event("startup")
def on_startup():
    start_scheduler()


@app.get("/")
def index():
    return FileResponse("app/static/index.html")


@app.get("/companies")
def get_companies():
    return load_json(COMPANIES_FILE, [])


@app.get("/watchlist")
def get_watchlist():
    return load_json(WATCHLIST_FILE, [])


@app.post("/watchlist")
async def add_watchlist(request: Request):
    body = await request.json()

    watchlist = load_json(WATCHLIST_FILE, [])

    for item in watchlist:
        if item["symbol"] == body["symbol"]:
            return {"message": "すでに登録されています"}

    new_item = {
        "name": body["name"],
        "symbol": body["symbol"],
        "market": body["market"],
        "enabled": True,
    }

    watchlist.append(new_item)
    save_json(WATCHLIST_FILE, watchlist)

    return {"message": "監視リストに追加しました"}


@app.post("/check")
def manual_check():
    try:
        check_all_stocks()
        return {"message": "手動チェックを実行しました"}
    except Exception as e:
        print("CHECK ERROR:", repr(e))
        return {
            "message": "チェック中にエラーが発生しました",
            "error": str(e)
        }


@app.post("/line/webhook")
async def line_webhook(request: Request):
    body = await request.json()

    events = body.get("events", [])

    for event in events:
        source = event.get("source", {})
        user_id = source.get("userId")

        if user_id:
            save_line_user(user_id)

        message = event.get("message", {})
        text = message.get("text", "")

        if text in ["登録", "通知登録", "開始"]:
            send_line_message("株価通知の送信先として登録しました。")

    return {"status": "ok"}

@app.post("/line/test")
def line_test():
    send_line_message("LINE通知テストです。")
    return {"message": "LINE通知テストを送信しました"}
<<<<<<< HEAD

@app.post("/line/test")
def line_test():
    send_line_message("LINE通知テストです。")
    return {"message": "LINE通知テストを送信しました"}
=======
>>>>>>> 471b64ae5fce4f35ccd061717209906550ce26f7
